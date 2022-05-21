import os
from rich.console import Console
from rich.progress import Progress
import argparse

console = Console()


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


class Filelist(object):
    def __init__(self, configdir, era, grid_control_path, run, finalstate, isMC):
        self.configdir = configdir
        self.era = era
        self.grid_control_path = grid_control_path
        self.run = run
        self.finalstate = finalstate
        self.isMC = isMC
        if isMC:
            self.datatype = "mc"
        else:
            self.datatype = "data"

    @classmethod
    def build_filelist():
        pass

    @classmethod
    def publish_dataset():
        pass


class PreselectionFilelist(Filelist):
    def build_filelist(self, config_path=None):
        console.rule("Generating Preselection filelist")
        if not os.path.exists("dbs/ul/"):
            os.mkdir("dbs/ul/")
        gc_config_folder = os.path.join(
            "{configdir}/{datatype}_{era}_preselection".format(
                datatype=self.datatype, configdir=self.configdir, era=self.era
            )
        )
        gc_config_path = os.path.join(
            gc_config_folder, "{run}.conf".format(run=self.run)
        )
        output_file = "dbs/ul/{output}.dbs".format(output=self.run)
        if config_path is not None:
            gc_config_path = config_path
        cmd = "{gc_path}/scripts/dataset_list_from_gc.py {config} -o {output}".format(
            gc_path=self.grid_control_path,
            config=gc_config_path,
            output=output_file,
        )
        console.log("Running {}".format(cmd))
        os.system(cmd)
        return os.path.abspath(output_file)

    def publish_dataset(self):
        console.log("We don't want to publish the preselection dataset ....")


class NanoFilelist(Filelist):
    def build_filelist(self, config_path=None):
        console.rule("Generating NanoAOD filelist")
        folder = "dbs/ul_embedding_nano/"
        if not os.path.exists(folder):
            os.mkdir(folder)
        gc_config_folder = os.path.join(
            "{configdir}/{datatype}_{era}_{finalstate}_nanoaod".format(
                datatype=self.datatype,
                finalstate=self.finalstate,
                configdir=self.configdir,
                era=self.era,
            )
        )
        gc_config_path = os.path.join(
            gc_config_folder, "{run}.conf".format(run=self.run)
        )
        output_file = os.path.join(
            folder,
            "{output}_{finalstate}.dbs".format(
                output=self.run, finalstate=self.finalstate
            ),
        )
        if config_path is not None:
            gc_config_path = config_path
        cmd = "{gc_path}/scripts/dataset_list_from_gc.py {config} -o {output}".format(
            gc_path=self.grid_control_path,
            config=gc_config_path,
            output=output_file,
        )
        console.log("Running {}".format(cmd))
        os.system(cmd)
        return os.path.abspath(output_file)

    def publish_dataset(self):
        console.log("To be implemented ")


class AggregatedMiniAODFilelist(Filelist):
    def build_filelist(self, config_path=None):
        console.rule("Generating Aggregated MiniAOD filelist")
        folder = "dbs/ul_embedding_aggregated_miniaod/"
        if not os.path.exists(folder):
            os.mkdir(folder)
        gc_config_folder = os.path.join(
            "{configdir}/{datatype}_{era}_{finalstate}_aggregate_miniAOD".format(
                datatype=self.datatype,
                configdir=self.configdir,
                era=self.era,
                finalstate=self.finalstate,
            )
        )
        gc_config_path = os.path.join(
            gc_config_folder, "{run}.conf".format(run=self.run)
        )
        output_file = os.path.join(
            folder,
            "{output}_{finalstate}.dbs".format(
                output=self.run, finalstate=self.finalstate
            ),
        )
        if config_path is not None:
            gc_config_path = config_path
        cmd = "{gc_path}/scripts/dataset_list_from_gc.py {config} -o {output}".format(
            gc_path=self.grid_control_path,
            config=gc_config_path,
            output=output_file,
        )
        console.log("Running {}".format(cmd))
        os.system(cmd)
        return os.path.abspath(output_file)

    def publish_dataset(self):
        console.log("To be implemented ")


