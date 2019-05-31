from __future__ import print_function
import subprocess
import pickle
import os.path
import json
from io import StringIO
from texttables import Dialect
from texttables.dynamic import writer
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


LEFT_MOUSE = "1"

TIME_DUNSTIFY_VISIBLE=30000

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']

# Generated during authentatication
PICKLE_PATH = 'token.pickle'
# File generated form Source: ...
CREDS_PATH = 'credentials.json'
# File where recent data are stored 
PATH = 'GoogleTaskI3BarData.json'

WIDE_WS = u"\u2000"
POINT_CHAR = u"\u2020"


def main():

    # detect click from I3Bar
    blockButton = str(os.environ.get('BLOCK_BUTTON'))
 
    subtasks = []
    tasksWithDate = []
    tasks = []
   
    # Call the Tasks API
    try:
        service = GetService()
        tasklists_raw = service.tasklists().list().execute()
        tasklists = tasklists_raw.get('items', [])
        for tasklist in tasklists:
            if tasklist['title'] == 'Notebook tasks':
                tasks_raw = service.tasks().list(tasklist=tasklist['id']).execute()
                allTasks = tasks_raw.get('items', [])
                break

        # separate alltasks
        for task in allTasks:
            try:
                task['parent']
                subtasks.append(task)
            except Exception:
                try:
                    task['due']
                    tasksWithDate.append(task)
                    tasks.append(task)
                except Exception:
                    tasks.append(task)
                continue
    
        tasksWithDate.sort(key=lambda x: datetime.strptime(x['due'], '%Y-%m-%dT%H:%M:%S.000Z'))

        # store data to file
        data = { 'tasks' : tasks, 'tasksWithDate' : tasksWithDate, 'subtasks' : subtasks}
        with open(PATH, 'w') as outFile:
            json.dump( data, outFile)

    except Exception:
        # load data from file
        with open(PATH, 'r') as inFile:
            data = json.load(inFile)
            tasks = data.get('tasks')
            tasksWithDate = data.get('tasksWithDate')
            subtasks = data.get('subtasks')

    if (tasksWithDate != []): 
        I3BarPrint(tasksWithDate[0])    
    else:
        I3BarPrint(tasks[0])

    if (blockButton == LEFT_MOUSE):
        DunstifyPrint(tasks, tasksWithDate, subtasks)


def GetService():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    if os.path.exists(PICKLE_PATH):
        with open(PICKLE_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDS_PATH, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(PICKLE_PATH, 'wb') as token:
            pickle.dump(creds, token)

    return build('tasks', 'v1', credentials=creds)
def TimeLeft(dueDate, offset = False):
    timeLeft = datetime.strptime(dueDate, '%Y-%m-%dT%H:%M:%S.000Z') - datetime.now()
    out = ""
    if (timeLeft.days > 0):
        out = "{0}d".format(timeLeft.days)
    elif (timeLeft.seconds//3600 > 0):
        out =  "{0}h".format(timeLeft.seconds//3600)
    elif (timeLeft.seconds//60 > 0):
        out = "{0}m".format(timeLeft.seconds//60)

    while len(out) < 5 and offset:
        out += u"\u2000"
    return out
 

def I3BarPrint(task):
    date = datetime.strptime(task['due'], '%Y-%m-%dT%H:%M:%S.000Z').strftime('%d. %b')
    print("{0} | {1} | {2}".format(date,  task['title'], TimeLeft(task['due'])))
def DunstifyPrint(tasks, tasksWithDate, subtasks):
    output = StringIO()
    with writer(output, ['', '', '']) as w:
        w.writeheader((' ', ' ', ' ')) # dynamic mode not working without this
        for taskWithDate in tasksWithDate:
            w.writerow((WIDE_WS * 3 + "<b>" + TimeLeft(taskWithDate['due'], True) + "</b>",
                        "<b>" + taskWithDate['title'] + "</b>", 
                        WIDE_WS * 3))
        for task in tasks:
            if not (task in tasksWithDate):
                w.writerow(('', WIDE_WS * 2 + "<b>" + task['title'] + "</b>", WIDE_WS * 3))
            for subtask in subtasks:
                if (task['id'] == subtask['parent']):
                    w.writerow(('', 
                                WIDE_WS * 4 + POINT_CHAR + WIDE_WS * 2 + subtask['title'],
                                WIDE_WS * 3))

    # run dunstify 
    subprocess.run(["dunstify", 
                    output.getvalue(),
                    "--replace=1234", 
                    "-t" , str(TIME_DUNSTIFY_VISIBLE), 
                    "--icon=None"])

if __name__ == '__main__':
    main()