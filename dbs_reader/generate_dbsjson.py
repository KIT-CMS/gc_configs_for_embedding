#!/usr/bin/env python
import pprint
import argparse

from yaml import events
from dbs.apis.dbsClient import DbsApi
import uuid
import os
import yaml
import subprocess
import json
import numpy as np
from multiprocessing import Pool, current_process, RLock
from tqdm import tqdm

import ROOT


def fix_prefix(prefix):
    if "srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN" in prefix:
        se_list = "cmssrm-kit.gridka.de"
        prefix = prefix.replace(
            "srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only",
            "root://cmsxrootd-kit.gridka.de/",
        )
    else:
        raise Exception("Unknown prefix")
    return prefix, se_list


def getlumi(file):
    output = subprocess.check_output("edmLumisInFiles.py {}".format(file),
                                     shell=True)
    lumidict = json.loads(output)
    outputdata = []
    for run in lumidict:
        for lumirange in lumidict[run]:
            lumilow = lumirange[0]
            lumihigh = lumirange[1]
            for lumi in xrange(lumilow, lumihigh + 1):
                outputdata.append({
                    "lumi_section_num": lumi,
                    "run_num": int(run)
                })
    return outputdata


def get_file_information(filepath):
    # print("Reading file: %s" % filepath)
    ROOT.gErrorIgnoreLevel = 6001
    file = ROOT.TFile.Open(filepath, "READ")
    tree = file.Get("Events")
    data = {}
    data["nentries"] = int(tree.GetEntries())
    data["file_size"] = int(file.GetSize())
    data["check_sum"] = "NULL"
    data["lumis"] = getlumi(filepath)
    return data


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script to generate json for DBS3 upload")
    parser.add_argument("--gc-config",
                        type=str,
                        help="path to the grid-control config",
                        required=True)
    parser.add_argument("--era", type=str, help="era", required=True)
    parser.add_argument("--run", type=str, help="run", required=True)
    parser.add_argument(
        "--publish-config",
        type=str,
        required=True,
        help="path to the configuration settings for publishing datasets",
        default="",
    )
    parser.add_argument(
        "--final-state",
        type=str,
        required=True,
        choices=["MuTau", "ElTau", "ElMu", "TauTau", "MuEmb", "ElEmb"],
        help="Name the final state from the config",
    )
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        choices=["prepare", "publish", "test_publish"],
        help="Name the task to be performed",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=12,
        help="Number of threads to be used",
    )
    return parser.parse_args()


def createEmptyBlock(ds_info, origin_site_name, blockid):

    acquisition_era_config = {"acquisition_era_name": "CRAB", "start_date": 0}
    processing_era_config = {
        "processing_version": 1,
        "description": ds_info["description"],
    }
    primds_config = {
        "primary_ds_type": ds_info["primary_ds_type"],
        "primary_ds_name": ds_info["primary_ds"],
    }

    dataset = "/%s/%s/%s" % (
        ds_info["primary_ds"],
        ds_info["processed_ds"],
        ds_info["tier"],
    )

    dataset_config = {
        "physics_group_name": ds_info["group"],
        "dataset_access_type": "VALID",
        "data_tier_name": ds_info["tier"],
        "processed_ds_name": ds_info["processed_ds"],
        "dataset": dataset,
    }

    block_name = "%s#%s" % (dataset, blockid)
    block_config = {
        "block_name": block_name,
        "origin_site_name": origin_site_name,
        "open_for_writing": 0,
    }

    dataset_conf_list = [{
        "app_name": ds_info["application"],
        "global_tag": ds_info["global_tag"],
        "output_module_label": ds_info["output_module_label"],
        "pset_hash": "dummyhash",
        "release_version": ds_info["app_version"],
    }]

    blockDict = {
        "files": [],
        "processing_era": processing_era_config,
        "primds": primds_config,
        "dataset": dataset_config,
        "dataset_conf_list": dataset_conf_list,
        "acquisition_era": acquisition_era_config,
        "block": block_config,
        "file_parent_list": [],
        "file_conf_list": [],
    }
    return blockDict


def addFilesToBlock(blockDict, files):
    blockDict["files"] = files
    blockDict["block"]["file_count"] = len(files)
    blockDict["block"]["block_size"] = sum(
        [int(file["file_size"]) for file in files])
    return blockDict


def generate_filelist(temp_output_file, gc_config_path, grid_control_path):
    cmd = "{gc_path}/scripts/dataset_list_from_gc.py {config} -o {output}".format(
        gc_path=grid_control_path,
        config=gc_config_path,
        output=temp_output_file,
    )
    print("Running {}".format(cmd))
    os.system(cmd)


