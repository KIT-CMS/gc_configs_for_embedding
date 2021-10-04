import argparse
import os
import subprocess
import enquiries
from shutil import copyfile
from rich.console import Console

console = Console()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Setup Grid Control for Embedding Production"
    )
    parser.add_argument(
        "--inputfile", type=str, help="path to the inputfile", default=""
    )
    parser.add_argument(
        "--embedding-scripts-folder",
        "--e",
        type=str,
        required=True,
        help="path to the folder containing the scripts",
    )
    parser.add_argument(
        "--workdir",
        type=str,
        default="/ceph/sbrommer/embedding/UL/studies/",
        help="path to the workdir",
    )
    parser.add_argument(
        "--workdirtag", type=str, required=True, help="tag for the workdir"
    )
    parser.add_argument(
        "--events", type=int, default=-1, help="number of events to process"
    )
    parser.add_argument(
        "--run-all", action="store_true", help="if set, all tasks will be run"
    )
    parser.add_argument(
        "--run-preselection", action="store_true", help="if set, all tasks will be run"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=8,
        help="set the number of threads to be used by cmsRun",
    )

    return parser.parse_args()


embedding_order = [
    "selection.py",
    "lheprodandcleaning.py",
    "generator_preHLT.py",
    "generator_HLT.py",
    "generator_postHLT.py",
    "merging.py",
]

if __name__ == "__main__":
    args = parse_arguments()
    workdir = os.path.join(os.path.abspath(args.workdir), args.workdirtag)
    inputfile = os.path.abspath(args.inputfile)
    emb_folder = os.path.abspath(args.embedding_scripts_folder)
    main_cmssw = os.path.abspath("CMSSW_10_6_28")
    hlt_cmssw = os.path.abspath("CMSSW_10_2_16_UL")
    start_index = 0
    tasks = embedding_order
    if args.run_preselection:
        if "preselection.py" in os.listdir(emb_folder):
            tasks = ["preselection.py"]
            start_index = 0
        else:
            console.print("preselection.py not found in embedding folder")
            raise FileNotFoundError
    else:
        if not args.run_all:
            starttask = enquiries.choose("Pick tasks to start with", embedding_order)
            start_index = embedding_order.index(starttask)
            tasks = embedding_order[start_index:]
    console.rule("Starting to run embedding")
    console.log("Running {}".format(tasks))
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    for i, filename in enumerate(tasks):
        # we have to change the number of events directly in the script,
        # and therefore parse the selection config, replacing the events line
        modified_input = False
        if i == 0:
            with open(os.path.join(emb_folder, filename), "r") as f:
                lines = f.readlines()
            with open(os.path.join(workdir, filename), "w") as f:
                for line in lines:
                    if (
                        "fileNames = cms.untracked.vstring(" in line
                        and modified_input is False
                    ):
                        f.write(
                            "    fileNames = cms.untracked.vstring('file:{}'),\n".format(
                                inputfile
                            )
                        )
                        modified_input = True
                    elif "input = cms.untracked.int32(-1)" in line:
                        console.log("Reducing output to {} events".format(args.events))
                        f.write(
                            "   input = cms.untracked.int32({})\n".format(args.events)
                        )
                    else:
                        f.write(line)
        else:
            copyfile(
                os.path.join(emb_folder, filename), os.path.join(workdir, filename)
            )
    # now run the stuff using the provided script
    if args.run_preselection:
        copyfile(
            os.path.join("scripts", "analysis_scripts", "minimal_preselection.sh"),
            os.path.join(workdir, "minimal_embedding.sh"),
        )
    else:
        copyfile(
            os.path.join("scripts", "analysis_scripts", "minimal_embedding.sh"),
            os.path.join(workdir, "minimal_embedding.sh"),
        )
    console.log("Using inputfile {}".format(inputfile))
    console.log("Using workdir {}".format(workdir))
    console.rule("Setup finished")
    commands = [
        "bash",
        "minimal_embedding.sh",
        main_cmssw,
        hlt_cmssw,
        inputfile,
        str(start_index),
        str(args.threads),
    ]
    p = subprocess.Popen(commands, cwd=workdir)

    (output, err) = p.communicate()

    # This makes the wait possible
    p_status = p.wait()

    console.log("Results can be found in {}".format(workdir))
    console.rule("Done")
