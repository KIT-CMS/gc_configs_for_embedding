import os,stat

class finale_state():
	def __init__(self, finalstate, identifier="", generator_frag="", runs = ['Run2016B','Run2016C','Run2016D','Run2016E','Run2016F','Run2016G','Run2016H'], add_dbs=None, inputfolder = "Run2016_CMSSW_8_0_26",generator_frag_map=None, reselect=False):
		if finalstate == 'ElEmb':
			self.finalstate = 'ElEl'
			self.particle_to_embed = 'ElEmbedding'
		elif finalstate == 'MuEmb': 
			self.finalstate = 'MuMu'
			self.particle_to_embed = 'MuEmbedding'
		else:
			self.finalstate = finalstate
			self.particle_to_embed = 'TauEmbedding'
		self.identifier=identifier
		self.name = self.finalstate+"_"+identifier
		self.gc_cfgs = []
		self.generator_frag_map = generator_frag_map
		self.inputfolder = inputfolder
		self.cmsRun_order =  ['preselection.py','selection.py','lheprodandcleaning.py','generator.py','merging.py'] ## will be overwitten by copy_pyconfigs (checks is exsist in input folder)
		self.reselect = reselect

		if not os.path.exists(self.name):
			os.mkdir(self.name)
		if self.generator_frag_map is None:
			self.generator_frag_map=self.make_generator_frag_map(this_finalstate=self.finalstate)
			
		self.copy_pyconfigs(generator_frag=self.generator_frag_map[self.finalstate],reselect=self.reselect)
		self.copy_gcconfigs(runs=runs,add_dbs=add_dbs)
		self.write_while()
	def copy_pyconfigs(self, generator_frag="", reselect=False):
		is_first = True ## can be late used to init the first config with customize_for_gc and the later with the dummy stings 
		self.cmsRun_order = []
		files_to_copy = ['preselection.py'] if self.finalstate=="Preselection" else ['selection.py','lheprodandcleaning.py','generator.py','merging.py']
		for file_to_copy in files_to_copy: # ['preselection.py','selection.py','lheprodandcleaning.py','generator.py','merging.py']:
			add_fragment_to_end=[]
			if is_first:
				with open('customise_for_gc.py','r') as function_to_add:
					add_fragment_to_end.append(function_to_add.read())
				add_fragment_to_end.append('process = customise_for_gc(process)')
			else:
				add_fragment_to_end.append('####@FILE_NAMES@, @SKIP_EVENTS@, @MAX_EVENTS@')
			if file_to_copy in ['lheprodandcleaning.py','generator.py']:
				add_fragment_to_end.append('from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper')
				add_fragment_to_end.append('randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)')
				add_fragment_to_end.append('randSvc.populate()')
				add_fragment_to_end.append('print("Generator random seed: %s" % process.RandomNumberGeneratorService.generator.initialSeed)')

				if file_to_copy == 'generator.py':
					add_fragment_to_end.append(generator_frag)
			if file_to_copy == 'lheprodandcleaning.py':
				if self.particle_to_embed == "MuEmbedding":
					add_fragment_to_end.append('process.externalLHEProducer.particleToEmbed = cms.int32(13)')
				if self.particle_to_embed == "ElEmbedding":
					add_fragment_to_end.append('process.externalLHEProducer.particleToEmbed = cms.int32(11)')
			if file_to_copy == 'merging.py' and not "2016" in self.identifier:
				if "Run201" in self.inputfolder:
					add_fragment_to_end.append('from TauAnalysis.MCEmbeddingTools.customisers import customiseKeepPrunedGenParticles')
					if reselect:
						add_fragment_to_end.append('process = customiseKeepPrunedGenParticles(process,True)')
					else:
						add_fragment_to_end.append('process = customiseKeepPrunedGenParticles(process)')
			if self.copy_file(file_to_copy, add_fragment_to_end=add_fragment_to_end, skip_if_not_there=True):
				is_first = False
				self.cmsRun_order.append(file_to_copy)
	def copy_gcconfigs(self, runs=[], add_dbs=None):
		dbs_folder="dbs"
		for add_run in runs:
			if not add_dbs:
				if os.path.exists(dbs_folder+"/"+add_run+'.dbs'):
					self.copy_file(add_run+'.dbs', copy_from_folder = dbs_folder)
					"Copied {}".format(dbs_folder+add_run+'.dbs')
				else:
					print '{}.dbs could not be found in folder {}. Please run preselection'.format(add_run,dbs_folder)
				if not os.path.exists(self.name+'/'+add_run+'.conf'):
					self.write_cfg(add_run=add_run)
			else:
				self.write_cfg(add_run=add_run, add_dbs=add_dbs)
		if len(runs)==0 and add_dbs:
			self.write_cfg(add_dbs=add_dbs)
		cmsRun_order_str = 'config file = '
		for cmsRun_cfg in self.cmsRun_order:
			cmsRun_order_str += cmsRun_cfg+'\n\t\t'
		rp_base_cfg = {}
		rp_base_cfg['__CMSRUN_ORDER__'] = cmsRun_order_str
		if self.finalstate=="Preselection":
			se_path_str = 'se path = srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only/store/user/sbrommer/gc_storage'
		else:
			se_path_str = 'se path = srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only/store/user/' + os.environ["USER"] + '/gc_storage/embedding_16_legacy'
		rp_base_cfg['__SE_PATH__']=se_path_str
		se_output_pattern_str= 'se output pattern = '+self.finalstate+'_'+self.identifier+'/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@'
		rp_base_cfg['__SE_OUTPUT_PATTERN__']=se_output_pattern_str
		rp_base_cfg['__partition_lfn_modifier__'] = 'partition lfn modifier = <xrootd:nrg>'
		rp_base_cfg['__SE_OUTPUT_FILE__'] = 'se output files = merged.root'
		if self.finalstate=="Preselection":
			self.copy_file('grid_control_fullembedding_data_base_preselection.conf', copy_from_folder='./' ,replace_dict=rp_base_cfg)
		else:
			self.copy_file('grid_control_fullembedding_data_base_freiburg.conf', copy_from_folder='./' ,replace_dict=rp_base_cfg)
			self.copy_file('grid_control_fullembedding_data_base_naf.conf', copy_from_folder='./' ,replace_dict=rp_base_cfg)		
		
	def copy_file(self, in_file_name, copy_from_folder = None ,add_fragment_to_end=[], skip_if_not_there=False, overwrite=False, replace_dict={}):
		if not copy_from_folder:
			copy_from_folder = self.inputfolder
		if skip_if_not_there and not os.path.isfile(copy_from_folder.rstrip('/')+'/'+in_file_name):
			return False
		in_file = open (copy_from_folder.rstrip('/')+'/'+in_file_name, 'r')
		file_str = in_file.read()
		in_file.close()
		if os.path.isfile(self.name+'/'+in_file_name) and not overwrite: ## do not overwrit if the file exists
			return True
		for fragment in add_fragment_to_end:
			file_str += '\n'+fragment
		for replace in replace_dict: ## replace Variable by the value. 
			file_str = file_str.replace(replace,replace_dict[replace])
		out_file = open(self.name+'/'+in_file_name,'w')
		out_file.write(file_str)
		out_file.close()
		return True
	def write_cfg(self, add_run=None, add_dbs=None):
		if add_run:
			out_file = open(self.name+'/'+add_run+'.conf','w')
		else:
		 	out_file = open(self.name+'/DAS.conf','w')
		out_file.write('[global]\n')
		if "naf" in os.environ["HOSTNAME"]:
			out_file.write('include=grid_control_fullembedding_data_base_naf.conf\n')
		elif self.finalstate=="Preselection":
			out_file.write('include=grid_control_fullembedding_data_base_preselection.conf\n')
		else:
			out_file.write('include=grid_control_fullembedding_data_base_freiburg.conf\n')
		if "etp.kit.edu" in os.environ["HOSTNAME"]:
			out_file.write('workdir = /portal/ekpbms2/home/{user}/embedding/legacy/gc_workdir/{particle_to_embed}_{name}\n'.format(
								user=os.environ["USER"],
								particle_to_embed=self.particle_to_embed,
								name=out_file.name.split('.')[0]						
								))
		elif "naf" in os.environ["HOSTNAME"]:
			out_file.write('workdir = /nfs/dust/cms/user/{user}/embedding/gc_workdir/{particle_to_embed}_{name}\n'.format(
								user=os.environ["USER"],
								particle_to_embed=self.particle_to_embed,
								name=out_file.name.split('.')[0]						
								))
		else:
			print "Host for job submission unknown. Please set workdir manually"
		out_file.write('[CMSSW]\n')
		if add_run and not add_dbs:
			out_file.write('dataset = '+self.particle_to_embed+'_'+self.name+'_'+add_run+' :  list:'+add_run+'.dbs\n')
		if add_dbs:
			for akt_name in add_dbs:
				out_file.write('dataset = '+self.particle_to_embed+'_'+self.name+'_'+akt_name+' :  dbs:'+add_dbs[akt_name]+'\n')
		out_file.close()
		self.gc_cfgs.append(out_file.name) ## save the 
		
	def write_while(self, overwrite=False):
	        if os.path.isfile(self.name+'/while.sh') and not overwrite:
			return
		out_file = open(self.name+'/while.sh','w')
		out_file.write('#!/bin/bash\n')
		out_file.write('\n')
		out_file.write('touch .lock\n')
		out_file.write('\n')
		out_file.write('while [ -f ".lock" ]\n')
		out_file.write('do\n')
		for akt_cfg in self.gc_cfgs:
			out_file.write('go.py '+akt_cfg.split("/")[1]+' -G \n')
		out_file.write('echo "rm .lock"\n')
		out_file.write('sleep 2\n')
		out_file.write('done\n')
		out_file.close()
		os.chmod(self.name+'/while.sh',stat.S_IRWXU)
	def make_generator_frag_map(self,this_finalstate,generator_frag_map=None):
		if generator_frag_map is None:
			generator_frag_map = {}
			if this_finalstate=="MuTau":
				generator_frag_map["MuTau"] = "process.generator.HepMCFilter.filterParameters.MuHadCut = cms.string('Mu.Pt > 18 && Had.Pt > 18 && Mu.Eta < 2.2 && Had.Eta < 2.4')"
				generator_frag_map["MuTau"]+="\n"
				generator_frag_map["MuTau"]+="process.generator.HepMCFilter.filterParameters.Final_States=cms.vstring('MuHad')"
			elif this_finalstate=="ElTau":
				generator_frag_map["ElTau"] = "process.generator.HepMCFilter.filterParameters.ElHadCut = cms.string('El.Pt > 18 && Had.Pt > 18 && El.Eta < 2.2 && Had.Eta < 2.4')"
				generator_frag_map["ElTau"]+="\n"
				generator_frag_map["ElTau"]+="process.generator.HepMCFilter.filterParameters.Final_States=cms.vstring('ElHad')"
			elif this_finalstate=="ElMu":
				generator_frag_map["ElMu"] = "process.generator.HepMCFilter.filterParameters.ElMuCut = cms.string('(El.Pt > 19 && Mu.Pt > 9) || (El.Pt > 9 && Mu.Pt > 19)')"
				generator_frag_map["ElMu"]+="\n"
				generator_frag_map["ElMu"]+="process.generator.HepMCFilter.filterParameters.Final_States=cms.vstring('ElMu')"
			elif this_finalstate=="TauTau":
				generator_frag_map["TauTau"] = "process.generator.HepMCFilter.filterParameters.HadHadCut = cms.string('Had1.Pt > 20 && Had2.Pt > 20 && Had1.Eta < 2.2 && Had2.Eta < 2.2')"
				generator_frag_map["TauTau"]+="\n"
				generator_frag_map["TauTau"]+="process.generator.HepMCFilter.filterParameters.Final_States=cms.vstring('HadHad')"
			elif this_finalstate=="MuMu":
				generator_frag_map["MuMu"]="process.generator.HepMCFilter.filterParameters.Final_States=cms.vstring('MuMu')"
				if self.particle_to_embed == "MuEmbedding":
					generator_frag_map["MuMu"] +='\nprocess.generator.nAttempts = cms.uint32(1)'
			elif this_finalstate=="ElEl":
				generator_frag_map["ElEl"]="process.generator.HepMCFilter.filterParameters.Final_States=cms.vstring('ElEl')"
				if self.particle_to_embed == "ElEmbedding":
					generator_frag_map["ElEl"] +='\nprocess.generator.nAttempts = cms.uint32(1)'
			elif this_finalstate=="Preselection":
				generator_frag_map["Preselection"]=""					
		return generator_frag_map
