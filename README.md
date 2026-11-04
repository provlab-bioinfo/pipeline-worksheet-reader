# pipeline-worksheet-reader

 [![Lifecycle:Stable](https://img.shields.io/badge/Lifecycle-Stable-97ca00)](https://lifecycle.r-lib.org/articles/stages.html#stable) [![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/provlab-bioinfo/pipeline-worksheet-reader/issues) [![License: GPL3](https://img.shields.io/badge/license-GPL3-lightgrey.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html) [![minimal Python version: 3.10](https://img.shields.io/badge/Python-3.10-6666ff.svg)](https://www.python.org/) [![Package Version = 1.0.0](<https://img.shields.io/badge/Package%20version-1.0.0-orange.svg?style=flat-square>)](https://github.com/provlab-bioinfo/pipeline-worksheet-reader/blob/main/NEWS) [![Last-changedate](<https://img.shields.io/badge/last%20change-2026--11--04-yellowgreen.svg>)](https://github.com/provlab-bioinfo/pipeline-worksheet-reader/blob/main/NEWS)

A reader for NGS pipeline worksheets used with the [provlab-bioinfo/ngs-pipeline-launcher](https://github.com/provlab-bioinfo/ngs-pipeline-launcher).

## Table of Contents

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Arguments](#arguments)
- [Usage](#usage)
- [References](#references)

## Dependencies

See [pyproject.toml](pyproject.toml) for package dependancies.

## Installation

Install with pip:

```bash
$ pip install git+https://github.com/provlab-bioinfo/pipeline-worksheet-reader
```

## Usage

Access in python:

```python
>>> import pipeline_worksheet_reader as pwr
>>> r = pwr.PipelineWorksheet("./examples/")
>>> r = pwr.PipelineWorksheet("./examples/PipelineWorksheet.xlsx")
>>> print(r)
>>> r.getSheetPath()
>>> r.getRunName()
>>> r.getRunDir()
>>> r.getSampleData()
>>> r.getMetaData()
>>> r.getOutputDirs()
>>> r.getPipelines()

>>> import pandas as pd
>>> data = pd.read_csv('examples/Nextclade.tsv', sep='\t')
>>> r.fuzzyMerge(data,"seqName")
```

## References

1. **Provlab-Bioinfo/ngs-pipeline-launcher:** A launcher tool for sorting sequencing runs and automatic initialization of their downstream pipelines. [https://github.com/provlab-bioinfo/ngs-pipeline-launcher](https://github.com/provlab-bioinfo/ngs-pipeline-launcher)
