import os


class Filelist():
    def __init__(self, configdir, era, grid_control_path, run):
        self.configdir = configdir
        self.era = era
        self.grid_control_path = grid_control_path
        self.run = run

    @classmethod
    def build_filelist():
        pass

    @classmethod
    def publish_dataset():
        pass


class PreselectionFilelist(Filelist):
    def build_filelist(self):
        if not os.path.exists("dbs/ul/"):
            os.mkdir("dbs/ul/")
        gc_config_folder = os.path.join(
            "{configdir}/data_{era}_preselection".format(
                configdir=self.configdir, era=self.era))
        gc_config_path = os.path.join(gc_config_folder,
                                      "{run}.conf".format(run=self.run))
        output_file = "dbs/ul/{output}.dbs".format(output=self.run)
        cmd = "{gc_path}/scripts/dataset_list_from_gc.py {config} -o {output}".format(
            gc_path=self.grid_control_path,
            config=gc_config_path,
            output=output_file,
        )
        # print(cmd)
        os.system(cmd)
        return os.path.abspath(output_file)

    def publish_dataset(self):
        print("We don't want to publish the preselection dataset ....")


class FullFilelist(Filelist):
    def __init__(self, configdir, era, grid_control_path, run, finalstate):
        super().__init__(self, configdir, era, grid_control_path, run)
        self.finalstate = finalstate

    def build_filelist(self):
        # TODO
        pass

    def publish_dataset(self):
        # TODO
        pass
