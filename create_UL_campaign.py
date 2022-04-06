#!/usr/bin/env python
import argparse
import os
import stat
import yaml
import sys

if sys.version_info[0] == 2:
    print("You need to run this with Python 3")
    raise SystemExit

from scripts.EmbeddingTask import Preselection, FullTask, Nano, aggregateMiniAOD
from scripts.create_tmux_while import create_tmux_while
from scripts.filelist_generator import (
    PreselectionFilelist,
    FullFilelist,
    NanoFilelist,
    AggregatedMiniAODFilelist,
)
import getpass
from rich.console import Console


console = Console()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Setup Grid Control for Embedding Production"
    )
    parser.add_argument("--workdir", type=str, help="path to the workdir", default="")
    parser.add_argument(
        "--era",
        type=str,
        # choices=['2016_preVFP', '2016_postVFP', '2017', '2018'],
        choices=["2017", "2018"],
        required=True,
        help="Era used for the production",
    )
    parser.add_argument(
        "--final-state",
        type=str,
        required=False,
        choices=["MuTau", "ElTau", "ElMu", "TauTau", "MuEmb", "ElEmb"],
        help="Name the final state you want to process",
    )
    parser.add_argument(
        "--run",
        type=str,
        nargs="+",
        help="Name or list of the runs you want to process, use all to process all runs of an era",
    )
    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=["preselection", "full", "aggregate", "nanoaod"],
        help="Select preselection mode, full embedding mode, aggregate mode, or nanoaod mode",
    )
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        choices=[
            "setup_cmssw",
            "upload_tarballs",
            "setup_jobs",
            "run_production",
            "create_filelist",
            "publish_dataset",
        ],
        help="Different commands that are possible",
    )
    parser.add_argument(
        "--backend",
        type=str,
        choices=["etp", "naf", "lxplus"],
        default="etp",
        help="Select the condor backend that is used.",
    )
    parser.add_argument(
        "--custom-configdir",
        type=str,
        help="If this is set, use the configdir from the given folder",
    )
    parser.add_argument(
        "--mc",
        action="store_true",
        help="If this is set, mc embedding is run instead of data embedding",
    )
    parser.add_argument(
        "--no_tmux",
        action="store_true",
        help="If this is set, no tmux is used to run the jobs",
    )
    parser.add_argument(
        "--user",
        type=str,
        default="",
        help="if you have a different username on NAF and ETP you have to choose your ETP username here",
    )
    return parser.parse_args()


def possible_runs(era):
    config = yaml.load(open("scripts/ul_config.yaml", "r"))
    runlist = config["runlist"][era]
    return runlist


def get_inputfolder(era):
    if era == "2018":
        return "Run2018_CMSSW_10_6_28_UL"
    elif era == "2017":
        return "Run2017_CMSSW_10_6_28_UL"
    elif era == "2016_postVFP":
        return "Run2016_CMSSW_10_6_28_UL_postVFP"
    elif era == "2016_preVFP":
        return "Run2016_CMSSW_10_6_28_UL_preVFP"
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
    args = parse_arguments()
    config = yaml.safe_load(open("scripts/ul_config.yaml", "r"))
    if args.final_state is None:
        finalstate = "NotSet"
    else:
        finalstate = args.final_state
    if args.custom_configdir:
        configdir = args.custom_configdir
    else:
        configdir = os.path.dirname(os.path.realpath(__file__))
    # first setup CMSSW environments
    if args.mode == "preselection":
        task = PreselectionTask(
            args.era,
            args.workdir,
            configdir,
            config,
            args.backend,
            args.run,
            args.user,
            args.no_tmux,
            args.mc,
        )
    elif args.mode == "nanoaod":
        task = NanoTask(
            args.era,
            args.workdir,
            configdir,
            config,
            args.backend,
            args.run,
            args.user,
            finalstate,
            args.no_tmux,
            args.mc,
        )
    elif args.mode == "aggregate":
        task = AggregateMiniAODTask(
            args.era,
            args.workdir,
            configdir,
            config,
            args.backend,
            args.run,
            args.user,
            finalstate,
            args.no_tmux,
            args.mc,
        )
    else:
        task = EmbeddingTask(
            args.era,
            args.workdir,
            configdir,
            config,
            args.backend,
            args.run,
            args.user,
            finalstate,
            args.no_tmux,
            args.mc,
        )
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
