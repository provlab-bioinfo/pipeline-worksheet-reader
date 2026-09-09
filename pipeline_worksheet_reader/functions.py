import io, tempfile, os
import pandas as pd
from pathlib import Path
from configparser import ConfigParser

class PipelineWorksheet:

    def __init__(self, path):
        if os.path.isdir(path):
            worksheets = [str(p) for p in Path(path).rglob("PipelineWorksheet.xlsx")]
            if (len(worksheets) > 1): # If more than 1 file is found
                raise Exception(f"More than one pipeline worksheet identified. Only 1 filename can contain 'PipelineWorksheet'. Found:\n{worksheets}.")
            path, *remainder = worksheets
        self.csv = tempfile.NamedTemporaryFile().name
        self.path = path
        df = pd.read_excel(path)        
        df.to_csv(self.csv, index=False)

    def __str__(self):
        msg = (
            f"Path: {Path(self.path).resolve()}\n"
            f"RunName: {self.getRunName()}\n"
            f"RunDir: {self.getRunDir()}\n\n"
            f"Pipelines\n"
            f"---------\n"
            f"{self.getPipelines().to_string(index=False)}\n\n"
            f"Directories\n"
            f"-----------\n"
            f"{self.getOutputDir().to_string(index=False)}\n\n"
            f"Samples\n"
            f"--------\n"
            f"{self.getSamples().to_string(index=False)}\n"
        )
        return (msg)

    def getDataVar(self:object, section:str) -> dict:
        """Generates a dictionary from the first two columns of a [HEADER] section
        :param section: The name of the section
        :return: A dictionary containing variable keys
        """    
        cfg = ConfigParser(allow_no_value=True)
        cfg.optionxform = str
        cfg.read(self.csv)
        dict = {k:v for k, *v in map(lambda x: str.split(x,sep=","), cfg[section])}
        dict = {k:v[0] for k, v in dict.items() if v} # Removes blank keys and keep only first column after var
        return (dict)

    def getDataFrame(self:object, section:str, header:list = []) -> pd.DataFrame:
        """Generates a DataFrame from a [DEFINED] section
        :param section: The name of the section. Typically 'PIPELINES', 'DIRECTORIES', or 'SAMPLES'.
        :return: A DataFrame representing the sections
        """ 
        cfg = ConfigParser(allow_no_value=True)
        cfg.optionxform = str
        cfg.read(self.csv)
        buf = io.StringIO()
        buf.writelines('\n'.join(row.rstrip(',') for row in cfg[section]))
        buf.seek(0)
        if header:
            df = pd.read_csv(buf, header=None, names=header)
        else:
            df = pd.read_csv(buf)
        return (df.dropna(subset=['Sample_Group']))
    
    def getSheetPath(self:object) -> str:
        """Gets the run name from a pipeline worksheet
        :return: The run name
        """ 
        return self.path

    def getRunName(self:object) -> str:
        """Gets the run name from a pipeline worksheet
        :return: The run name
        """ 
        return self.getDataVar("Header")["Run_Name"]
    
    def getRunDir(self:object) -> str:
        """Gets the run directory from a pipeline worksheet
        :return: The run directory
        """ 
        return self.getDataVar("Header")["Run_Dir"]
    
    def getSamples(self:object) -> pd.DataFrame:
        """Gets a dataframe containing the sample information from a pipeline worksheet. See documentation for the ngs-pipeline-launcher for column limitations.
        :return: The sample metadata. At miniminum, these columns: Barcode, Plate_Pos, Sample_Group, and Control
        """ 
        return self.getDataFrame("Samples")
    
    def getOutputDir(self:object) -> pd.DataFrame:
        """Gets the output directories for each Sample_Group in the worksheet.
        :return: The output directories for each Sample_Group in the format of Sample_Group, Directory.
        """
        outdirs = self.getDataFrame("Directories",header=["Sample_Group","Directory"])
        samples = self.getSamples()["Sample_Group"]
        result = pd.merge(outdirs, samples, on='Sample_Group', how='right')
        return result.drop_duplicates()
    
    def getPipelines(self:object) -> pd.DataFrame:
        """Gets the pipeline scripts for each Sample_Group in the worksheet.
        :return: The output directories for each Sample_Group in the format of Sample_Group, Script.
        """
        scripts = self.getDataFrame("Pipelines",header=["Sample_Group","Script"])
        samples = self.getSamples()["Sample_Group"]
        result = pd.merge(scripts, samples, on='Sample_Group', how='right')
        return result.drop_duplicates()