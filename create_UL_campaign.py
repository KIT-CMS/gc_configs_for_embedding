#!/usr/bin/env python
from src.arg_parser import parser
import os
import stat
import yaml
import sys

if sys.version_info[0] == 2:
    print("You need to run this with Python 3")
    raise SystemExit

from scripts.EmbeddingTask import (
    Preselection,
    FullTask,
    Nano,
    aggregateMiniAOD,
    PuppiOnMini,
)
from create_grid_control_script import create_tmux_while
from scripts.filelist_generator import (
    PreselectionFilelist,
    FullFilelist,
    NanoFilelist,
    AggregatedMiniAODFilelist,
    PuppiOnMiniFilelist,
)
import getpass
from rich.console import Console


console = Console()


def possible_runs(era):
    config = yaml.load(open("scripts/ul_config.yaml", "r"))
    runlist = config["runlist"][era]
    return runlist


def get_inputfolder(era):
    if era == "2018":
        return "Run2018_CMSSW_10_6_28_UL"
    elif era == "2017":
        return "Run2017_CMSSW_10_6_28_UL"
    elif era == "2016":
        return "Run2016_CMSSW_10_6_28_UL"
    elif era == "2016-HIPM":
        return "Run2016-HIPM_CMSSW_10_6_28_UL"
    else:
        raise ValueError("Era not supported")


class Task(object):
    def __init__(
        self,
        era,
        workdir,
        configdir,
        config,
        backend,
        run,
        user,
        no_tmux=False,
        isMC=False,
    ):
        self.era = era
        self.workdir = workdir
        self.config = config
        self.configdir = configdir
        self.isMC = isMC
        self.runlist = self.validate_run(run)
        self.gc_path = os.path.abspath("grid-control")
        self.backend = backend
        self.no_tmux = no_tmux
        self.cmssw_versions = {
            "main": self.config["cmssw_version"][self.era]["main"],
            "hlt": self.config["cmssw_version"][self.era]["hlt"],
        }
        self.identifier = "data_{}".format(self.era)
        if isMC:
            self.identifier = "mc_{}".format(self.era)
        if args.user:
            self.username = args.user
        else:
            self.username = getpass.getuser()

    def run_production(self):
        console.rule(
            "Running production for - {era} - {run}".format(
                era=self.era, run=self.runlist
            )
        )
        configlist = []
        for run in self.runlist:
            configlist.append(
                "{name}/{run}.conf".format(name=self.task.get_name(), run=run)
            )
        if self.no_tmux:
            console.rule("Using old script")
            out_file = open("{name}/while.sh".format(name=self.task.get_name()), "w")
            out_file.write("#!/bin/bash\n")
            out_file.write("\n")
            out_file.write("touch .lock\n")
            out_file.write("\n")
            out_file.write('while [ -f ".lock" ]\n')
            out_file.write("do\n")
            for config in configlist:
                out_file.write(
                    "python2 {gc_path}/go.py {configpath} -G \n".format(
                        gc_path=self.gc_path, configpath=config
                    )
                )
            out_file.write('echo "rm .lock"\n')
            out_file.write("sleep 2\n")
            out_file.write("done\n")
            out_file.close()
            os.chmod("{name}/while.sh".format(name=self.task.get_name()), stat.S_IRWXU)
            os.system("./{name}/while.sh".format(name=self.task.get_name()))
        else:
            console.rule("Using tmux version")
            script = create_tmux_while(
                taskname=self.task.get_name(),
                configlist=configlist,
                gc_path=self.gc_path,
                tmux_path=self.config["tmux_path"],
            )
            os.system("./{}".format(script))

    def setup_env(self):
        console.rule("Setting up main CMSSW")
        os.system(
            "bash scripts/UL_checkouts/checkout_UL_{ERA}.sh {VERSION}".format(
                ERA=self.era, VERSION=self.cmssw_versions["main"]
            )
        )

        console.rule("Setting up HLT CMSSW ")
        os.system(
            "bash scripts/UL_checkouts/checkout_UL_{ERA}_HLT.sh {VERSION}".format(
                ERA=self.era, VERSION=self.cmssw_versions["hlt"]
            )
        )

    def validate_run(self, run):
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
                    console.log(
                        "Run name unknown: Known runs are: {}".format(
                            self.config["runlist"][self.era]
                        )
                    )
                    exit()
        return runlist

    @classmethod
    def build_filelist(self):
        pass

    @classmethod
    def publish_dataset(self):
        pass

    @classmethod
    def setup_cmsRun(self):
        pass

    @classmethod
    def upload_tarballs(self):
        pass


