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
    
    def hideRowsExceptGroup(self:object, ws:xl.Worksheet, col: str, section:str, group:str):
        """Hides rows in the worksheet that do not match the group
        :param ws: The worksheet to check
        :param path: The column to check, as an integer. E.g., 1 for 'A'
        :param section: The section header. Typically '[Directories]' or '[Pipelines]'.
        :param group: The group to check for (case sensitive).
        :return: A DataFrame representing the sections
        """     
        sectionIdx = 0

        # Find the start of the section
        for cell in ws[xl.utils.get_column_letter(1)]:
            if cell.value == section:
                sectionIdx = cell.row
                break
        
        for row in range(sectionIdx+1,ws.max_row+1):
            val = ws.cell(row,1).value
            if val is None: # Break if the first column is blank
                break
            val = ws.cell(row,col).value
            if val != group: # Check if the target column contains the group
                ws.row_dimensions[row].hidden = True

    def subsetWorksheet(self:object, group:str, path:str, outPath:str, maxCols:int = 26):
        """Subsets a worksheet to only include a specific Sample_Group in the [SAMPLES] section.
        Due to limitations with openpyxl, formatting cannot be removed from the entire row without a significant amount of computation,
        so formatting will only be changed for columns 1 to 'maxCols'.
        :param group: The group to look for in the column 'Sample_Group'
        :param path: The input path of the pipeline worksheet
        :param out_path: The output path of the subsetted pipeline worksheet
        :param maxCols: The maximum number of columns to display/format
        :return: A DataFrame representing the sections
        """ 
        wb = xl.load_workbook(path)
        ws = wb.active

        # Sets the max visible columns
        last_col = maxCols 
        for col_idx in range(last_col+1, 16385):
            col_letter = xl.utils.get_column_letter(col_idx)
            # if (ws.column_dimensions[col_letter].hidden): break
            ws.column_dimensions[col_letter].hidden = True

        # Remove samples from the [Samples] section
        rows = list(ws.iter_rows(min_row=1, max_row=ws.max_row))

        for row in reversed(rows): 
            cell = row[2] # col idx 3 is Sample_Group, TODO: Search for this instead of hardcoding
            if cell.value == "Sample_Group":
                break
            if cell.value != group:
                ws.delete_rows(idx = cell.row)
                # Clear styles from the last row in the sheet, as the data will have shifted upwards
                for row in ws.iter_cols(min_row = ws.max_row+1, min_col = 1, max_col = last_col+1, max_row = ws.max_row+1):
                    for cell in row:
                        cell.style = "Normal"

        # Hide directories in the [Directories section]
        self.hideRowsExceptGroup(ws = ws, col = 1, section = "[Directories]", group = group)
        self.hideRowsExceptGroup(ws = ws, col = 1, section = "[Pipelines]",   group = group)

        wb.save(outPath)

