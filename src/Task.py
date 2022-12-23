import os
import stat
from rich.console import Console
from src.create_grid_control_script import create_tmux_grid_control_script, create_simple_grid_control_script

class Task:

    console = Console()

    def __init__(
        self,
        era,
        workdir,
        configdir,
        config,
        backend,
        run,
        user=os.getlogin(),
        no_tmux=False,
        isMC=False,
    ):
        self.era = era
        self.workdir = workdir
        self.configdir = configdir
        self.config = config
        self.backend = backend
        self.runs = self._validate_run(run)
        self.user = user
        self.isMC = isMC
        self.gc_path = os.path.abspath("grid-control")
        self.no_tmux = no_tmux

        self.cmssw_versions = {
            "main": self.config["cmssw_version"][self.era]["main"],
            "hlt": self.config["cmssw_version"][self.era]["hlt"],
        }
        self.inputfolder = f"Run{era}_{self.cmssw_versions['main']}_UL"
        self.identifier = f"mc_{self.era}" if isMC else f"data_{self.era}"
        self.name = self.identifier + "_generalTask"
        self.datatype = "mc" if isMC else "data"

    def _validate_run(self, run):
        runlist = []
        if type(run) is not list:
            run = [run]
        if run == ["all"]:
            runlist = self.config["runlist"][self.era]
        else:
            for single_run in run:
                if single_run in self.config["runlist"][self.era]:
                    runlist.append(single_run)
                else:
                    # raise AttributeError
                    self.console.log(
                        f"Run name '{single_run}' unknown: Known runs are: {self.config['runlist'][self.era]}"
                    )
                    exit()
        return runlist

    def setup_env(self, not_hlt_version = False):
        self.console.rule("Setting up main CMSSW")
        os.system(
            f"bash scripts/UL_checkouts/checkout_UL_{self.era}.sh {self.cmssw_versions['main']}"
        )
        if not not_hlt_version:
            self.console.rule("Setting up HLT CMSSW ")
            os.system(
                f"bash scripts/UL_checkouts/checkout_UL_{self.era}.sh {self.cmssw_versions['hlt']}"
            )

    def run_production(self):
        self.console.rule(f"Running production for - {self.era} - {self.run}")
        configlist = [f"{self.name}/{run}.conf" for run in self.runs]
        # create script which runs grid control
        if self.no_tmux:
            self.console.rule("Using simple script")
            script = create_simple_grid_control_script(
                taskname=self.name,
                configlist=configlist,
                gc_path=self.gc_path,
            )
        else:
            self.console.rule("Using tmux script")
            script = create_tmux_grid_control_script(
                taskname=self.name,
                configlist=configlist,
                gc_path=self.gc_path,
                tmux_path=self.config["tmux_path"],
            )
        # execute grid control script
        os.system(f"./{script}")


    # @classmethod
    def build_filelist(self):
        pass

    # @classmethod
    def publish_dataset(self):
        pass

    # @classmethod
    def upload_tarballs(self):
        pass

    def setup_path(self):
        if not os.path.exists(self.name):
            os.mkdir(self.name)
    # @classmethod
    def build_generator_fragment(self):
        pass

    # @classmethod
    def build_python_configs(self):
        pass

    # @classmethod
    def build_gc_configs(self):
        pass


    def copy_file(
        self,
        in_file_name,
        copy_from_folder=None,
        add_fragment_to_end=[],
        skip_if_not_there=False,
        overwrite=False,
        replace_dict={},
    ):
        if not copy_from_folder:
            copy_from_folder = self.inputfolder
            
        in_file_path = os.path.join(copy_from_folder, in_file_name)
        filename = os.path.basename(in_file_name)

        if skip_if_not_there and not os.path.isfile(in_file_path):
            return False
        
        with open(in_file_path, "r") as in_file:
            file_str = in_file.read()

        if os.path.isfile(self.name + "/" + filename) and not overwrite:
            return True
        for fragment in add_fragment_to_end:
            file_str += "\n" + fragment
        for replace in replace_dict:
            file_str = file_str.replace(replace, replace_dict[replace])

        with open(self.name + "/" + filename, "w") as out_file:
            out_file.write(file_str)
        return True

    def setup_cmsRun(self):
        self.setup_path()
        self.build_generator_fragment()
        self.build_python_configs()
        self.build_gc_configs()
        self.console.log("--> Done ")
