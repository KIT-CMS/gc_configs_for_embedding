import os
import argparse
import gzip
from datetime import datetime
from datetime import date
#~ from datetime import 
import json
import time
import matplotlib.pyplot as plt

def str_to_sec(time):
	year=int(time[:4])
	month=int(time[5:6]) if time[5]!='0' else int(time[6])
	day=int(time[8:10])
	sec=(date(year,month,day)-date(2017,1,1)).total_seconds()
	#~ print time
	#~ startday = time[8:10]
	#~ print startday
	#~ sec = int(startday)*24*60*60
	
	time=time[11:]
	
	sec+= int(time[:2])*60*60
	sec+= int(time[3:5])*60
	sec+= int(time[6:8])
	return sec

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="Track status of gridcontrol job.")
	parser.add_argument("-w", "--workbase", required=False, default = "",
						help="GC working directory [Default: here]")
	parser.add_argument("--loop", default=None,	help="Loop the script all LOOP seconds.")
	parser.add_argument("-o","--output", default='output',	help="Output file. If it exists, values stay and new values will be added to the end. [Default: tracking.json]")
	parser.add_argument("-id","--identifier", default='',	help="Only tracks folders that have identifier string somewhere in them.")
	parser.add_argument("-bl","--blacklist", default=[],	nargs='*', help="Excludes any that have blacklist string somewhere in them. Possible to give multiple strings. (Will select according to name of job that is printed by this script)")
	parser.add_argument("-p","--plot", default=False, action='store_true', help="Plot results to png output file. Will have same name as output json file. [Default: False]")
	parser.add_argument("-v","--verbose", default=True, action='store_false', help="More output on screen, including error codes of failed jobs.")
	parser.add_argument("-r","--only-running", default=False, action='store_true', help="Track only GC tasks that have at least one job in RUNNING.")

	args = parser.parse_args()
	last_time={}

	skip=[]
	if not os.path.exists(args.output):
		os.mkdir(args.output)
	last_time_stamp=time.time()
	while True:
		workdir_list=[]
		output_list=[]
		
		print '\n\033[94m'+'Time:		'+str(datetime.now())[:-7]+'\033[0m'
		if os.path.exists(os.path.join(args.workbase,'current.conf')):
					workdir_list.append(os.path.join(args.workbase))
					output_list.append(os.path.basename(args.workbase))
		else:
			for d in os.listdir(os.path.join(args.workbase)):
					if os.path.exists(os.path.join(args.workbase,d,'current.conf')):
						if args.identifier in os.path.join(args.workbase,d):
							workdir_list.append(os.path.join(args.workbase,d))
							output_list.append(d)
						continue
					if os.path.isdir(os.path.join(args.workbase,d)):
						for d2 in os.listdir(os.path.join(args.workbase,d)):
							if os.path.exists(os.path.join(args.workbase,d,d2,'current.conf')):
								if args.identifier in os.path.join(args.workbase,d,d2):
									workdir_list.append(os.path.join(args.workbase,d,d2))
									output_list.append(d+'_'+d2)

		for i in range(len(workdir_list)):
			in_blacklist=False
			for blacklisted_string in args.blacklist:
				if blacklisted_string in output_list[i] or output_list[i] in skip:
					in_blacklist=True
			if in_blacklist:
				continue
			
			workdir=workdir_list[i]
			output=output_list[i]+'.json'
			
			if args.loop is not None:
				loop=True
				delay=int(args.loop)
			else: 
				loop=False

			if not output[-5:]=='.json':
				print "Output file needs to be a json file."
				exit()
			if not os.path.isabs(output):
				output=os.path.join(os.getcwd(),output)
			if not os.path.isabs(workdir):
				workdir=os.path.join(os.getcwd(),workdir)
			if not os.path.exists(os.path.join(workdir,'current.conf')):
				if not args.plot or loop:
					print "Workdir "+workdir+" is not a valid grid control workdir."
					exit()

			with gzip.open(workdir+'/params.map.gz','r') as f:
				n_jobs=int(f.read().strip('\n'))




		

			if loop or not args.plot:
				done=[]
				success=[]
				failed=[]
				exitcode=[]
				exitcode_id=[]
				submitted=[]
				current_time = str(datetime.now())
				states={}
				possible_states=[]
				runtime={}
				ekp=[]
				if os.path.exists(os.path.join(workdir,'jobs')):
					for d in os.listdir(os.path.join(workdir,'jobs')):
						try:
							f=open(os.path.join(workdir,'jobs',d))
							for line in f.readlines():
								
								if line[:3]=='wn=' and not 'bwforcluster' in line:
									ekp.append(int(d.strip('job_').strip('.txt')))
									#print d.strip('job_').strip('.txt')
								if not line[:9]=='retcode=0' and line[:8]=='retcode=':
									exitcode.append(line[8:].strip('\n'))
									exitcode_id.append(int(d.strip('job_').strip('.txt')))
								elif line[:7]=='status=':
									job_status=line[8:].strip('"\n')
									if job_status not in possible_states:
										possible_states.append(job_status)
										states.setdefault(job_status,[])
										states[job_status].append(int(d.strip('job_').strip('.txt')))
									else:
										states[job_status].append(int(d.strip('job_').strip('.txt')))
								elif not line.strip('\n')=='runtime=-1' and not line.strip('\n')=='runtime=0' and line[:8]=='runtime=':
									runtime.setdefault(d.strip('job_').strip('.txt'),float(line[8:].strip('\n')))
							f.close()
						except: 
							pass
				#~ print output_list[i]
				#~ print states['SUCCESS']
				#~ continue
				#~ for l in range(len(exitcode)):
					#~ if exitcode[l]=='121':
						#~ if int(exitcode_id[l]) in states['FAILED']:
							#~ print exitcode_id[l]
				n_success=0
				n_failed=0
				n_submitted=0
				n_running=0
				n_ready=0

				if 'SUCCESS' in possible_states:
					n_success=len(states['SUCCESS'])
				if 'READY' in possible_states:
					n_ready=len(states['READY'])
				if 'FAILED' in possible_states:
					n_failed=len(states['FAILED'])
				if 'SUBMITTED' in possible_states:
					n_submitted=len(states['SUBMITTED'])
				if 'RUNNING' in possible_states:
					n_running=len(states['RUNNING'])
				
				
				if args.only_running:
					if n_running==0:
						skip.append(output_list[i])
						continue
				exitcode_failed=[]

				for j in range(len(exitcode)):
						#print exitcode_id[j]
					if 'FAILED' in states.keys():
						if exitcode_id[j] in states['FAILED']:
							exitcode_failed.append(exitcode[j])
				codes={}
				for code in set(exitcode):
					codes.setdefault(code,exitcode.count(code))
					codes.setdefault('FAILED_'+code,exitcode_failed.count(code))
				average_runtime=0.
				n=0
				max_runtime=0.
				min_runtime=1.0e300
				for job in runtime.keys():
					if 'SUCCESS' in possible_states:
						if int(job) in states['SUCCESS']:
							average_runtime+=float(runtime[job])
							if runtime[job]>max_runtime:
								max_runtime=runtime[job]
                                                        if runtime[job]<min_runtime:
                                                                min_runtime=runtime[job]

							n+=1
				if n>0:
					average_runtime=average_runtime/float(n)

				
				if os.path.exists(os.path.join(os.path.dirname(output),args.output,output+".json")):
					t_json=open(os.path.join(os.path.dirname(output),args.output,output+".json"),'r+')
					trackingdict = json.load(t_json)
					trackingdict.setdefault('INFO',workdir)
					if not "READY" in trackingdict.keys():
					
						trackingdict.setdefault('READY',[])
						trackingdict['READY']={}
					t_json.close()
				else:
					trackingdict = {}
					trackingdict.setdefault('INFO',workdir)
					trackingdict.setdefault('SUBMITTED',[])
					trackingdict.setdefault('READY',[])
					trackingdict.setdefault('RUNNING',[])
					trackingdict.setdefault('FAILED',[])
					trackingdict.setdefault('SUCCESS',[])
					trackingdict.setdefault('TOTAL',[])
					trackingdict.setdefault('ERRORCODE',[])
					trackingdict.setdefault('RUNTIME',[])
					trackingdict.setdefault('JOB_ID',[])

					trackingdict['SUBMITTED']={}
					trackingdict['READY']={}
					trackingdict['RUNNING']={}
					trackingdict['FAILED']={}
					trackingdict['SUCCESS']={}
					trackingdict['TOTAL']=n_jobs
					trackingdict['ERRORCODE']={}
					trackingdict['RUNTIME']={}
					trackingdict['JOB_ID']={}
			
				trackingdict['SUBMITTED'].update({current_time: n_submitted})
				trackingdict['READY'].update({current_time: n_ready})
				trackingdict['RUNNING'].update({current_time: n_running})
				trackingdict['FAILED'].update({current_time: n_failed})
				trackingdict['SUCCESS'].update({current_time: n_success})
				trackingdict['ERRORCODE'].update({current_time: codes})
				trackingdict['RUNTIME'].update(runtime)
				trackingdict['JOB_ID'].update(states)
				
				gain=''
			#	print last_time.keys()
				if output_list[i] in last_time.keys():
					if last_time[output_list[i]]<n_success:	
						gain='+'+str(n_success-last_time[output_list[i]])+' in last '+str(round((time.time()-last_time_stamp)/60./60.,2))+' hours'
				else:
					last_time_stamp=time.time()
					last_time.setdefault(output_list[i],n_success)

			
				
				skip_info=False
				if(n_success==n_jobs):
					print '\033[92m'+'         '+output_list[i]+' completed\033[0m'
			
				else:
					print '         '+output_list[i]
				
				if not args.verbose:
					print 'Average Runtime:		'+str(round(average_runtime/60./60.,2))+' hours'
                                        print 'Min Runtime:         '+str(round(min_runtime/60./60.,2))+' hours'
                                        print 'Max Runtime:         '+str(round(max_runtime/60./60.,2))+' hours'

				print '\033[92m'+'Finished:	'+str(100*round(float(n_success)/float(n_jobs),3))+'% '+gain+'\033[0m'
				if not args.verbose:
					print 'Time:		'+current_time[:-7]
					print 'Total jobs:	'+str(n_jobs)
					print 'Submitted:	'+str(n_submitted)
					print 'Ready:		'+str(n_ready)
				print '\033[94m'+'Running:	'+str(n_running)+'\033[0m'
				if not args.verbose:	
					print '\033[92m'+'Successful:	'+str(n_success)+'\033[0m'
					print '\033[91m'+'Failed:		'+str(n_failed)+'\033[0m'
					#~ if len(exitcode)>0:
						#~ print 'All Exitcodes:	'
						#~ for code in codes.keys():
							#~ print code+':	occured '+str(codes[code])+' times.'
						#~ print '\n'
					if len(exitcode)>0:
						print 'Exitcodes of jobs currently in failed:	'
						for code in codes.keys():
							if code[:6]=='FAILED':
								if codes[code] > 0:
									print code[7:]+':	occured '+str(codes[code])+' times.'
			
				#~ if (time.time()-last_time_stamp)>(60.*60.):
					#~ last_time_stamp=time.time()
					#~ last_time[output_list[i]]=n_success
					
				t_json=open(os.path.join(os.path.dirname(output),args.output,output),'w')
				t_json.write(json.dumps(trackingdict, sort_keys=True, indent=2))
				t_json.close()
				if not args.verbose:
					print '\nJob info was written to '+os.path.join(os.path.dirname(output),args.output,output)
			
			else:
				print 'Plotting only mode. Plotting from '+os.path.join(os.path.dirname(output),args.output,output+".json")
				t_json=open(os.path.join(os.path.dirname(output),args.output,output+".json"),'r+')
				trackingdict = json.load(t_json)
				t_json.close()
		
			if args.plot is not None:
				starttime=min([float(str_to_sec(str(x))) for x in trackingdict['SUBMITTED'].keys()])
				x=[]
				xticks = []
				xlabels=[]
				SUBMITTED=[]
				RUNNING=[]
				SUCCESS=[]
				FAILED=[]
				INIT=[]
				key=[]
				for tm in trackingdict['SUBMITTED'].keys():
					key.append(tm)
					x.append(float(str_to_sec(tm)-starttime)/60./60.)
					SUBMITTED.append(trackingdict['SUBMITTED'][tm])
					RUNNING.append(trackingdict['RUNNING'][tm])
					SUCCESS.append(trackingdict['SUCCESS'][tm])
					FAILED.append(trackingdict['FAILED'][tm])
				for i in range(len(SUBMITTED)):
					INIT.append(trackingdict['TOTAL']-SUBMITTED[i]-RUNNING[i]-SUCCESS[i]-FAILED[i])
				SUBMITTED=[e for (d,e) in sorted(zip(x,SUBMITTED))]
				INIT=[e for (d,e) in sorted(zip(x,INIT))]
				RUNNING=[e for (d,e) in sorted(zip(x,RUNNING))]
				SUCCESS=[e for (d,e) in sorted(zip(x,SUCCESS))]
				FAILED=[e for (d,e) in sorted(zip(x,FAILED))]
				key=[e for (d,e) in sorted(zip(x,key))]
				x=sorted(x)

				plt.plot(x,INIT,'k')
				plt.plot(x,SUBMITTED,'y')
				plt.plot(x,RUNNING,'b')
				plt.plot(x,SUCCESS,'g')
				plt.plot(x,FAILED,'r')
				
				nticks=4
				xticks_pos=[]
				xticks=[]
				div=float(len(x))/float(nticks)
				for i in range(nticks+1):
					if i==nticks:
						xticks_pos.append(x[int(i*div-1)])
						xticks.append(key[int(i*div-1)][5:16])
						break
					xticks_pos.append(x[int(i*div)])
					xticks.append(key[int(i*div)][5:16])
				#labels = [z for z in 
				plt.xticks(xticks_pos,xticks)
				#plt.ylim(0,10000)
				plt.xlabel('Time')
				plt.ylabel('Jobs')
				#plt.yscale('log')
				#
				#plt.xlim(0,30)
				plt.legend(['init' , 'submitted', 'running', 'success', 'failed'], loc='upper center')
				plot_name=output.strip('.json')+'.png'
				plt.savefig(os.path.join(os.path.dirname(output),args.output,os.path.basename(plot_name)))
				plt.clf()
				if not args.verbose:
					print 'Plot '+os.path.join(os.path.dirname(output),args.output,os.path.basename(plot_name))+' created.'


			
		if not loop:
			exit()
		time.sleep(delay)
