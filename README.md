## TableViewResults
_Simple module for generating reports in .csv and .html, 
based on template csv files, consisting InfuxDB requests and other data.
Converts valid sql requests into db requests, saves results in output csv and html file._ 

Script accepts 3 String parameters:
    
        python run.py -h

1. template path 
2. test start ([in Unix format](https://www.epochconverter.com))
3. test end 

For example:

    python run.py templates/test.csv 1562668594441 1562672194442

