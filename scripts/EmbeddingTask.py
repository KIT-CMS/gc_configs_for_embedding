import os, stat, yaml, getpass
from scripts.read_filelist_from_das import read_filelist_from_das
from shutil import copyfile
from rich.console import Console

console = Console()


class GeneralTask:
    def __init__(self, era, workdir, identifier, runs, inputfolder, config, isMC):
        self.config = config
        self.inputfolder = inputfolder
        self.runs = runs
        self.workdir = workdir
        self.identifier = identifier
        self.era = era
        self.name = ""
        self.username = getpass.getuser()
        if isMC:
            self.datatype = "mc"
        else:
            self.datatype = "data"

    @classmethod
    def build_generator_fragment():
        pass

    @classmethod
    def build_python_configs():
        pass

    @classmethod
    def build_gc_configs():
        pass

    def setup_path(self):
        if not os.path.exists(self.name):
            os.mkdir(self.name)

    def get_name(self):
        return self.name

    def copy_file(
        self,
        in_file_name,
        copy_from_folder=None,
        add_fragment_to_end=[],
        skip_if_not_there=False,
        overwrite=False,
        replace_dict={},
    ):
        if not copy_from_folder:
            copy_from_folder = self.inputfolder
        if skip_if_not_there and not os.path.isfile(
            copy_from_folder.rstrip("/") + "/" + in_file_name
        ):
            return False
        in_file = open(copy_from_folder.rstrip("/") + "/" + in_file_name, "r")
        filename = os.path.basename(in_file_name)
        file_str = in_file.read()
        in_file.close()
        if os.path.isfile(self.name + "/" + filename) and not overwrite:
            return True
        for fragment in add_fragment_to_end:
            file_str += "\n" + fragment
        for replace in replace_dict:
            file_str = file_str.replace(replace, replace_dict[replace])
        out_file = open(self.name + "/" + filename, "w")
        out_file.write(file_str)
        out_file.close()
        return True

    def setup_all(self):
        self.setup_path()
        self.build_generator_fragment()
        self.build_python_configs()
        self.build_gc_configs()
        console.log("--> Done ")


