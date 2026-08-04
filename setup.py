from setuptools import setup, find_packages

setup(
    name='pipeline_worksheet_reader',
    version='0.1.0-alpha',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'pandas',
        'openpyxl',
        'setuptools'
    ],
    python_requires='>=3.10, <4',
    description='A reader for NGS pipeline worksheets at APL.',
    url='https://github.com/provlab-bioinfo/pipeline-worksheet-reader',
    author='Andrew Lindsay',
    author_email='andrew.lindsay@albertaprecisionlabs.ca',
    include_package_data=True,
    keywords=[],
    zip_safe=False
)