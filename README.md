## TableViewResults
_Simple module for generating reports in .csv and .html, 
based on template csv files, consisting InfuxDB requests and other data.
Converts valid sql requests into db requests, saves results in output csv and html file, generates report in parent confluence page
and attaches all images from Grafana._

script accepts one string parameter - template path:

        python run.py -h

For example:

    python run.py templates/template.csv

other parameters, could be set in settings.ini



template .csv creation tips: 
 * query should be inserted in cell as is, without escaping
 * there is difference function, it calculates difference between reply waiting time and rt of the following component and
  works with string 'diff' , cell order should be the same

For ex.:

COMPONENT  | RT   | RQ PROC | RS PROC | RW
---------- | ---- | ------- | ------- | ---
COMPONENT1 | 112  |    5    |    5    | 117
---------- | -----| ------- | ------- | ---
EMS        | diff |    x    |    x    |
---------- | -----| ------- | ------- | ---
COMPONENT2 | 111  |    5    |    5    | 100
