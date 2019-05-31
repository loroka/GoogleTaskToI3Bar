#GoogleTaskToI3Bar
Small  program for I3Bar & dunstify which is based on GoogleTask API. Displays most recent task and uses dunstify to print out all tasks and subtasks when clicked. Script generates `GoogleTaskI3BarData.json` where last get data are stored to be used when offline.

##Instalation
Enable GoogleTask API at [link](https://developers.google.com/tasks/quickstart/python) and get the credentials. Copy credentials to location of [GoogleTaskToI3Bar.py]() and install all dependencies. Run the script and follow the verification at your browser. `token.pickle` will be generated containing all info to acces your GoogleTask via API (**do not share this file**), you can now delete `credentials.json`. When moving script make sure you move `token.pickle` with it or edit path to it.

###Dependencies:
* texttables - used for dunstify
* google-api-python-client 
* google-auth-httplib2 
* google-auth-oauthlib

```
$pip install --upgrade texttables google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
i3bar - https://i3wm.org/i3bar/
dunstify - https://github.com/dunst-project/dunst

