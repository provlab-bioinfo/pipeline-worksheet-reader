import pytest
import pipeline_worksheet_reader.functions as pwr

def test_bad_input(): # Check for bad input
    with pytest.raises(FileNotFoundError): 
        pwr.PipelineWorksheet("/not-a-file/")

def test_pw_load():
    # Check if pipeline worksheets load
    pw = pwr.PipelineWorksheet("./examples/PipelineWorksheet.xlsx")
    assert len(str(pw)) > 0

    # Check if search returns the same worksheet
    pw2 = pwr.PipelineWorksheet("./examples/")
    assert len(str(pw)) > 0
    assert(str(pw) == str(pw2))

    # Check the string output
    assert("Path:" in str(pw))     # Check there's string output when calling obj alone

def test_getters():
    pw = pwr.PipelineWorksheet("./examples/PipelineWorksheet.xlsx")
    
    # Check the getters
    assert('str' in str(type(pw.getDataVar("Header")["Run_Name"]))) 
    assert('pandas.DataFrame' in str(type(pw.getDataFrame("Samples"))))

def test_outputs():

    pw = pwr.PipelineWorksheet("./examples/PipelineWorksheet.xlsx")

    # Check the file/header info
    assert(pw.getSheetPath() == './examples/PipelineWorksheet.xlsx')
    assert(pw.getRunName() == '230711_N_I_063')
    assert(pw.getRunDir() == '/nfs/raw/YOUR_RUN/')

    # Check the sample data
    sd = pw.getSampleData()
    assert('pandas.DataFrame' in str(type(sd)))
    assert('Barcode' in sd.columns.tolist())
    assert('Sample_Group' in sd.columns.tolist())
    assert(len(sd) == 5)

    # Check the metadata
    md = pw.getMetaData()
    assert('pandas.DataFrame' in str(type(md)))
    assert('Barcode' in sd.columns.tolist())
    assert('Sample_Group' not in md.columns.tolist())   # Sample_Group should NOT be present
    assert(len(sd) == 5)
    assert(set(md.columns).issubset(set(sd.columns)))

    # Check the output dirs
    od = pw.getOutputDirs()
    assert('pandas.DataFrame' in str(type(od)))
    assert('Sample_Group' in od.columns.tolist())
    assert(len(od) == 1)

    # Check the pipeline scripts
    ps = pw.getPipelines()
    assert('pandas.DataFrame' in str(type(ps)))
    assert('Sample_Group' in ps.columns.tolist())
    assert(len(od) == 1)