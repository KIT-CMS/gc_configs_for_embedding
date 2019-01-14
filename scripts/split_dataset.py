

infile = 'datasetlist80X_data.dbs'

runs=['Run2016B','Run2016C','Run2016D','Run2016E','Run2016F','Run2016G']
outfiles = {}
events = {}

for akt_run in runs:
    outfiles[akt_run] = []
    events[akt_run]  = 0


in_file = open(infile, 'r')
for akt_line in in_file.readlines():
    if akt_line.split('_')[0] != 'DoubleMuon':
      for key in outfiles:
	outfiles[key].append(akt_line)
    else:
      akt_key = akt_line.split('_')[1][:8]
      akt_events =  int(akt_line.strip().split('=')[-1])
      if akt_events > 1 :
	  outfiles[akt_key].append(akt_line)
	  events[akt_key] += akt_events
in_file.close()

for akt_out in outfiles:
    akt_out_file = open(akt_out+'.dbs','w')
    for akt_line in outfiles[akt_out]:
	if akt_line[:6] != 'events':
	  akt_out_file.write(akt_line)
	else:
	  akt_out_file.write('events = '+str(events[akt_out])+'\n')
    akt_out_file.close()
    
for akt_run in runs:
    print akt_run,events[akt_run]

