# gc_configs_for_embedding

This package collects the configs (cmsRun, gridcontrol, inputs dbs files) for embedding, such that one can start a large scale production

## UL Campaign

The setup is done automatically, using the `create_UL_campaign.py` tool.

```
usage: create_UL_campaign.py [-h] [--workdir WORKDIR] --era {2018}
                             [--final-state {MuTau,ElTau,ElMu,TauTau,MuEmb,ElEmb}]
                             [--run RUN] --mode {preselection,full} --task
                             {setup_cmssw,upload_tarballs,setup_jobs,run_production,create_filelist,publish_dataset}
                             [--backend {etp,naf,cern}]

Setup Grid Control for Embedding Production

optional arguments:
  -h, --help            show this help message and exit
  --workdir WORKDIR     path to the workdir
  --era {2018}          Era used for the production
  --final-state {MuTau,ElTau,ElMu,TauTau,MuEmb,ElEmb}
                        Name the final state you want to process
  --run RUN             Name of the Run you want to process
  --mode {preselection,full}
                        Select preselection mode of full embedding mode
  --task {setup_cmssw,upload_tarballs,setup_jobs,run_production,create_filelist,publish_dataset}
                        Different commands that are possible
  --backend {etp,naf,cern}
                        Select the condor backend that is used -- TODO --

```

### Setup

Install the framework using
```
git clone --recursive @github.com:KIT-CMS/gc_configs_for_embedding.git
```


### Preselection

#### Setup
For the preselection, only a single CMSSW version is needed. The version can be installed using
```bash
./create_UL_campaign.py --mode preselection --era 2018 --task setup_cmssw
```

then, the different preselection tasks for all runs in a single era can be setup using
```bash
./create_UL_campaign.py --mode preselection --era 2018 --task setup_jobs --run all
```
or a single run can be specified by using the name of the run instead of `all`.
### Production
The Production of the preselection can be started using
```bash
./create_UL_campaign.py --mode preselection --era 2018 --task run_production --run all
```
This will automatically start the fitting grid control tasks.
### Output Collection
After successful completion of the preselection task, the output filelist can be generated using
```bash
./create_UL_campaign.py --mode preselection --era 2018 --task create_filelist --run all
```

### Full Campaign

#### Setup
For the full campaign, two CMSSW versions are needed. They are setup using
```bash
./create_UL_campaign.py --mode full --era 2018 --task setup_cmssw --final-state $FINALSTATENAME
```
The possible Final State names are:
```
FINALSTATENAME = ["MuTau", "ElTau", "ElMu", "TauTau", "MuEmb", "ElEmb"]
```
After this setup, the two tarballs containing the CMSSW code are generated and uploaded to the grid storage using
```bash
./create_UL_campaign.py --mode full --era 2018 --task upload_tarballs --final-state $FINALSTATENAME
```
Job setup is done using
```bash
./create_UL_campaign.py --mode full --era 2018 --task setup_jobs --final-state $FINALSTATENAME --run all
```
for all runs of an era or by specified the name of the run instead of using `all`.

### Production
The Production of a full campaign can be started using
```bash
./create_UL_campaign.py --mode full --era 2018 --task run_production --run all --final-state $FINALSTATENAME
```
This will automatically start the fitting grid control tasks.

### Output Collection
After successful completion of the preselection task, the output filelist can be generated using
```bash
./create_UL_campaign.py --mode preselection --era 2018 --task create_filelist --run all
```
### Publish Dataset

TODO


## older campaigns

for older campaign, use the [`rereco`](https://github.com/KIT-CMS/gc_configs_for_embedding/tree/rereco) branch