class FullFilelist(Filelist):
    def build_filelist(self, config_path=None):
        self.import_root()
        console.rule("Generating Full filelist")
        folder = "dbs/ul_embedding/"
        if not os.path.exists(folder):
            os.mkdir(folder)
        gc_config_folder = os.path.join(
            "{configdir}/{finalstate}_{datatype}_{era}".format(
                datatype=self.datatype,
                finalstate=self.finalstate,
                configdir=self.configdir,
                era=self.era,
            )
        )
        gc_config_path = os.path.join(
            gc_config_folder, "{run}.conf".format(run=self.run)
        )
        temp_output_file = os.path.join(
            folder,
            "{output}_{finalstate}_temp.dbs".format(
                output=self.run, finalstate=self.finalstate
            ),
        )
        if config_path is not None:
            gc_config_path = config_path
        cmd = "{gc_path}/scripts/dataset_list_from_gc.py {config} -o {output}".format(
            gc_path=self.grid_control_path,
            config=gc_config_path,
            output=temp_output_file,
        )
        console.log("Running {}".format(cmd))
        os.system(cmd)
        # now we have the filelist, we have to open each file and check the event content by hand
        output_file = os.path.join(
            folder,
            "{output}_{finalstate}.dbs".format(
                output=self.run, finalstate=self.finalstate
            ),
        )
        data = {}
        data["files"] = {}
        with open(temp_output_file, "r") as f:
            lines = f.readlines()
            num_lines = len(lines) - 4
            print("Checking {} files".format(num_lines))
            with Progress() as progress:
                task = progress.add_task(
                    "[red]Reading number of events from files...", total=num_lines
                )
                prefix = ""
                for i, line in enumerate(lines):
                    if i < 4:
                        if line.startswith("["):
                            data["header"] = line.strip("\n")
                        if line.startswith("prefix"):
                            prefix, se_list = fix_prefix(
                                line.replace("prefix = ", "").strip("\n")
                            )
                            data["prefix"] = prefix
                            data["se_list"] = se_list
                        if line.startswith("nickname"):
                            data["nickname"] = line.replace("nickname = ", "").strip(
                                "\n"
                            )
                        if line.startswith("events"):
                            data["events"] = 0
                    else:
                        filename = line.split(("="))[0].strip()
                        filepath = prefix + "/" + filename
                        if not filepath.endswith(".root"):
                            continue
                        nevents = self.get_number_of_events(filepath)
                        data["files"][filename] = nevents
                        data["events"] += nevents
                        progress.advance(task)
        with open(output_file, "w") as output:
            output.write(data["header"] + "\n")
            output.write("nickname = {}\n".format(data["nickname"]))
            output.write("events = {}\n".format(data["events"]))
            output.write("se list = {}\n".format(data["se_list"]))
            prefix = data["prefix"][data["prefix"].find("/store") :]
            output.write("prefix = {}\n".format(prefix))
            for filename, nevents in data["files"].items():
                output.write("{} = {}\n".format(filename, nevents))
        console.rule("{} generated ".format(output_file))
        os.remove(temp_output_file)

    def get_number_of_events(self, filepath):
        import ROOT

        ROOT.gErrorIgnoreLevel = 6001
        file = ROOT.TFile.Open(filepath, "READ")
        tree = file.Get("Events")
        return tree.GetEntries()

    def import_root(self):
        console.log("Trying to import ROOT")
        try:
            import ROOT
        except ImportError:
            console.log(
                "ROOT cannot be found, please source some lcg stack including ROOT and python3, e.g."
            )
            console.log(
                "source /cvmfs/sft.cern.ch/lcg/views/LCG_97python3/x86_64-centos7-gcc9-opt/setup.sh"
            )
            exit()
        console.log("ROOT imported ..")

    def publish_dataset(self):
        # TODO
        pass


if __name__ == "__main__":
    print("Hello")
    console.log("Running in script mode")
    parser = argparse.ArgumentParser(description="Generate filelist for embedding")
    parser.add_argument("--config", type=str, help="path to the config", required=True)
    parser.add_argument("--era", type=str, help="era", required=True)
    parser.add_argument("--run", type=str, help="run", required=True)
    parser.add_argument("--finalstate", type=str, help="finalstate", required=True)
    parser.add_argument("--isMc", action="store_true", help="is is mc, set this")
    args = parser.parse_args()
    grid_control_path = os.path.join("grid-control")
    filelist = FullFilelist(
        args.config,
        args.era,
        grid_control_path,
        args.run,
        args.finalstate,
        args.isMc,
    )
    filelist.build_filelist(config_path=args.config)
