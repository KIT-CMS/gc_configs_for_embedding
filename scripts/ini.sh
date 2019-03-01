
source /cvmfs/grid.cern.ch/emi3ui-latest/etc/profile.d/setup-ui-example.sh
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch

source $VO_CMS_SW_DIR/cmsset_default.sh

cd /portal/ekpbms1/home/${USER}/embedding/CMSSW_10_2_4_patch1/src/

cmsenv

export PATH=$PATH:/portal/ekpbms1/home/${USER}/embedding/CMSSW_10_4_patch1/src/grid-control

export PATH=$PATH:/portal/ekpbms1/home/${USER}/embedding/CMSSW_10_2_4_patch1/src/grid-control/scripts


export X509_USER_PROXY=~/.globus/x509up

voms-proxy-info

echo "voms-proxy-init --voms cms:/cms/dcms --valid 192:00 --out ${X509_USER_PROXY}"

