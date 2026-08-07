import io, tempfile
import pandas as pd
from configparser import ConfigParser

class PipelineWorksheet:

    def __init__(self, path):
        self.xlsx = path
        self.csv = tempfile.NamedTemporaryFile().name
        df = pd.read_excel(path)        
        df.to_csv(self.csv, index=False)

    def getDataVar(self:object, section:str):
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

    def getDataFrame(self:object, section:str):
        """Generates a DataFrame from a [HEADER] section
        :param section: The name of the section
        :return: A DataFrame representing the sections
        """ 
        cfg = ConfigParser(allow_no_value=True)
        cfg.optionxform = str
        cfg.read(self.csv)
        buf = io.StringIO()
        buf.writelines('\n'.join(row.rstrip(',') for row in cfg[section]))
        buf.seek(0)
        df = pd.read_csv(buf)
        return (df)