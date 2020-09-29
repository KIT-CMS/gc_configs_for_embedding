import os, stat
import yaml


class FinalState():
    def __init__(self,
                 era,
                 finalstate,
                 workdir,
                 identifier="",
                 generator_frag="",
                 runs=[],
                 add_dbs=None,
                 inputfolder="Run2016_CMSSW_8_0_26",
                 generator_frag_map=None,
                 reselect=False,
                 preselection=False, config={}):
        if preselection:
            self.finalstate = "preselection"
            self.particle_to_embed = "preselection"
        else:
            self.finalstate = config["finalstate_map"][finalstate]["name"]
            self.particle_to_embed = config["finalstate_map"][finalstate]["embeddedParticle"]
        self.cmssw_version = config["cmssw_version"][era]["main"]
        self.preselection = preselection
        self.inputfolder = inputfolder
        self.cmsRun_order = []
        self.reselect = reselect
        self.runs = runs
        self.workdir = workdir
        self.add_dbs = add_dbs
        # if finalstate == 'ElEmb':
        #     self.finalstate = 'ElEl'
        #     self.particle_to_embed = 'ElEmbedding'
        # elif finalstate == 'MuEmb':
        #     self.finalstate = 'MuMu'
        #     self.particle_to_embed = 'MuEmbedding'
        # else:
        #     self.finalstate = finalstate
        #     self.particle_to_embed = 'TauEmbedding'
        self.identifier = identifier
        if self.preselection:
            self.name = identifier
        else:
            self.name = self.finalstate + "_" + identifier
        self.gc_cfgs = []
        self.era = era
        self.generator_frag = ""
        

    def setup_all(self):
        if not os.path.exists(self.name):
            os.mkdir(self.name)
        if not self.preselection:
            self.generator_frag = self.make_generator_frag(
                finalstate=self.finalstate, preselection=self.preselection)

        self.cmsRun_order = self.copy_pyconfigs(generator_frag=self.generator_frag,
                            reselect=self.reselect, preselection=self.preselection)
        if self.preselection:
            self.copy_gcconfigs(runs=self.runs, add_dbs=self.add_dbs, preselection=self.preselection)
        # self.write_while()

    def copy_pyconfigs(self, generator_frag="", reselect=False,preselection=False):
        is_first = True  ## can be late used to init the first config with customize_for_gc and the later with the dummy stings
        cmsRun_order = []
        files_to_copy = [
            'preselection.py'
        ] if preselection else [
            'selection.py', 'lheprodandcleaning.py', 'generator_preHLT.py',
            'generator_HLT.py', 'generator_postHLT.py', 'merging.py'
        ]
        for file_to_copy in files_to_copy:
            add_fragment_to_end = []
            if is_first:
                with open('scripts/customise_for_gc.py',
                          'r') as function_to_add:
                    add_fragment_to_end.append(function_to_add.read())
                add_fragment_to_end.append(
                    'process = customise_for_gc(process)')
            else:
                add_fragment_to_end.append(
                    '####@FILE_NAMES@, @SKIP_EVENTS@, @MAX_EVENTS@')
            if file_to_copy in ['lheprodandcleaning.py', 'generator_preHLT.py', 'generator_postHLT.py', 'generator_HLT.py']:
                add_fragment_to_end.append(
                    'from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper'
                )
                add_fragment_to_end.append(
                    'randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)'
                )
                add_fragment_to_end.append('randSvc.populate()')
                add_fragment_to_end.append(
                    'print("Generator random seed: %s" % process.RandomNumberGeneratorService.generator.initialSeed)'
                )

                if file_to_copy == 'generator_preHLT.py':
                    add_fragment_to_end.append(generator_frag)
            if file_to_copy == 'lheprodandcleaning.py':
                if self.particle_to_embed == "MuEmbedding":
                    add_fragment_to_end.append(
                        'process.externalLHEProducer.particleToEmbed = cms.int32(13)'
                    )
                if self.particle_to_embed == "ElEmbedding":
                    add_fragment_to_end.append(
                        'process.externalLHEProducer.particleToEmbed = cms.int32(11)'
                    )
            if file_to_copy == 'merging.py' and not "2016" in self.identifier:
                if "Run201" in self.inputfolder:
                    add_fragment_to_end.append(
                        'from TauAnalysis.MCEmbeddingTools.customisers import customiseKeepPrunedGenParticles'
                    )
                    if reselect:
                        add_fragment_to_end.append(
                            'process = customiseKeepPrunedGenParticles(process,True)'
                        )
                    else:
                        add_fragment_to_end.append(
                            'process = customiseKeepPrunedGenParticles(process)'
                        )
            if self.copy_file(file_to_copy,
                              add_fragment_to_end=add_fragment_to_end,
                              skip_if_not_there=True):
                is_first = False
                cmsRun_order.append(file_to_copy)
        return cmsRun_order

    def copy_gcconfigs(self, runs=[], add_dbs=None, preselection=False):
        dbs_folder = "dbs"
        for add_run in runs:
            if not add_dbs:
                if os.path.exists(dbs_folder + "/" + add_run + '.dbs'):
                    self.copy_file(add_run + '.dbs',
                                   copy_from_folder=dbs_folder)
                    "Copied {}".format(dbs_folder + add_run + '.dbs')
                else:
                    print(
                        '{}.dbs could not be found in folder {}. Please run preselection'
                        .format(add_run, dbs_folder))
                if not os.path.exists(self.name + '/' + add_run + '.conf'):
                    self.write_cfg(add_run=add_run, preselection=preselection)
            else:
                self.write_cfg(add_run=add_run, add_dbs=add_dbs, preselection=preselection)
        if len(runs) == 0 and add_dbs:
            self.write_cfg(add_dbs=add_dbs, preselection=preselection)
        cmsRun_order_str = 'config file = '
        for cmsRun_cfg in self.cmsRun_order:
            cmsRun_order_str += cmsRun_cfg + '\n\t\t'
        rp_base_cfg = {}
        rp_base_cfg['__CMSRUN_ORDER__'] = cmsRun_order_str
        if preselection:
            se_path_str = 'se path = srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only/store/user/sbrommer/gc_storage'
            se_output_pattern_str = 'se output pattern = ' + "preselection" + '_' + self.identifier + '/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@'
            rp_base_cfg['__CMSSW_BASE__'] = os.path.join(os.path.dirname(os.path.abspath(self.cmssw_version)),self.cmssw_version + "/")
        else:
            se_path_str = 'se path = srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only/store/user/' + os.environ[
                "USER"] + '/gc_storage/' + self.identifier
            se_output_pattern_str = 'se output pattern = ' + self.finalstate + '_' + self.identifier + '/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@'
        rp_base_cfg['__SE_PATH__'] = se_path_str
        
        rp_base_cfg['__SE_OUTPUT_PATTERN__'] = se_output_pattern_str
        rp_base_cfg[
            '__partition_lfn_modifier__'] = 'partition lfn modifier = <xrootd:nrg>'
        rp_base_cfg['__SE_OUTPUT_FILE__'] = 'se output files = merged.root'

        if preselection:
            self.copy_file(
                'scripts/base_configs/grid_control_fullembedding_data_base_preselection.conf',
                copy_from_folder='./',
                replace_dict=rp_base_cfg)
        else:
            self.copy_file(
                'scripts/base_configs/grid_control_fullembedding_data_base_freiburg.conf',
                copy_from_folder='./',
                replace_dict=rp_base_cfg)
            self.copy_file(
                'scripts/base_configs/grid_control_fullembedding_data_base_naf.conf',
                copy_from_folder='./',
                replace_dict=rp_base_cfg)

    def copy_file(self,
                  in_file_name,
                  copy_from_folder=None,
                  add_fragment_to_end=[],
                  skip_if_not_there=False,
                  overwrite=False,
                  replace_dict={}):
        if not copy_from_folder:
            copy_from_folder = self.inputfolder
        if skip_if_not_there and not os.path.isfile(
                copy_from_folder.rstrip('/') + '/' + in_file_name):
            return False
        in_file = open(copy_from_folder.rstrip('/') + '/' + in_file_name, 'r')
        filename = os.path.basename(in_file_name)
        file_str = in_file.read()
        in_file.close()
        if os.path.isfile(
                self.name + '/' + filename
        ) and not overwrite:  ## do not overwrit if the file exists
            return True
        for fragment in add_fragment_to_end:
            file_str += '\n' + fragment
        for replace in replace_dict:  ## replace Variable by the value.
            file_str = file_str.replace(replace, replace_dict[replace])
        out_file = open(self.name + '/' + filename, 'w')
        out_file.write(file_str)
        out_file.close()
        return True

    def write_cfg(self, add_run=None, add_dbs=None, preselection=False):
        if add_run:
            out_file = open(self.name + '/' + add_run + '.conf', 'w')
        else:
            out_file = open(self.name + '/DAS.conf', 'w')
        out_file.write('[global]\n')
        if "naf" in os.environ["HOSTNAME"]:
            out_file.write(
                'include=grid_control_fullembedding_data_base_naf.conf\n')
        elif preselection:
            out_file.write(
                'include=grid_control_fullembedding_data_base_preselection.conf\n'
            )
        else:
            out_file.write(
                'include=grid_control_fullembedding_data_base_freiburg.conf\n')
        if "etp.kit.edu" in os.environ["HOSTNAME"] and self.workdir == "":
            workdir = '/work/{user}/embedding/UL/gc_workdir'.format(user=os.environ["USER"])
        elif "naf" in os.environ["HOSTNAME"] and self.workdir == "":
            workdir = '/nfs/dust/cms/user/{user}/embedding/gc_workdir'.format(user=os.environ["USER"])
        else:
            workdir = self.workdir
        out_file.write(
            'workdir = {WORKDIR}/{particle_to_embed}_{name}\n'
            .format(WORKDIR=workdir,
                    particle_to_embed=self.particle_to_embed,
                    name=out_file.name.split('.')[0]))
        out_file.write('[CMSSW]\n')
        if add_run and not add_dbs:
            out_file.write('dataset = ' + self.particle_to_embed + '_' +
                           self.name + '_' + add_run + ' :  list:' + add_run +
                           '.dbs\n')
        if add_dbs:
            for akt_name in add_dbs:
                out_file.write('dataset = ' + self.particle_to_embed + '_' +
                               self.name + '_' + akt_name + ' :  dbs:' +
                               add_dbs[akt_name] + '\n')
        out_file.close()
        self.gc_cfgs.append(out_file.name)  ## save the

    # def write_while(self, overwrite=False):
    #     if os.path.isfile(self.name + '/while.sh') and not overwrite:
    #         return
    #     out_file = open(self.name + '/while.sh', 'w')
    #     out_file.write('#!/bin/bash\n')
    #     out_file.write('\n')
    #     out_file.write('touch .lock\n')
    #     out_file.write('\n')
    #     out_file.write('while [ -f ".lock" ]\n')
    #     out_file.write('do\n')
    #     for akt_cfg in self.gc_cfgs:
    #         out_file.write('go.py ' + akt_cfg.split("/")[1] + ' -G \n')
    #     out_file.write('echo "rm .lock"\n')
    #     out_file.write('sleep 2\n')
    #     out_file.write('done\n')
    #     out_file.close()
    #     os.chmod(self.name + '/while.sh', stat.S_IRWXU)


    def make_generator_frag(self, finalstate, preselection=False):
        configdict = yaml.load(open("scripts/ul_config.yaml", 'r'))
        generator_frag = ""
        cuts = configdict["generator_cuts"][self.era][finalstate]
        naming_map = configdict["finalstate_map"][finalstate]
        cutstring = "({LEP1}.Pt > {LEP1_PT_CUT} && {LEP2}.Pt > {LEP2_PT_CUT} && {LEP1}.Eta < {LEP1_ETA_CUT} && {LEP2}.Eta < {LEP2_ETA_CUT})".format(LEP1=naming_map["lep1_name"],
        LEP2=naming_map["lep2_name"],
        LEP1_PT_CUT=cuts["lep1_pt"],
        LEP2_PT_CUT=cuts["lep2_pt"],
        LEP1_ETA_CUT=cuts["lep1_eta"],
        LEP2_ETA_CUT=cuts["lep2_eta"])
        if finalstate == "ElMu":
            # in this channel add the rotated version of the cut as well, as el and mu can be both first or second lepton
            cutstring += "|| ({LEP1}.Pt > {LEP2_PT_CUT} && {LEP2}.Pt > {LEP1_PT_CUT} && {LEP1}.Eta < {LEP2_ETA_CUT} && {LEP2}.Eta < {LEP1_ETA_CUT})".format(LEP1=naming_map["lep1_name"],
            LEP2=naming_map["lep2_name"],
            LEP1_PT_CUT=cuts["lep1_pt"],
            LEP2_PT_CUT=cuts["lep2_pt"],
            LEP1_ETA_CUT=cuts["lep1_eta"],
            LEP2_ETA_CUT=cuts["lep2_eta"])
            generator_frag += "process.generator.HepMCFilter.filterParameters.{CHANNEL}Cut = cms.string('{CUTSTRING}')".format(
            CHANNEL=naming_map["name"], CUTSTRING=cutstring)
        else:
            generator_frag += "process.generator.HepMCFilter.filterParameters.{CHANNEL}Cut = cms.string('{CUTSTRING}')".format(
                CHANNEL=naming_map["name"], CUTSTRING=cutstring)
        generator_frag += "\n"
        generator_frag += "process.generator.HepMCFilter.filterParameters.Final_States=cms.vstring('{CHANNEL}')".format(
            CHANNEL=naming_map["name"])
        generator_frag += '\nprocess.generator.nAttempts = cms.uint32({ATTEMPTS})'.format(
            ATTEMPTS=cuts["attempts"])
        return generator_frag
