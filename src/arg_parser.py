"""
This file contains all different command-line parsers. 
Different Tasks need different command-line arguments which gives us the need for different parsers.#

A command-line parsers reads the arguments from the command-line and parses them with the argparse library.
For more information see: https://docs.python.org/3/library/argparse.html
To use it, import the parser and call
```python
    from src.arg_parser import parser 
    args = parser.parse_args()
```
to get an object with the arguments.
"""
import argparse
import os
from helpers import setup_cmssw

parser = argparse.ArgumentParser(
    description="Setup Grid Control for Embedding Production"
)
# This allows us to specify different subparsers for different commands fiven in the command-line
subparsers = parser.add_subparsers()

# parser_setup_cmssw = subparsers.add_parser("setup_cmssw")
# parser_setup_cmssw.set_defaults(func=setup_cmssw)

parser_preselection = subparsers.add_parser("preselection")

parser_full = subparsers.add_parser("full")

parser_aggregate = subparsers.add_parser("aggregate")

parser_rerunpuppi = subparsers.add_parser("rerunpuppi")

parser_nanoaod = subparsers.add_parser("nanoaod")

parser_publish_dataset = subparsers.add_parser("publish_dataset")

parser.add_argument("--workdir", type=str, help="path to the workdir", default="")
parser.add_argument(
    "--era",
    type=str,
    # choices=['2016_preVFP', '2016_postVFP', '2017', '2018'],
    choices=["2016-HIPM", "2016", "2017", "2018"],
    required=True,
    help="Era used for the production",
)
parser.add_argument(
    "--final-state",
    type=str,
    required=False,
    default="NotSet",
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
    choices=["preselection", "full", "aggregate", "rerunpuppi", "nanoaod"],
    help="Select preselection mode, full embedding mode, aggregate mode, rerun puppi mode, or nanoaod mode",
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
    default=os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
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