def generate_dataset_info(publish_configpath, era, run, final_state,
                          outputfile):
    # INFORMATION TO BE PUT IN DBS3
    config = yaml.load(open(publish_configpath, "r"))[era]
    # almost free text here, but beware WMCore/Lexicon.py
    dataset_info = {
        "primary_ds": config["primary_ds"].format(run=run),
        "processed_ds": config["processed_ds"].format(final_state=final_state),
        "tier": config["tier"],
        "group": config["group"],
        "campaign_name": config["campaign_name"],
        "application": config["application"],
        "app_version": config["app_version"],
        "description": config["description"],
        "primary_ds_type": config["primary_ds_type"],
        "global_tag": config["global_tag"],
        "output_module_label": config["output_module_label"],
    }
    json.dump(dataset_info, open(outputfile, "w"))


def readout_file_information(
    gc_filelist,
    task_begin_index,
    task_end_index,
    outputfolder,
    offset,
    prefix,
    tasknumber,
):
    # worker id
    worker_id = current_process()._identity[0]
    outputfile = os.path.join(outputfolder, "temp",
                              "file_details_{}.json".format(tasknumber))
    if os.path.exists(outputfile):
        print("File {} already exists".format(outputfile))
        return
    data = {}
    files = []
    with open(gc_filelist, "r") as f:
        lines = f.readlines()
        total = task_end_index - task_begin_index
        with tqdm(
                total=total,
                position=worker_id,
                desc="Task {}".format(tasknumber),
                dynamic_ncols=True,
                leave=False,
        ) as bar:
            for lineindex in xrange(task_begin_index + offset,
                                    task_end_index + offset):
                line = lines[lineindex]
                filename = line.split(("="))[0].strip()
                filepath = prefix + "/" + filename
                if not filepath.endswith(".root"):
                    continue
                fileinfo = get_file_information(filepath)
                aFile = {
                    "name": filepath.replace("root://cmsxrootd-kit.gridka.de/",
                                             ""),
                    "event_count": fileinfo["nentries"],
                    "file_size": fileinfo["file_size"],
                    "check_sum": fileinfo["check_sum"],
                    "lumis": fileinfo["lumis"],
                    "adler32": "deadbeef",
                }
                files.append(aFile)
                bar.update(1)
    data[tasknumber] = files
    json.dump(data, open(outputfile, "w"))


def job_wrapper(args):
    return readout_file_information(*args)


def generate_file_json(file_info_file, outputfolder, gc_filelist, nthreads,
                       blocksize):
    offset = 4
    num_files = 0
    prefix = ""
    with open(gc_filelist, "r") as f:
        lines = f.readlines()
        num_files = len(lines) - offset
        print("Checking {} files".format(num_files))
        prefix = ""
        for i, line in enumerate(lines):
            if i < 4:
                if line.startswith("prefix"):
                    prefix, _ = fix_prefix(
                        line.replace("prefix = ", "").strip("\n"))
            else:
                break
    ntasks = int(num_files / float(blocksize)) + 1
    files = range(num_files)
    jobtasks = np.array_split(files, ntasks)
    arguments = [(
        gc_filelist,
        min(jobtasks[i]),
        max(jobtasks[i] + 1),
        outputfolder,
        offset,
        prefix,
        i,
    ) for i in range(ntasks)]
    if nthreads > len(arguments):
        nthreads = len(arguments)
    print("Running {} tasks with {} threads".format(len(arguments), nthreads))
    pool = Pool(nthreads, initargs=(RLock(), ), initializer=tqdm.set_lock)
    for _ in tqdm(
            pool.imap_unordered(job_wrapper, arguments),
            total=len(arguments),
            desc="Total progess",
            position=nthreads + 1,
            dynamic_ncols=True,
            leave=True,
    ):
        pass
    # result = pool.map(job_wrapper, arguments)
    pool.close()
    pool.join()
    print("Done generating file information")
    # merge all json files into a single one
    combined = {}
    combined["blocks"] = []
    for i in range(ntasks):
        result = json.loads(
            open(
                os.path.join(outputfolder, "temp",
                             "file_details_{}.json".format(i)),
                "r",
            ).read())
        block = {
            "blockid": str(uuid.uuid4()),
            "files": result[str(i)],
        }
        combined["blocks"].append(block)
    json.dump(combined, open(file_info_file, "w"), indent=4)
    print("Finished preparing dbs for {} blocks...".format(
        len(combined["blocks"])))
    # generate file indicating that the filelist is complete
    open(os.path.join(outputfolder, "scanned"), "a").close()


