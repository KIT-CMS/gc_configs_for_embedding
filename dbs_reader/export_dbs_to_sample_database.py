import argparse
from configparser import ConfigParser
import glob
import json
import os
import re
import shutil
import tempfile


SUB_RUNS = {
    "2017": ["B", "C", "D", "E", "F"],
    "2018": ["A", "B", "C", "D"],
}


EMBEDDING_TYPES = {
    "ElTau": "TauEmbedding-ElTauFinalState",
    "MuTau": "TauEmbedding-MuTauFinalState",
    "TauTau": "TauEmbedding-TauTauFinalState",
    "ElMu":"TauEmbedding-ElMuFinalState",
    "MuEmb": "MuonEmbedding",
    "ElEmb": "ElectronEmbedding",
}


DBS_FILE_NAME_PATTERN = re.compile(r"^Run(\d+)(\w)_(\w+)\.dbs$")


def create_argument_parser():
    parser = argparse.ArgumentParser()

    # add command-line arguments

    parser.add_argument(
        "--database-path",
        type=str,
        required=True,
        help="path to the root directory of the sample database (clone of https://github.com/KIT-CMS/KingMaker_sample_database)",
    )

    parser.add_argument(
        "--data-tier",
        type=str,
        required=True,
        help="data tier of the embedding production, for which filelists are exported; valid choices: 'aggregated_miniaod', 'nanoaod'; default: 'nanoaod'",
    )

    # TODO add 2016 eras
    parser.add_argument(
        "--era",
        type=str,
        required=True,
        choices=["2017", "2018"],
        help="data-taking era; valid choices: '2017', '2018'",
    )

    parser.add_argument(
        "--sub-run",
        nargs="*",
        type=str,
        choices=["A", "B", "C", "D", "E", "F"],
        help="sub-runs of the data-taking era; valid choices: letters 'B' to 'F' for 2017 and 'A' to 'D' for 2018; default: all sub-runs of the corresponding era",
    )

    parser.add_argument(
        "--final-state",
        nargs="*",
        type=str,
        choices=["ElTau", "MuTau", "TauTau", "ElMu", "MuEmb", "ElEmb"],
        help="final state of the embedding samples; valid choices: 'ElTau', 'MuTau', 'TauTau', 'ElMu', 'MuEmb', 'ElEmb'",
    )

    parser.add_argument(
        "--redirector",
        type=str,
        default="root://cmsxrootd-kit-disk.gridka.de/",
        help="base URI of the XRootD redirector; default: 'root://cmsxrootd-kit-disk.gridka.de/",
    )

    return parser


def get_sanitized_arguments(parser):
    namespace = parser.parse_args()

    # get the path to the sample database, check for existence
    database_path = os.path.abspath(namespace.database_path)
    if not os.path.exists(database_path):
        raise FileNotFoundError("path {} does not exist".format(database_path))
    
    # get the era, which has already been validated by the parser
    era = namespace.era

    # use all sub-runs if none have been chosen explicitly via command line, otherwise check if selected sub-runs are
    # valid for considered era
    sub_runs = namespace.sub_run
    if sub_runs is None:
        sub_runs = SUB_RUNS[era]
    else:
        for sub_run in sub_runs:
            if sub_run not in SUB_RUNS[era]:
                raise RuntimeError("data-taking era {} has no sub-run {}".format(era, sub_run))

    # use all final state if none have been chosen explicitly via command line
    final_states = namespace.final_state
    if final_states is None:
        final_states = ["ElTau", "MuTau", "TauTau", "ElMu", "MuEmb", "ElEmb"]

    return {
        "database_path": database_path,
        "data_tier": namespace.data_tier,
        "era": namespace.era,
        "sub_runs": sub_runs,
        "final_states": final_states,
        "redirector": namespace.redirector,
    }