class Preselection(GeneralTask):
    def __init__(self, era, workdir, identifier, runs, inputfolder, config, isMC):
        GeneralTask.__init__(
            self, era, workdir, identifier, runs, inputfolder, config, isMC
        )
        self.preselection = True
        self.finalstate = "preselection"
        self.particle_to_embed = "preselection"
        self.cmsRun_order = ["preselection.py"]
        self.name = identifier + "_preselection"
        self.cmssw_version = self.config["cmssw_version"][era]["main"]

    def build_generator_fragment(self):
        console.log("No generator fragment needed for preselection")

    def build_python_configs(self):
        console.log("Setting up python configs")
        add_fragment_to_end = []
        with open("scripts/customise_for_gc.py", "r") as (function_to_add):
            add_fragment_to_end.append(function_to_add.read())
        add_fragment_to_end.append("process = customise_for_gc(process)")
        self.copy_file(
            self.cmsRun_order[0],
            add_fragment_to_end=add_fragment_to_end,
            skip_if_not_there=True,
        )

    def build_gc_configs(self):
        console.log("Setting up gc configs")
        for run in self.runs:
            self.write_gc_config("grid_control_preselection.conf", run)

        rp_base_cfg = {}
        rp_base_cfg["__CMSRUN_ORDER__"] = "config file = preselection.py"
        se_path_str = ("se path = {path}").format(
            path=self.config["output_paths"]["preselection"].replace(
                "{USER}", self.username
            )
        )
        se_output_pattern_str = (
            "se output pattern = "
            + "preselection"
            + "_"
            + self.identifier
            + "/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@"
        )
        rp_base_cfg["__CMSSW_BASE__"] = os.path.join(
            os.path.dirname(os.path.abspath(self.cmssw_version)),
            self.cmssw_version + "/",
        )
        rp_base_cfg["__SE_PATH__"] = se_path_str
        rp_base_cfg["__SE_OUTPUT_PATTERN__"] = se_output_pattern_str
        rp_base_cfg[
            "__partition_lfn_modifier__"
        ] = "partition lfn modifier = <xrootd:nrg>"
        rp_base_cfg["__SE_OUTPUT_FILE__"] = "se output files = PreRAWskimmed.root"
        self.copy_file(
            "scripts/base_configs/grid_control_preselection.conf",
            copy_from_folder="./",
            replace_dict=rp_base_cfg,
        )

    def write_gc_config(self, outfile, run):
        out_file = open(self.name + "/" + run + ".conf", "w")
        out_file.write("[global]\n")
        out_file.write(("include={}\n").format(outfile))
        if "etp.kit.edu" in os.environ["HOSTNAME"] and self.workdir == "":
            workdir = ("/work/{user}/embedding/UL/gc_workdir").format(
                user=os.environ["USER"]
            )
        elif "naf" in os.environ["HOSTNAME"] and self.workdir == "":
            workdir = ("/nfs/dust/cms/user/{user}/embedding/gc_workdir").format(
                user=os.environ["USER"]
            )
        else:
            workdir = self.workdir
        out_file.write(
            ("workdir = {WORKDIR}/{particle_to_embed}_{name}\n").format(
                WORKDIR=workdir,
                particle_to_embed=self.particle_to_embed,
                name=out_file.name.split(".")[0],
            )
        )
        out_file.write("[CMSSW]\n")
        dbs_name = ("/DoubleMuon/{RUN}-v1/RAW").format(RUN=run)
        filelistname = "DoubleMuon_{run}_RAW.dbs".format(name=self.name, run=run)
        read_filelist_from_das(
            "{particle}_{name}_DoubleMuon_{run}".format(
                particle=self.particle_to_embed, name=self.name, run=run
            ),
            dbs_name,
            "{name}/{filelistname}".format(name=self.name, filelistname=filelistname),
            False,
            "root://cms-xrd-global.cern.ch/",
        )
        out_file.write(
            (
                "dataset = {particle}_{name}_DoubleMuon_{run} : list:{filelistname} \n"
            ).format(
                particle=self.particle_to_embed,
                name=self.name,
                run=run,
                filelistname=filelistname,
            )
        )
        out_file.close()


