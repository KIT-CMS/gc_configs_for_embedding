# Embedding Configurations

This package collects the configs (cmsRun, gridcontrol, inputs dbs files) for embedding, such that one can start a large scale production

## Current Status

Code Portation: 

- [ ] UL2016preVFP
- [ ] UL2016postVFP
- [x] UL2017
- [x] UL2018

Additional features needed

- [x] Fiellist creation for completed Embedding Datasets
- [x] Dataset Publication
- [ ] Integrate Dataset Publication into the main script
- [x] Extention to other computer infrastructures than KIT

## UL Campaign

The setup is done automatically, using the `create_UL_campaign.py` tool.

```
usage: create_UL_campaign.py [-h] [--workdir WORKDIR] --era {2017,2018}
                             [--final-state {MuTau,ElTau,ElMu,TauTau,MuEmb,ElEmb}]
                             [--run RUN [RUN ...]] --mode
                             {preselection,full,nanoaod} --task
                             {setup_cmssw,upload_tarballs,setup_jobs,run_production,create_filelist,publish_dataset}
                             [--backend {etp,naf,lxplus}]
                             [--custom-configdir CUSTOM_CONFIGDIR] [--mc]
                             [--no_tmux]

Setup Grid Control for Embedding Production

optional arguments:
  -h, --help            show this help message and exit
  --workdir WORKDIR     path to the workdir
  --era {2017,2018}     Era used for the production
  --final-state {MuTau,ElTau,ElMu,TauTau,MuEmb,ElEmb}
                        Name the final state you want to process
  --run RUN [RUN ...]   Name or list of the runs you want to process, use all
                        to process all runs of an era
  --mode {preselection,full,nanoaod}
                        Select preselection mode, full embedding mode or
                        nanoaod mode
  --task {setup_cmssw,upload_tarballs,setup_jobs,run_production,create_filelist,publish_dataset}
                        Different commands that are possible
  --backend {etp,naf,lxplus}
                        Select the condor backend that is used.
  --custom-configdir CUSTOM_CONFIGDIR
                        If this is set, use the configdir from the given
                        folder
  --mc                  If this is set, mc embedding is run instead of data
                        embedding
  --no_tmux             If this is set, no tmux is used to run the jobs

```

---

### Setup

Install the framework using
```
git clone --recursive git@github.com:KIT-CMS/gc_configs_for_embedding.git
```
---

## Configurations

The large part of the embedding specific configuration settings can be found in [scripts/ul_config.yaml](scripts/ul_config.yaml)

## Preselection

### Setup
For the preselection, only a single CMSSW version is needed. The version can be installed using
```bash
python3 create_UL_campaign.py --mode preselection --era 2018 --task setup_cmssw --run all
```

then, the different preselection tasks for all runs in a single era can be setup using
```bash
python3 create_UL_campaign.py --mode preselection --era 2018 --task setup_jobs --workdir /path/to/workdir --run all
```
or a single run can be specified by using the name of the run instead of `all`. If a space sepatated list of Runs is provided, those Runs will be processed. The workdir is the folder, that grid-control will use to keep track of the different jobs and store the respective job logfiles.

### Production
The Production of the preselection can be started using
```bash
python3 create_UL_campaign.py --mode preselection --era 2018 --task run_production --run all
```
This will automatically start the fitting grid control tasks.
### Output Collection
After successful completion of the preselection task, the output filelist can be generated using
```bash
python3 create_UL_campaign.py --mode preselection --era 2018 --task create_filelist --run all
```
---

## Full Campaign

### Setup
For the full campaign, two CMSSW versions are needed. They are setup using
```bash
python3 create_UL_campaign.py --mode full --era 2018 --task setup_cmssw --final-state $FINALSTATENAME
```
The possible Final State names are:
```
FINALSTATENAME = ["MuTau", "ElTau", "ElMu", "TauTau", "MuEmb", "ElEmb"]
```
After this setup, the two tarballs containing the CMSSW code are generated and uploaded to the grid storage using
```bash
python3 create_UL_campaign.py --mode full --era 2018 --task upload_tarballs --final-state $FINALSTATENAME
```
Job setup is done using
```bash
python3 create_UL_campaign.py --mode full --era 2018 --task setup_jobs --final-state $FINALSTATENAME --run all --workdir /path/to/workdir
```
for all runs of an era or by specified the name of the run instead of using `all`.

### Production
The Production of a full campaign can be started using
```bash
python3 create_UL_campaign.py --mode full --era 2018 --task run_production --run all --final-state $FINALSTATENAME
```
This will automatically start the fitting grid control tasks.

### Output Collection

Collecting the output files into a file list is done using
```bash
python3 create_UL_campaign.py --mode full --era 2018 --run all --workdir  /path/to/workdir --task create-filelist --final-state $FINALSTATENAME
```
For this step, it is nessessary to use a different environment, the script will say if a different environment is needed.



### Publish Dataset

TODO

---

## older campaigns

for older campaign, use the [`rereco`](https://github.com/KIT-CMS/gc_configs_for_embedding/tree/rereco) branch