def upload_to_dbs(dataset_info_file,
                  file_info_file,
                  origin_site_name,
                  dry=False):
    print("Uploading to DBS3...")
    with open(dataset_info_file, "r") as f:
        dataset_info = json.loads(f.read())
    with open(file_info_file, "r") as f:
        file_info = json.loads(f.read())
    phy3WriteUrl = "https://cmsweb.cern.ch/dbs/prod/phys03/DBSWriter"
    writeApi = DbsApi(url=phy3WriteUrl, debug=1)
    total_files = 0
    total_events = 0
    print("insert block in DBS3: %s" % writeApi.url)
    print("Preparing upload for {}".format(dataset_info["processed_ds"]))
    print("Blocks to be processed: {}".format(len(file_info["blocks"])))
    print("DatasetName: {}".format(
        createEmptyBlock(dataset_info, origin_site_name,
                         "asdf")["dataset"]["dataset"]))
    for block in file_info["blocks"]:
        blockid = block["blockid"]
        filedata = block["files"]
        filelist = []
        print("Processing block {} - Number of files: {}".format(
            blockid, len(filedata)))
        total_files += len(filedata)
        blockDict = createEmptyBlock(dataset_info, origin_site_name, blockid)
        for file in filedata:
            fileDic = {}
            lfn = file["name"]
            fileDic["file_type"] = "EDM"
            fileDic["logical_file_name"] = lfn
            for key in ["check_sum", "adler32", "file_size", "event_count"]:
                fileDic[key] = file[key]
            total_events += file["event_count"]
            fileDic["file_lumi_list"] = file["lumis"]
            fileDic["auto_cross_section"] = 0.0
            fileDic["last_modified_by"] = "sbrommer"
            filelist.append(fileDic)
        # now upload the block
        blockDict = addFilesToBlock(blockDict, filelist)
        if not dry:
            writeApi.insertBulkBlock(blockDict)
        else:
            print("Dry run, not inserting block into DBS3")
            pprint.pprint(blockDict)
            exit()
    print("Total files: {} // Total Events: {}".format(total_files,
                                                       total_events))


if __name__ == "__main__":
    blocksize = 500
    origin_site_name = "T1_DE_KIT"
    args = parse_arguments()

    # first create the folders
    sample = "{}_Embedding_{}_{}".format(args.era, args.final_state, args.run)
    sample_publish_folder = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "publishdb", sample)
    # if not existent, create the gc_filelist which contains all the output filepaths
    gc_filelist = os.path.join(sample_publish_folder,
                               "gc_{}_filelist.txt".format(sample))
    if not os.path.exists(sample_publish_folder):
        os.makedirs(sample_publish_folder)
    if not os.path.exists(os.path.join(sample_publish_folder, "temp")):
        os.makedirs(os.path.join(sample_publish_folder, "temp"))
    if not os.path.exists(gc_filelist):
        print("Creating gc filelist for {}".format(sample))
        grid_control_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "..", "grid-control")
        generate_filelist(gc_filelist, args.gc_config, grid_control_path)
    # create the dataset_info.json file if not existent
    dataset_info_file = os.path.join(sample_publish_folder,
                                     "dataset_info.json")
    file_info_file = os.path.join(sample_publish_folder, "file_info.json")
    if not os.path.exists(dataset_info_file):
        generate_dataset_info(args.publish_config, args.era, args.run,
                              args.final_state, dataset_info_file)
    if args.task == "prepare":
        print("Preparing dataset")
        if not os.path.exists(os.path.join(sample_publish_folder, "scanned")):
            # now we have to parse all the different files and create the block json
            generate_file_json(
                file_info_file,
                sample_publish_folder,
                gc_filelist,
                nthreads=args.threads,
                blocksize=blocksize,
            )
        else:
            print("Dataset already prepared")
    elif args.task == "publish":
        # now we have to upload the dataset to DBS3
        if not os.path.exists(os.path.join(sample_publish_folder, "scanned")):
            print("Dataset not prepared yet")
            exit()
        else:
            print("Uploading dataset to DBS3")
            upload_to_dbs(dataset_info_file, file_info_file, origin_site_name)
    elif args.task == "test_publish":
        # now we have to upload the dataset to DBS3
        if not os.path.exists(os.path.join(sample_publish_folder, "scanned")):
            print("Dataset not prepared yet")
            exit()
        else:
            print("Uploading dataset to DBS3")
            upload_to_dbs(dataset_info_file,
                          file_info_file,
                          origin_site_name,
                          dry=True)