class Nano(GeneralTask):
    def __init__(
        self, era, workdir, finalstate, identifier, runs, inputfolder, config, isMC
    ):
        GeneralTask.__init__(
            self, era, workdir, identifier, runs, inputfolder, config, isMC
        )
        self.nanoaod = True
        self.finalstate = finalstate
        self.particle_to_embed = config["finalstate_map"][finalstate][
            "embeddedParticle"
        ]
        self.cmsRun_order = ["embedding_nanoaod.py"]
        self.name = identifier + "_nanoaod"
        self.cmssw_version = self.config["cmssw_version"][era]["main"]

    def build_generator_fragment(self):
        console.log("No generator fragment needed for nanoaod task")

    def build_python_configs(self):
        console.log("Setting up python configs")
        add_fragment_to_end = []
        with open("scripts/customise_for_gc.py", "r") as (function_to_add):
            add_fragment_to_end.append(function_to_add.read())
        add_fragment_to_end.append("process = customise_for_gc(process)")
        self.copy_file(
            self.cmsRun_order[0],
            add_fragment_to_end=add_fragment_to_end,
            skip_if_not_there=True,
        )

    def build_gc_configs(self):
        console.log("Setting up gc configs")
        for run in self.runs:
            self.write_gc_config(
                "grid_control_nanoaod.conf".format(datatype=self.datatype),
                run,
            )

        rp_base_cfg = {}
        rp_base_cfg["__CMSRUN_ORDER__"] = "config file = embedding_nanoaod.py"
        se_path_str = ("se path = {path}").format(
            path=self.config["output_paths"]["nanoaod"].replace("{USER}", self.username)
        )
        se_output_pattern_str = (
            "se output pattern = "
            + "nanoaod"
            + "_"
            + self.identifier
            + "/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@"
        )
        rp_base_cfg["__CMSSW_BASE__"] = os.path.join(
            os.path.dirname(os.path.abspath(self.cmssw_version)),
            self.cmssw_version + "/",
        )
        rp_base_cfg["__SE_PATH__"] = se_path_str
        rp_base_cfg["__SE_OUTPUT_PATTERN__"] = se_output_pattern_str
        rp_base_cfg[
            "__partition_lfn_modifier__"
        ] = "partition lfn modifier = <xrootd:nrg>"
        rp_base_cfg["__SE_OUTPUT_FILE__"] = "se output files = merged_nano.root"
        self.copy_file(
            "scripts/base_configs/grid_control_nanoaod.conf",
            copy_from_folder="./",
            replace_dict=rp_base_cfg,
        )

    def write_gc_config(self, outfile, run):
        out_file = open(self.name + "/" + run + ".conf", "w")
        out_file.write("[global]\n")
        out_file.write(("include={}\n").format(outfile))
        if "etp.kit.edu" in os.environ["HOSTNAME"] and self.workdir == "":
            workdir = ("/work/{user}/embedding/UL/gc_workdir").format(
                user=os.environ["USER"]
            )
        elif "naf" in os.environ["HOSTNAME"] and self.workdir == "":
            workdir = ("/nfs/dust/cms/user/{user}/embedding/gc_workdir").format(
                user=os.environ["USER"]
            )
        else:
            workdir = self.workdir
        out_file.write(
            ("workdir = {WORKDIR}/{particle_to_embed}_{name}\n").format(
                WORKDIR=workdir,
                particle_to_embed=self.particle_to_embed,
                name=out_file.name.split(".")[0],
            )
        )
        out_file.write("[CMSSW]\n")
        dbs_folder = "dbs/ul_embedding"
        inputfile = os.path.join(dbs_folder, "{}_{}.dbs".format(run, self.finalstate))
        filelist_location = os.path.join(self.name, os.path.basename(inputfile))
        copyfile(inputfile, filelist_location)
        out_file.write(
            ("dataset = {particle}_{name}_{run} : list:{filelistname} \n").format(
                particle=self.particle_to_embed,
                name=self.name,
                run=run,
                filelistname=os.path.basename(filelist_location),
            )
        )
        out_file.close()


