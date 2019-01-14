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
	parser.add_argument("-w", "--workdir", required=False, default = "",
						help="GC working directory [Default: here]")
	parser.add_argument("--loop", default=None,	help="Loop the script all LOOP seconds.")
	parser.add_argument("-o","--output", default='tracking.json',	help="Output file. If it exists, values stay and new values will be added to the end. [Default: tracking.json]")
	parser.add_argument("-p","--plot", default=None, help="Plot results to png output file. [Default: None]")
	args = parser.parse_args()
	workdir=args.workdir

	if args.loop is not None:
		loop=True
		delay=int(args.loop)
	else: 
		loop=False

	if not args.output[-5:]=='.json':
		print "Output file needs to be a json file."
		exit()
	if not os.path.isabs(args.output):
		args.output=os.path.join(os.getcwd(),args.output)
	if not os.path.isabs(workdir):
		workdir=os.path.join(os.getcwd(),workdir)
	if not os.path.exists(os.path.join(workdir,'current.conf')):
		if args.plot is None or loop:
			print "Workdir "+workdir+" is not a valid grid control workdir."
			exit()
	else:
		with gzip.open(workdir+'/params.map.gz','r') as f:
			n_jobs=int(f.read().strip('\n'))




	
	while True:
		if loop or args.plot is None:
			done=[]
			success=[]
			failed=[]
			exitcode=[]
			submitted=[]
			current_time = str(datetime.now())
			states={}
			possible_states=[]
			runtime={}
			if os.path.exists(os.path.join(workdir,'jobs')):
				for d in os.listdir(os.path.join(workdir,'jobs')):
					f=open(os.path.join(workdir,'jobs',d))
					for line in f.readlines():
						if not line[:9]=='retcode=0' and line[:8]=='retcode=':
							exitcode.append(line[8:].strip('\n'))
						elif line[:7]=='status=':
							job_status=line[8:].strip('"\n')
							if job_status not in possible_states:
								possible_states.append(job_status)
								states.setdefault(job_status,[])
								states[job_status].append(int(d[4]))
							else:
								states[job_status].append(int(d.strip('job_').strip('.txt')))
						elif not line.strip('\n')=='runtime=-1' and not line.strip('\n')=='runtime=0' and line[:8]=='runtime=':
							runtime.setdefault(d.strip('job_').strip('.txt'),float(line[8:].strip('\n')))
					f.close()

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
			codes={}
			for code in set(exitcode):
				codes.setdefault(code,exitcode.count(code))
			print 'Time:		'+current_time[:-7]
			print 'Total jobs:	'+str(n_jobs)
			print 'Submitted:	'+str(n_submitted)
			print 'Ready:		'+str(n_ready)
			print '\033[94m'+'Running:	'+str(n_running)+'\033[0m'
			print '\033[92m'+'Successful:	'+str(n_success)+'\033[0m'
			print '\033[91m'+'Failed:		'+str(n_failed)+'\033[0m'
			if len(exitcode)>0:
				print '\nExitcodes:	'
				for code in codes.keys():
					print code+':	occured '+str(codes[code])+' times.'
			
			
			if os.path.exists(args.output):
			
				t_json=open(args.output,'r+')
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


			t_json=open(args.output,'w')
			t_json.write(json.dumps(trackingdict, sort_keys=True, indent=2))
			t_json.close()
			print '\nJob info was written to '+args.output
		
		else:
			print 'Plotting only mode. Plotting from '+args.output
			t_json=open(args.output,'r+')
			trackingdict = json.load(t_json)
			t_json.close()
	
		if args.plot is not None:
			if args.plot[-4:]!='.png':
				print 'Output plot must be .png format. Exiting.'
				exit()

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
			
			plt.savefig(args.plot)
			plt.clf()
			print 'Plot '+args.plot+' created.'



			
		if not loop:
			exit()
		time.sleep(delay)