class PreselectionTask(Task):
    def __init__(
        self, era, workdir, configdir, config, backend, run, user, no_tmux, isMC
    ):
        Task.__init__(
            self, era, workdir, configdir, config, backend, run, user, no_tmux, isMC
        )
        self.task = Preselection(
            era=self.era,
            workdir=self.workdir,
            identifier=self.identifier,
            runs=self.runlist,
            user=self.username,
            inputfolder=get_inputfolder(era),
            config=self.config,
            isMC=self.isMC,
            input_samples=self.config["input_samples"][self.era],
        )

    def build_filelist(self):
        for run in self.runlist:
            filelist = PreselectionFilelist(
                configdir=self.configdir,
                era=self.era,
                grid_control_path=self.gc_path,
                run=run,
                finalstate="preselection",
                isMC=self.isMC,
            )
            filelist.build_filelist()

    def setup_cmsRun(self):
        self.task.setup_all()

    def upload_tarballs(self):
        console.log("Not needed for preselection --> Exiting ")

    def publish_dataset(self):
        console.log("Ne need to publish preselection datasets --> Exiting")


class AggregateMiniAODTask(Task):
    def __init__(
        self,
        era,
        workdir,
        configdir,
        config,
        backend,
        run,
        user,
        finalstate,
        no_tmux,
        isMC,
    ):
        Task.__init__(
            self, era, workdir, configdir, config, backend, run, user, no_tmux, isMC
        )
        self.finalstate = finalstate
        self.task = aggregateMiniAOD(
            era=self.era,
            finalstate=self.finalstate,
            workdir=self.workdir,
            identifier=self.identifier,
            runs=self.runlist,
            user=self.username,
            inputfolder=get_inputfolder(era),
            config=self.config,
            isMC=self.isMC,
        )

    def build_filelist(self):
        for run in self.runlist:
            filelist = AggregatedMiniAODFilelist(
                configdir=self.configdir,
                era=self.era,
                grid_control_path=self.gc_path,
                run=run,
                finalstate=self.finalstate,
                isMC=self.isMC,
            )
            filelist.build_filelist()

    def setup_cmsRun(self):
        self.task.setup_all()

    def upload_tarballs(self):
        console.log("Not needed for preselection --> Exiting ")

    def publish_dataset(self):
        console.log("To be implemented ...")


class PuppiOnMiniTask(Task):
    def __init__(
        self,
        era,
        workdir,
        configdir,
        config,
        backend,
        run,
        user,
        finalstate,
        no_tmux,
        isMC,
    ):
        Task.__init__(
            self, era, workdir, configdir, config, backend, run, user, no_tmux, isMC
        )
        self.finalstate = finalstate
        self.task = PuppiOnMini(
            era=self.era,
            finalstate=self.finalstate,
            workdir=self.workdir,
            identifier=self.identifier,
            runs=self.runlist,
            user=self.username,
            inputfolder=get_inputfolder(era),
            config=self.config,
            isMC=self.isMC,
        )

    def build_filelist(self):
        for run in self.runlist:
            filelist = PuppiOnMiniFilelist(
                configdir=self.configdir,
                era=self.era,
                grid_control_path=self.gc_path,
                run=run,
                finalstate=self.finalstate,
                isMC=self.isMC,
            )
            filelist.build_filelist()

    def setup_cmsRun(self):
        self.task.setup_all()

    def upload_tarballs(self):
        console.log("Not needed for preselection --> Exiting ")

    def publish_dataset(self):
        console.log("To be implemented ...")


class NanoTask(Task):
    def __init__(
        self,
        era,
        workdir,
        configdir,
        config,
        backend,
        run,
        user,
        finalstate,
        no_tmux,
        isMC,
    ):
        Task.__init__(
            self, era, workdir, configdir, config, backend, run, user, no_tmux, isMC
        )
        self.finalstate = finalstate
        self.task = Nano(
            era=self.era,
            finalstate=self.finalstate,
            workdir=self.workdir,
            identifier=self.identifier,
            runs=self.runlist,
            user=self.username,
            inputfolder=get_inputfolder(era),
            config=self.config,
            isMC=self.isMC,
        )

    def build_filelist(self):
        for run in self.runlist:
            filelist = NanoFilelist(
                configdir=self.configdir,
                era=self.era,
                grid_control_path=self.gc_path,
                run=run,
                finalstate=self.finalstate,
                isMC=self.isMC,
            )
            filelist.build_filelist()

    def setup_cmsRun(self):
        self.task.setup_all()

    def upload_tarballs(self):
        console.log("Not needed for preselection --> Exiting ")

    def publish_dataset(self):
        console.log("To be implemented ...")


