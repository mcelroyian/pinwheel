Python version 3.8.3


This script works with command line arguements

There are two availalbe functions on this script

Save Forms

This will save the form based on a Form Name and range of years
This will create a folder of the form name in the directory that the program is being run and download the files in that directory. 

Usage
```search-forms.py save_forms <form_name> <start_year> <end_year>
#example
search-forms.py save_forms 'Form W-2' 1988 1998

```


Get Form Data

This will return to the terminal JSON containing data on the list of searched term

Usage
```
#single
search-forms.py get_form_data 'Form w-2'

#multiple
search-forms.py get_form_data 'Form w-2' 'Form W-2 P' 'Form 1095-C'
```