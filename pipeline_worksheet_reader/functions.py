import os, re, io, pickle, glob, random, copy, shutil, logging, errno, hashlib, gzip
import pandas as pd
import openpyxl as xl
from configparser import ConfigParser
from pathlib import Path
from contextlib import suppress
from alive_progress import alive_bar
from itertools import chain
from collections import defaultdict

class PipelineWorksheet:

    def __init__(self, path):
        self.path = path

    def getDataVar(self:object, section:str):
        """Generates a dictionary from the first two columns of a [HEADER] section
        :param section: The name of the section
        :return: A dictionary containing variable keys
        """    
        cfg = ConfigParser(allow_no_value=True)
        cfg.optionxform = str
        cfg.read(self.path)
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
        cfg.read(self.pathpath)
        buf = io.StringIO()
        buf.writelines('\n'.join(row.rstrip(',') for row in cfg[section]))
        buf.seek(0)
        df = pd.read_csv(buf)
        return (df)
    
    # def convertToSampleSheet(self:object):

    def subsetWorksheet(self:object, group:str, path:str):
        """Generates a DataFrame from a [HEADER] section
        :param group: The group to look for in the column 'Sample_Group'
        :param path: The output path of the subsetted pipeline worksheet
        :return: A DataFrame representing the sections
        """ 
        wb = xl.load_workbook(self.path)
        ws = wb.active
        rows = list(ws.iter_rows(min_row=1, max_row=ws.max_row))
        for row in reversed(rows): 
            cell = row[2] # col idx 3 is Sample_Group
            if cell.value == "Sample_Group":
                break
            if cell.value != group:
                ws.delete_rows(cell.row, 1)
        wb.save(path)