def get_selected_dbs_files(data_tier, era, sub_runs, final_states):

    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dbs")
    dbs_file_paths = None
    if data_tier == "nanoaod":
        dbs_file_paths = glob.glob(os.path.join(base_path, "ul_embedding_nano", "*.dbs"))
    elif data_tier == "aggregated_miniaod":
        dbs_file_paths = glob.glob(os.path.join(base_path, "ul_embedding_aggregated_miniaod", "*.dbs"))
    else:
        raise RuntimeError("unknown data tier '{}'".format(data_tier))

    # categorize files with regard to three attributes: era, run and final state
    for dbs_file_path in dbs_file_paths:
        m = DBS_FILE_NAME_PATTERN.match(os.path.basename(dbs_file_path))
        if m is None:
            continue

        # get era, sub-run and final state information from parsed regex
        era_dbs = m.group(1)
        sub_run_dbs = m.group(2)
        final_state_dbs = m.group(3)

        # yield file information if all checks are successful
        if (era == era_dbs) and (sub_run_dbs in sub_runs) and (final_state_dbs in final_states):
            dbs = ConfigParser()
            dbs.read(dbs_file_path)
            section = dbs.sections()[0]
            yield era_dbs, sub_run_dbs, final_state_dbs, dbs[section]


def create_sample_database_entry(era, sub_run, final_state, dbs, redirector):

    # get file information in DBS key-value pairs
    prefix = dbs["prefix"]
    uris = []
    for k in dbs.keys():
        if re.match("^\d+\/.*\.root$", k):
            uris.append(redirector + os.path.join(prefix, k))

    # get the data-taking year (cropping preVFP and postVFP for 2016 eras)
    year = int(era[0:4])

    # get number of events
    n_events = int(dbs["events"])

    # generate the new nick of the sample
    nick = "{}_Run{}{}-UL{}".format(EMBEDDING_TYPES[final_state], era, sub_run, era)

    # generate the entry
    return {
        "dbs": "/sample/not/published",
        "era": year,
        "filelist": uris,
        "generator_weight":  1.0,
        "nevents": n_events,
        "nfiles": len(uris),
        "nick":  nick,
        "sample_type": "embedding",
        "xsec":  1.0,
    }


if __name__ == "__main__":

    # invoke command-line argument parser
    parser = create_argument_parser()
    arguments = get_sanitized_arguments(parser)

    # save specific arguments as local variables
    database_path = arguments["database_path"]
    data_tier = arguments["data_tier"]
    era = arguments["era"]
    sub_runs = arguments["sub_runs"]
    final_states = arguments["final_states"]
    redirector = arguments["redirector"]

    # prepare sample database directory for embedding samples for specific era
    embedding_path = os.path.join(database_path, era, "embedding")
    if not os.path.exists(embedding_path):
        os.makedirs(embedding_path)

    # load the full sample database
    full_database_path = os.path.join(database_path, "datasets.json")
    with open(full_database_path, mode="r") as f:
        full_database = json.load(f)

    # iterate over DBS files, which fulfill all conditions concerning era, sub-runs and final states
    for _era, sub_run, final_state, dbs in get_selected_dbs_files(data_tier, era, sub_runs, final_states):

        # create the entry
        entry = create_sample_database_entry(_era, sub_run, final_state, dbs, redirector)

        # dump entry file temporarily and copy output file to sample database
        destination_path = os.path.join(database_path, _era, "embedding", "{}.json".format(entry["nick"]))
        with tempfile.NamedTemporaryFile(mode="w") as tmp_file:
            json.dump(entry, tmp_file, separators=(", ", ": "), indent=4)
            tmp_file.flush()
            shutil.copy(tmp_file.name, destination_path)
        
        # dump the entry without the filelist into the full filelist
        entry.pop("filelist")
        full_database[entry["nick"]] = (entry)

    # finally dump the modified full database into the original file
    with open(full_database_path, mode="w") as f:
        json.dump(full_database, f, separators=(",", ": "), indent=4)