class FullTask(GeneralTask):
    def __init__(
        self, era, workdir, finalstate, identifier, runs, inputfolder, config, isMC
    ):
        GeneralTask.__init__(
            self, era, workdir, identifier, runs, inputfolder, config, isMC
        )
        self.preselection = False
        self.finalstate = finalstate
        self.particle_to_embed = config["finalstate_map"][finalstate][
            "embeddedParticle"
        ]
        self.cmsRun_order = [
            "selection.py",
            "lheprodandcleaning.py",
            "generator_preHLT.py",
            "generator_HLT.py",
            "generator_postHLT.py",
            "merging.py",
        ]
        self.name = self.finalstate + "_" + identifier
        self.generator_frag = self.build_generator_fragment()
        self.cmssw_version = self.config["cmssw_version"][era]["main"]

    def build_generator_fragment(self):
        generator_frag = ""
        cuts = self.config["generator_cuts"][self.era][self.finalstate]
        naming_map = self.config["finalstate_map"][self.finalstate]
        cutstring = (
            "({LEP1}.Pt > {LEP1_PT_CUT} && {LEP2}.Pt > {LEP2_PT_CUT} && {LEP1}.Eta < {LEP1_ETA_CUT} && {LEP2}.Eta < {LEP2_ETA_CUT})"
        ).format(
            LEP1=naming_map["lep1_name"],
            LEP2=naming_map["lep2_name"],
            LEP1_PT_CUT=cuts["lep1_pt"],
            LEP2_PT_CUT=cuts["lep2_pt"],
            LEP1_ETA_CUT=cuts["lep1_eta"],
            LEP2_ETA_CUT=cuts["lep2_eta"],
        )
        if self.finalstate == "ElMu":
            cutstring += (
                "|| ({LEP1}.Pt > {LEP2_PT_CUT} && {LEP2}.Pt > {LEP1_PT_CUT} && {LEP1}.Eta < {LEP2_ETA_CUT} && {LEP2}.Eta < {LEP1_ETA_CUT})"
            ).format(
                LEP1=naming_map["lep1_name"],
                LEP2=naming_map["lep2_name"],
                LEP1_PT_CUT=cuts["lep1_pt"],
                LEP2_PT_CUT=cuts["lep2_pt"],
                LEP1_ETA_CUT=cuts["lep1_eta"],
                LEP2_ETA_CUT=cuts["lep2_eta"],
            )
            generator_frag += (
                "process.generator.HepMCFilter.filterParameters.{CHANNEL}Cut = cms.string('{CUTSTRING}')"
            ).format(CHANNEL=naming_map["name"], CUTSTRING=cutstring)
        else:
            generator_frag += (
                "process.generator.HepMCFilter.filterParameters.{CHANNEL}Cut = cms.string('{CUTSTRING}')"
            ).format(CHANNEL=naming_map["name"], CUTSTRING=cutstring)
        generator_frag += "\n"
        generator_frag += (
            "process.generator.HepMCFilter.filterParameters.Final_States=cms.vstring('{CHANNEL}')"
        ).format(CHANNEL=naming_map["name"])
        generator_frag += (
            "\nprocess.generator.nAttempts = cms.uint32({ATTEMPTS})"
        ).format(ATTEMPTS=cuts["attempts"])
        return generator_frag

    def build_python_configs(self):
        for i, file_to_copy in enumerate(self.cmsRun_order):
            add_fragment_to_end = []
            if i == 0:
                with open("scripts/customise_for_gc.py", "r") as (function_to_add):
                    add_fragment_to_end.append(function_to_add.read())
                add_fragment_to_end.append("process = customise_for_gc(process)")
            else:
                add_fragment_to_end.append(
                    "####@FILE_NAMES@, @SKIP_EVENTS@, @MAX_EVENTS@"
                )
            if file_to_copy in (
                "lheprodandcleaning.py",
                "generator_preHLT.py",
                "generator_postHLT.py",
                "generator_HLT.py",
            ):
                add_fragment_to_end.append(
                    "from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper"
                )
                add_fragment_to_end.append(
                    "randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)"
                )
                add_fragment_to_end.append("randSvc.populate()")
                add_fragment_to_end.append(
                    'print("Generator random seed: %s" % process.RandomNumberGeneratorService.generator.initialSeed)'
                )
                if file_to_copy == "generator_preHLT.py":
                    add_fragment_to_end.append(self.generator_frag)
            if file_to_copy == "lheprodandcleaning.py":
                if self.particle_to_embed == "MuEmbedding":
                    add_fragment_to_end.append(
                        "process.externalLHEProducer.particleToEmbed = cms.int32(13)"
                    )
                if self.particle_to_embed == "ElEmbedding":
                    add_fragment_to_end.append(
                        "process.externalLHEProducer.particleToEmbed = cms.int32(11)"
                    )
            if file_to_copy == "merging.py" and "2016" not in self.identifier:
                if "Run201" in self.inputfolder:
                    add_fragment_to_end.append(
                        "from TauAnalysis.MCEmbeddingTools.customisers import customiseKeepPrunedGenParticles"
                    )
                    add_fragment_to_end.append(
                        "process = customiseKeepPrunedGenParticles(process)"
                    )
            self.copy_file(
                file_to_copy,
                add_fragment_to_end=add_fragment_to_end,
                skip_if_not_there=True,
            )
            self.copy_file("../scripts/base_configs/full_embedding.sh")
            os.chmod("{path}/full_embedding.sh".format(path=self.name), stat.S_IRWXU)

    def build_gc_configs(self):
        dbs_folder = "dbs/ul"
        inputdata = {}
        for run in self.runs:
            inputfile = dbs_folder + "/" + run + ".dbs"
            inputdata = {}
            inputdata["nfiles"] = 0
            if os.path.exists(inputfile):
                console.log("Using filelist from {}".format(inputfile))
                with open(inputfile, "r") as (file):
                    for line in file.readlines():
                        if "se list" in line:
                            if "gridka" in line:
                                inputdata[
                                    "selist"
                                ] = "root://cmsxrootd-kit.gridka.de:1094"
                            else:
                                inputdata["selist"] = line.split(" = ")[1].strip("\n")
                        if "prefix" in line:
                            inputdata["prefix"] = line.split(" = ")[1].strip("\n")
                        if ".root =" in line:
                            inputdata["nfiles"] += 1

            else:
                console.log(
                    "{} could not be found in folder {}. Please run preselection".format(
                        inputfile, dbs_folder
                    )
                )
                exit()
            if os.path.exists(self.name + "/" + run + ".conf"):
                console.log("Moving existing config to grid_control_ul_main.conf.bak")
                copyfile(
                    os.path.join(self.name, "grid_control_ul_main.conf"),
                    os.path.join(self.name, "grid_control_ul_main.conf.bak"),
                )
            self.write_gc_config("grid_control_ul_main.conf", run, inputdata)
        rp_base_cfg = {}
        se_path_str = ("se path = {path}").format(
            path=self.config["output_paths"]["main"].replace("{USER}", self.username)
        )
        se_output_pattern_str = (
            "se output pattern = "
            + "main"
            + "_"
            + self.identifier
            + "/@NICK@/@XBASE@_@GC_JOB_ID@.@XEXT@"
        )
        rp_base_cfg["__CMSSW_BASE__"] = os.path.join(
            os.path.dirname(os.path.abspath(self.cmssw_version)),
            self.cmssw_version + "/",
        )
        rp_base_cfg["__SE_PATH__"] = se_path_str
        rp_base_cfg["__SE_OUTPUT_PATTERN__"] = se_output_pattern_str
        rp_base_cfg[
            "__partition_lfn_modifier__"
        ] = "partition lfn modifier = <xrootd:nrg>"
        rp_base_cfg["__SE_OUTPUT_FILE__"] = "se output files = merged.root"
        rp_base_cfg["__CMSSW_MAIN__"] = self.config["cmssw_version"][self.era]["main"]
        rp_base_cfg["__CMSSW_HLT__"] = self.config["cmssw_version"][self.era]["hlt"]
        rp_base_cfg["__TARBALL_PATH__"] = self.config["output_paths"][
            "tarballs"
        ].replace("{USER}", self.username)
        rp_base_cfg["__EXE__"] = os.path.join(
            os.path.dirname(os.path.abspath("scripts")),
            "scripts/base_configs/embedding_wrapper.sh",
        )
        self.copy_file(
            "scripts/base_configs/grid_control_ul_main.conf",
            copy_from_folder="./",
            replace_dict=rp_base_cfg,
        )

    def write_gc_config(self, outfile, run, inputdata):
        out_file = open(self.name + "/" + run + ".conf", "w")
        out_file.write("[global]\n")
        out_file.write(("include={}\n").format(outfile))
        if "etp.kit.edu" in os.environ["HOSTNAME"] and self.workdir == "":
            workdir = ("/work/{user}/embedding/UL/gc_workdir").format(
                user=os.environ["USER"]
            )
        elif "naf" in os.environ["HOSTNAME"] and self.workdir == "":
            workdir = ("/nfs/dust/cms/user/{user}/embedding/gc_workdir").format(
                user=os.environ["USER"]
            )
        else:
            workdir = self.workdir
        out_file.write(
            ("workdir = {WORKDIR}/{particle_to_embed}_{name}\n").format(
                WORKDIR=workdir,
                particle_to_embed=self.particle_to_embed,
                name=out_file.name.split(".")[0],
            )
        )
        out_file.write("[constants]\n")
        out_file.write(
            "INPUTPATH = " + inputdata["selist"] + "/" + inputdata["prefix"] + "\n"
        )
        out_file.write(
            "NICK = {particle_to_embed}_{finalstate}_{run}\n".format(
                particle_to_embed=self.particle_to_embed,
                finalstate=self.finalstate,
                run=run,
            )
        )
        out_file.write("[parameters]\n")
        out_file.write(("FILENUMBER = range(0,{max})").format(max=inputdata["nfiles"]))
        out_file.close()
