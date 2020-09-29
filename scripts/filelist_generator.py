import os


class Filelist():
    def __init__(self, workdir, era, finalstate, run):
        self.workdir = workdir
        self.era = era
        self.finalstate = finalstate
        self.run = run

    @classmethod
    def build_filelist():
        pass

    @classmethod
    def publish_dataset():
        pass


class PreselectionFilelist(Filelist):
    def build_filelist(self):
        gc_config_folder = os.path("{workdir}/preselection_data_{era}".format(
            workdir=self.workdir, era=self.era))
        gc_config_path = os.path.join(gc_config_folder,
                                      "{run}.conf".format(run=self.run))
        output_file = "{output}_preselection.dbs".format(output=self.run)
        cmd = "dataset_list_from_gc.py {config} -o {output}".format(
            config=gc_config_path,
            output=output_file,
        )
        print(cmd)
        os.system(cmd)

        return os.path.abspath(output_file)

    def publish_dataset(self):
        print("We don't want to publish the preselection dataset ....")


class FullFilelist(Filelist):
    def build_filelist(self):
        # TODO
        pass

    def publish_dataset(self):
        # TODO
        pass
