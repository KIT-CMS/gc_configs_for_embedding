import argparse
import json
import subprocess

xootd_prefix = "root://cms-xrd-global.cern.ch/"
parser = argparse.ArgumentParser(
    description="This scipt can be used, to generate a grid control compatible filelist from das"
)

parser.add_argument("--nick", required=True, help="Name of the dataset")
parser.add_argument("--query", required=True, help="DAS query of the dataset")
parser.add_argument(
    "--phys03",
    action="store_true",
    help="If set, phys03 instance is used instead of global",
)
parser.add_argument(
    "--gridka-red",
    action="store_true",
    help="If set, the gridka redicator root://cmsxrootd-redirectors.gridka.de/ is used directly. Default: {}".format(
        xootd_prefix
    ),
)
parser.add_argument("--outputfile", help="output file")


def read_filelist_from_das(nick, query, outputfile, phys03, xootd_prefix):
    print("Getting filelist for \n  Nick: {}".format(nick))
    filedict = {}
    das_query = f"file dataset={query}"
    if phys03:
        das_query += " instance=prod/phys03"
    else:
        das_query += " instance=prod/global"
    print(f"  DAS Query: {das_query}")
    cmd = f"/cvmfs/cms.cern.ch/common/dasgoclient --query '{das_query}' --json"
    output = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
    jsonS = output.communicate()[0]
    filelist = json.loads(jsonS)
    for file in filelist:
        filedict[file["file"][0]["name"]] = file["file"][0]["nevents"]
    print(f"  Total files:  {len(filedict.keys())} \n  Total events: {sum(filedict.values())}")

    with  open(outputfile, "w") as outfile:
        outfile.write("[{}] \n".format(nick))
        outfile.write("nickname = {} \n".format(nick))
        for file in filedict.keys():
            outfile.write(
                "{prefix}/{path} = {nevents} \n".format(
                    prefix=xootd_prefix, path=file, nevents=filedict[file]
                )
            )


if __name__ == "__main__":
    args = parser.parse_args()
    if args.gridka_red:
        xootd_prefix = "root://cmsxrootd-redirectors.gridka.de/"
    read_filelist_from_das(
        args.nick, args.query, args.outputfile, args.phys03, xootd_prefix
    )
