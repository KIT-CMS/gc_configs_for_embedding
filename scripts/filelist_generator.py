import os
import ROOT
from create_UL_campaign import console


def fix_prefix(prefix):
    if "srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN" in prefix:
        console.log("replaceing srm path with xrootd path ...")
        prefix = prefix.replace(
            "srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only",
            "root://cmsxrootd-kit.gridka.de/",
        )
    else:
        raise Exception("Unknown prefix")
    return prefix


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
    def build_filelist(self):
        console.rule("Generating filelist")
        if not os.path.exists("dbs/ul/"):
            os.mkdir("dbs/ul/")
        gc_config_folder = os.path.join(
            "{configdir}/{datatype}_{era}".format(
                datatype=self.datatype, configdir=self.configdir, era=self.era
            )
        )
        gc_config_path = os.path.join(
            gc_config_folder, "{run}.conf".format(run=self.run)
        )
        output_file = "dbs/ul/{output}.dbs".format(output=self.run)
        cmd = "{gc_path}/scripts/dataset_list_from_gc.py {config} -o {output}".format(
            gc_path=self.grid_control_path,
            config=gc_config_path,
            output=output_file,
        )
        os.system(cmd)
        return os.path.abspath(output_file)

    def publish_dataset(self):
        console.log("We don't want to publish the preselection dataset ....")


class NanoFilelist(Filelist):
    def build_filelist(self):
        console.rule("Generating filelist")
        folder = "dbs/ul_embedding_nano/"
        if not os.path.exists(folder):
            os.mkdir(folder)
        gc_config_folder = os.path.join(
            "{configdir}/{datatype}_{era}".format(
                datatype=self.datatype, configdir=self.configdir, era=self.era
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
        cmd = "{gc_path}/scripts/dataset_list_from_gc.py {config} -o {output}".format(
            gc_path=self.grid_control_path,
            config=gc_config_path,
            output=output_file,
        )
        os.system(cmd)
        return os.path.abspath(output_file)

    def publish_dataset(self):
        console.log("To be implemented ")


class FullFilelist(Filelist):
    def build_filelist(self):
        console.rule("Generating filelist")
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
        with open(output_file, "w") as output:
            with open(temp_output_file, "r") as f:
                prefix = ""
                for i, line in enumerate(f):
                    if i < 4:
                        if line.startswith("prefix"):
                            prefix = fix_prefix(line.strip("prefix = ").strip("\n"))
                        output.write(line)
                    else:
                        filename = line.split(("="))[0].strip()
                        filepath = prefix + "/" + filename
                        if not filepath.endswith(".root"):
                            continue
                        output.write(
                            "{file} = {events}".format(
                                file=filename,
                                events=self.get_number_of_events(filepath),
                            )
                        )

    def get_number_of_events(self, filepath):
        # console.log("Checking {}".format(filepath))
        file = ROOT.TFile.Open(filepath, "READ")
        tree = file.Get("Events")
        return tree.GetEntries()

    def publish_dataset(self):
        # TODO
        pass
