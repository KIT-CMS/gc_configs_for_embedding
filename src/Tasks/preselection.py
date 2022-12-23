import os
from src.Task import Task
from read_filelist_from_das import read_filelist_from_das



class PreselectionTask(Task):
    def __init__(
        self, era, workdir, configdir, config, backend, run, user, no_tmux, isMC, input_samples=None
    ):
        Task.__init__(
            self, era, workdir, configdir, config, backend, run, user, no_tmux, isMC
        )
        self.input_samples=self.config["input_samples"][self.era]
        self.preselection = True
        self.finalstate = "preselection"
        self.particle_to_embed = "preselection"
        self.cmsRun_order = ["preselection.py"]
        self.name = self.identifier + "_preselection"
        self.cmssw_version = self.config["cmssw_version"][era]["main"]
        self.input_samples = input_samples


    def build_filelist(self):
        for run in self.runs:
            filelist = PreselectionFilelist(
                configdir=self.configdir,
                era=self.era,
                grid_control_path=self.gc_path,
                run=run,
                finalstate="preselection",
                isMC=self.isMC,
            )
            filelist.build_filelist()
    
    def upload_tarballs(self):
        self.console.log("Not needed for preselection --> Exiting ")

    def publish_dataset(self):
        self.console.log("Ne need to publish preselection datasets --> Exiting")

    def build_generator_fragment(self):
        self.console.log("No generator fragment needed for preselection")

    def build_python_configs(self):
        self.console.log("Setting up python configs")
        add_fragment_to_end = []
        with open("scripts/customise_for_gc.py", "r") as (function_to_add):
            add_fragment_to_end.append(function_to_add.read())
        add_fragment_to_end.append("process = customise_for_gc(process)")
        self.copy_file(
            self.cmsRun_order[0],
            add_fragment_to_end=add_fragment_to_end,
            skip_if_not_there=True,
        )

    def build_gc_configs(self):
        self.console.log("Setting up gc configs")
        for run in self.runs:
            self.write_gc_config("grid_control_preselection.conf", run)

        rp_base_cfg = {}
        rp_base_cfg["__CMSRUN_ORDER__"] = "config file = preselection.py"
        se_path_str = ("se path = {path}").format(
            path=self.config["output_paths"]["preselection"].replace(
                "{USER}", self.user
            )
        )
        se_output_pattern_str = (
            "se output pattern = "
            + "preselection"
            + "_"
            + self.identifier
            + "/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@"
        )
        rp_base_cfg["__CMSSW_BASE__"] = os.path.join(
            os.path.dirname(os.path.abspath(self.cmssw_version)),
            self.cmssw_version + "/",
        )
        rp_base_cfg["__SE_PATH__"] = se_path_str
        rp_base_cfg["__SE_OUTPUT_PATTERN__"] = se_output_pattern_str
        rp_base_cfg[
            "__partition_lfn_modifier__"
        ] = "partition lfn modifier = <xrootd:nrg>"
        rp_base_cfg["__SE_OUTPUT_FILE__"] = "se output files = PreRAWskimmed.root"
        self.copy_file(
            "scripts/base_configs/grid_control_preselection.conf",
            copy_from_folder="./",
            replace_dict=rp_base_cfg,
        )

    def write_gc_config(self, outfile, run):
        out_file = open(self.name + "/" + run + ".conf", "w")
        out_file.write("[global]\n")
        out_file.write(("include={}\n").format(outfile))
        if "etp.kit.edu" in os.environ["HOSTNAME"] and self.workdir == "":
            workdir = f"/work/{self.user}/embedding/UL/gc_workdir"
        elif "naf" in os.environ["HOSTNAME"] and self.workdir == "":
            workdir = f"/nfs/dust/cms/user/{self.user}/embedding/gc_workdir"
        else:
            workdir = self.workdir
        out_file.write(
            f"workdir = {workdir}/{self.particle_to_embed}_{out_file.name.split('.')[0]}\n"
        )
        out_file.write("[CMSSW]\n")
        if self.input_samples:
            dbs_name = self.input_samples[run]
        else:
            dbs_name = (f"/DoubleMuon/{run}-v1/RAW")
        filelistname = f"DoubleMuon_{run}_RAW.dbs"
        read_filelist_from_das(
            f"{self.particle_to_embed}_{self.name}_DoubleMuon_{run}",
            dbs_name,
            f"{self.name}/{filelistname}",
            False,
            "root://cms-xrd-global.cern.ch/",
        )
        out_file.write(f"dataset = {self.particle_to_embed}_{self.name}_DoubleMuon_{run} : list:{filelistname}\n")
        out_file.close()
