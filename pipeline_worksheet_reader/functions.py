import io, tempfile, os, difflib
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
            f"{self.getOutputDirs().to_string(index=False)}\n\n"
            f"Samples\n"
            f"--------\n"
            f"{self.getSampleData().to_string(index=False)}\n"
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
    
    def getSampleData(self:object) -> pd.DataFrame:
        """Gets a dataframe containing the sample information from a pipeline worksheet. See documentation for the ngs-pipeline-launcher for column limitations.
        :return: The sample metadata. At miniminum, these columns: Barcode, Plate_Pos, Sample_Group, and Control
        """ 
        return self.getDataFrame("Samples")
    
    def getMetaData(self:object) -> pd.DataFrame:
        """Gets a dataframe containing the sample information from a pipeline worksheet. See documentation for the ngs-pipeline-launcher for column limitations.
        :return: The sample metadata. At miniminum, these columns: Barcode, and Control
        """ 
        return self.getDataFrame("Samples").drop(columns=['Plate_Pos', 'Sample_Group'])
    
    def getOutputDirs(self:object) -> pd.DataFrame:
        """Gets the output directories for each Sample_Group in the worksheet.
        :return: The output directories for each Sample_Group in the format of Sample_Group, Directory.
        """
        outdirs = self.getDataFrame("Directories",header=["Sample_Group","Directory"])
        samples = self.getSampleData()["Sample_Group"]
        result = pd.merge(outdirs, samples, on='Sample_Group', how='right')
        return result.drop_duplicates()
    
    def getPipelines(self:object) -> pd.DataFrame:
        """Gets the pipeline scripts for each Sample_Group in the worksheet.
        :return: The output directories for each Sample_Group in the format of Sample_Group, Script.
        """
        scripts = self.getDataFrame("Pipelines",header=["Sample_Group","Script"])
        samples = self.getSampleData()["Sample_Group"]
        result = pd.merge(scripts, samples, on='Sample_Group', how='right')
        return result.drop_duplicates()
    
    def fuzzyMerge(self:object, data:pd.DataFrame, merge_on:str, drop_cols:list = ["Barcode", "Sample_Group", "Control"]) -> pd.DataFrame:
        """Attempts to merge metadata from a pipeline worksheet to another file. This is useful because the sample name usually contains the barcode, but also contains other necessary data (e.g., sample '260903_N_I_092_4_S4_L001' uses barcode '4').
        :param data: A dataframe containing the data to be collated to the metadata in the pipeline worksheet
        :param merge_on: The column in 'data' for which to merge against the metadata in the pipeline worksheet
        :param drop_cols: Columns to drop from the final output. By default, drops 'Barcode', 'Sample_Group', and 'Control', which are the most basic columns in the pipeline worksheet.
        :return: The same format as the input data frame, with the addition of the metadata columns from the pipeline worksheet.
        """
        metadata = self.getSampleData()
        metadata["Barcode"] = metadata["Barcode"].astype('string')

        # Find common suffix and prefixes
        prefix = os.path.commonprefix(data[merge_on].tolist())
        suffix = [id[::-1] for id in data[merge_on]]
        suffix = os.path.commonprefix(suffix)[::-1]

        # Create new column to merge on
        merge_on_barcode = merge_on+"_barcode"
        data[merge_on_barcode] = data[merge_on]
        data[merge_on_barcode] = data[merge_on_barcode].str.removeprefix(prefix)
        data[merge_on_barcode] = data[merge_on_barcode].str.removesuffix(suffix)

        # Find closest matches
        data[merge_on_barcode] = data[merge_on_barcode].map(lambda x: difflib.get_close_matches(x, metadata["Barcode"], n=1, cutoff=0.2)[0])

        # Merge and subset non-metadata columns
        result = data.merge(metadata, left_on=merge_on_barcode, right_on="Barcode").drop(columns=[merge_on_barcode]+drop_cols)
        return result