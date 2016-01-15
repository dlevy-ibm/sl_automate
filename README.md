# sl_automate
This code will retrieve information from the Softlayer API to populate the data for a number of required files for a blue box deploy (i.e computeX.yml)

Installation:
(Consider using a virtual environment)
Pip is required. Just run 'pip install softlayer' and you're good to go!

Usage Instructions:
1. Populate the file userinfo.py with your credentials. The API key can be retrieved from Softlayer in your profile (click on your user name).
2. Populate the machines.csv file.
Format:
computex/controllerx hostname
compute1 abc1.softlayer.com
compute2 abc2.softlayer.com
Since the only thing that should change are the numbers, an easy way to create this file is with excel.
3. Run populate_data.py


References:
https://softlayer-api-python-client.readthedocs.org/en/latest/install/