class EmbeddingTask(Task):
    def __init__(
        self,
        era,
        workdir,
        configdir,
        config,
        backend,
        run,
        user,
        finalstate,
        no_tmux,
        isMC,
    ):
        Task.__init__(
            self, era, workdir, configdir, config, backend, run, user, no_tmux, isMC
        )
        self.finalstate = finalstate
        self.task = FullTask(
            finalstate=self.finalstate,
            era=self.era,
            workdir=self.workdir,
            identifier=self.identifier,
            runs=self.runlist,
            user=self.username,
            inputfolder=get_inputfolder(era),
            config=self.config,
            isMC=self.isMC,
            backend=self.backend,
        )

    def build_filelist(self):
        for run in self.runlist:
            filelist = FullFilelist(
                configdir=self.configdir,
                era=self.era,
                grid_control_path=self.gc_path,
                run=run,
                finalstate=self.finalstate,
                isMC=self.isMC,
            )
            filelist.build_filelist()

    def publish_dataset(self):
        console.log("Implementation to be done")

    def setup_cmsRun(self):
        self.task.setup_all()

    def upload_tarballs(self):
        console.rule("building tarball...")
        for version in self.cmssw_versions.values():
            outputfile = "cmssw_{VERSION}.tar.gz".format(VERSION=version)
            cmd = "tar --dereference -czf {FILE} {CMSSW_FOLDER}/*".format(
                FILE=outputfile,
                CMSSW_FOLDER=version,
            )
            console.log(cmd)
            os.system(cmd)
            console.log("finished building tarball...")
            console.log("upload tarball...")
            cmd = "gfal-copy -f {outputfile} {tarballpath}/{TARBALLNAME}".format(
                outputfile=outputfile,
                tarballpath=config["output_paths"]["tarballs"].replace(
                    "{USER}", self.username
                ),
                TARBALLNAME=outputfile,
            )
            os.system(cmd)
            console.log(cmd)
            console.rule("finished uploading tarball...")


if __name__ == "__main__":
    # Get command-line arguments:
    # workdir
    # era
    # final-state
    # run
    # mode
    # task
    # backend
    # custom-configdir
    # mc
    # no_tmux
    # user
    args = parser.parse_args()
    # load config which contains details about the different LHC runs
    config = yaml.safe_load(open("src/ul_config.yaml", "r"))

    # first setup CMSSW environments
    params = [
        args.era,
        args.workdir,
        args.custom_configdir,
        config,
        args.backend,
        args.run,
        args.user,
        args.no_tmux,
        args.mc,
    ]
    # The following choices are possible: "preselection", "full", "aggregate", "rerunpuppi", "nanoaod"
    if args.mode == "preselection":
        task = PreselectionTask(*params)
    elif args.mode == "nanoaod":
        task = NanoTask(*params)
    elif args.mode == "aggregate":
        task = AggregateMiniAODTask(*params)
    elif args.mode == "rerunpuppi":
        task = PuppiOnMiniTask(*params)
    elif args.mode == "full":
        task = EmbeddingTask(*params)
    else:
        parser.error(f"The mode {args.mode} doesn't exist.")

    # Run the specific tasks
    # The following choices are possible:
    # "setup_cmssw",
    # "upload_tarballs",
    # "setup_jobs",
    # "run_production",
    # "create_filelist",
    # "publish_dataset",
    if args.task == "setup_cmssw":
        task.setup_env()
    elif args.task == "upload_tarballs":
        task.upload_tarballs()
    elif args.task == "run_production":
        if args.final_state is None:
            raise ValueError("Final state not specified")
        if args.run is None:
            raise ValueError("run not specified")
        task.run_production()
    elif args.task == "create_filelist":
        if args.final_state is None:
            raise ValueError("Final state not specified")
        if args.run is None:
            raise ValueError("run not specified")
        task.build_filelist()
    elif args.task == "setup_jobs":
        if args.final_state is None:
            raise ValueError("Final state not specified")
        if args.run is None:
            raise ValueError("run not specified")
        if args.workdir == "":
            console.log(
                "No workdir is set, please specify the workdir using --workdir /path/to/workdir"
            )
            raise Exception
        task.setup_cmsRun()
    elif args.task == "publish_dataset":
        if args.final_state is None:
            raise ValueError("Final state not specified")
        task.publish_dataset()
    else:
        exit()
