# accessibility-checker

# Overview :

This CLI program checks the given website's accessibility provided by the W3C guidelines and outputs a score from 0-100.  
Note that, this is not a definite tool for checking accessibility, therefore the results should be treated as suggestions.  
Also, this program doesn't check WAI-ARIA attributes, it checks for other HTML semantics.  

# Usage :

Get the dependencies first:  
```cmd
$ pip install -r requirements.txt
```

```cmd
$ python checker.py <website-url> [-h] [-n NAME] [-s] [-o] [-c]
```
# Arguments Guide :
```cmd
positional arguments:
  url                   enter the website url.

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  enter the name of the website.
  -s, --short           show a short version of the result with highlights.
  -o, --score           show only the score.
  -c, --csv             write the scores as csv.

```
# Known Issues :  
* > PermissionError: [Errno 13] Permission denied  
Run these commands:  
```
chown admin:admin web-accessibility.csv
or
chmod 755 web-accessibility.csv
```
# Sources : 
[WCAG2-W3C](https://www.w3.org/WAI/WCAG21/quickref/?showtechniques=121#principle1)  
[Accessibility-MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
