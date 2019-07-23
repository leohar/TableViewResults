## TableViewResults
_Simple module for generating reports in .csv and .html, 
based on template csv files, consisting InfuxDB requests and other data.
Converts valid sql requests into db requests, saves results in output csv and html file._ 

script accepts 3 string parameters:
    
        python run.py -h

1. template path 
2. test start ([in Unix format](https://www.epochconverter.com))
3. test end 

For example:

    python run.py templates/test.csv 1562668594441 1562672194442

template .csv creation tips: 
 * querry should be inserted in cell as is, without escaping
 * there is difference function, it works when minuend is followed by subtrahend with string 'diff' inbetween.

For ex.:

Cell 1 | Cell 2 | Cell 3
------ | ------ | ------
50 | diff | 30
