# Embedding 2016 legacy production

## Setup

The full Analysis can be setup by running `checkout_2016_legacy.sh` for example with

```sh
wget https://raw.githubusercontent.com/KIT-CMS/gc_configs_for_embedding/master/scripts/checkout_2016_legacy.sh && source ./checkout_2016_legacy.sh
```

This will setup two CMSSW Versions, `8_0_33` and `9_4_14`. The version 8xx is used to run the embedding process up to an AODSIM ouput. The AODSIM ouput is the processed using the 9xx Version, to generate the final MINIAODSIM used for analyses. 

## Transfering Filelists

After a campaign is finished in the 8xx setup, a filelist has to be generated, which is then used in the 9xx step as input. The filelist can be generated via

```sh
dataset_list_from_gc.py Run2016xx.conf -o Run2016xx_aod.dbs
```

when this step is completed, copy the filelist to the appropriate folder in the 9xx setup and start the conversion into MiniAOD