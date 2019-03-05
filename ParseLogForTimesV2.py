# -----------------------------------------------------------------------
# <copyright file = "ParseLogForTimes.py" company = "IGT">
#     Copyright © 2019 IGT.  All rights reserved.
# </copyright>
# -----------------------------------------------------------------------

import os
import re
import pandas as pd
from datetime import datetime
import PySimpleGUI as sg

# sample line for the following regex to match: Log Entry : 9:50:13 AM 09:50:13.902
pattern = r"([0-9]+:[0-9]+:[0-9]+.[0-9]+)|(\d+(/|-){1}\d+(/|-){1}\d{2,4}|([0-9]+:[0-9]+:[0-9]+\s[A|P]M))"
raw_logs_location = "\\\\USNVR-W1005006\\PublicShare\\BaccaratLogs"
logs_results_location = '\\\\USNVR-W1005006\\PublicShare\\BaccaratLogsCSV'

timeFormat = '%H:%M:%S.%f'

time_differences = []

files_read = []

def load_engine():
    for filename in os.listdir(raw_logs_location):
        files_read.append(filename)
        print(filename)
        old = '00:00:00.000'
        temp_list = []
        with open(raw_logs_location + '/' + filename) as f:
            fileContents = f.read()
            counter = 0
            matches = re.findall(pattern, fileContents, re.MULTILINE)

            for matchNum, match in enumerate(matches):
                log_entry_date = matches[counter + 0][1]
                log_entry_time = matches[counter + 1][1]
                game_event_timestamp = matches[counter + 2][0]

                new = game_event_timestamp
                deltaT = datetime.strptime(new, timeFormat) - datetime.strptime(old, timeFormat)

                deltaTinSeconds = deltaT.total_seconds()

                old = new
                temp_list.append([filename, log_entry_date, log_entry_time, (deltaTinSeconds)])

                if matchNum < len(matches)/3 -1: # 3 elements per match -1 for index out of range
                    counter += 3
                else:
                    for i in range(2):
                        temp_list.pop(0) # delete the entry that subtracts current time from 0, as that's meaningless.
                    break
            time_differences.append(temp_list)

    df = pd.DataFrame(item for sublist in time_differences for item in sublist) # convert list of lists into list

    df.columns = ['Client EGM','Log Entry Date','Log Entry Time','Elapsed Time']

    print('MAX seconds', df['Elapsed Time'].max())
    print('MIN seconds', df['Elapsed Time'].min())
    print('SUM of all seconds', df['Elapsed Time'].sum())
    print('MEAN time of the delta Ts', df['Elapsed Time'].mean())
    print('STANDARD DEVIATION ', df['Elapsed Time'].std())
    print('COUNT of samples', df['Elapsed Time'].count())

    current_time = str(datetime.now().date())

    # --- write to summary file --- #
    with open(logs_results_location + '\\' + current_time + '_BaccaratStats.txt', 'w+') as f:
        f.writelines(str(len(files_read)) + ' log files read.' + '\r\n\r\n')
        f.write('MAX seconds: ' + str(df['Elapsed Time'].max()) + '\r\n')
        f.write('MIN seconds: ' + str(df['Elapsed Time'].min()) + '\r\n')
        f.write('SUM of all elapsed times: ' + str(df['Elapsed Time'].sum()) + '\r\n')
        f.write('MEAN seconds: ' + str(df['Elapsed Time'].mean()) + '\r\n')
        f.write('STANDARD DEVIATION: ' + str(df['Elapsed Time'].std()) + '\r\n')
        f.write('COUNT of all samples: ' + str(df['Elapsed Time'].count()) + '\r\n')
        f.write('\r\n')
        for file in files_read:
            f.write('Log file read: ' + file + '\r\n')

    # --- write to a csv log --- #
    if not os.path.exists(logs_results_location):
        os.makedirs(logs_results_location)

    df.to_csv(logs_results_location + '\\' + current_time + '_LogsReport.csv')

# https://pysimplegui.readthedocs.io/#how-do-i
layout = [
    [sg.Text('Launch Baccarat Client Simulator', size = (30, 1), font=("Helvetica", 25), text_color='blue')],
    [sg.Text('IP Address of target Baccarat server:', size=(35, 1)), sg.InputText('10.213.133.65', key='_IP_')],
    [sg.Text('Port address of Baccarat server:', size=(35, 1)), sg.InputText('4456', key='_PORT_')],
    [sg.Text('Logs destination, full path:', size=(35, 1)), sg.InputText(r'\\USNVR-W1005006\PublicShare\BaccaratLogs', key='_LOGSDEST')],
    [sg.Text('Statistics and csv file destination:', size=(35, 1)), sg.InputText(r'\\USNVR-W1005006\PublicShare\BaccaratLogsCSV', key='CSVDEST')],
    [sg.Text('How many processes to launch: ', size=(35, 1)), sg.InputText('4', key='_NUMOFPROCS_')],
    [sg.Text('Statistics summary: ', size=(35, 1)), sg.Multiline(default_text='29 log files read\n'
                                                         '\n'
                                                         'MAX seconds: 108.177\n'
                                                         'MIN seconds: 0.004\n'
                                                         'SUM of all elapsed times: 32905.762\n'
                                                         'MEAN seconds: 4.005570541692027\n'
                                                         'STANDARD DEVIATION: 3.40685478981833\n'
                                                         'COUNT of all samples: 8215',key='_SUMMARY_', size=(55, 5))],
    [sg.Button("Create Stats File"), sg.Submit(), sg.Exit()]
]

window = sg.Window('Baccarat Client Load Test Automation').Layout(layout)

while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

    if event == 'Submit':
        # do the stuff here
        load_engine()
        print('I am here.')

window.Close()
print(values['_IP_'])
print(values['_PORT_'])
print(values['_LOGSDEST'])
print(values['CSVDEST'])
print(values['_NUMOFPROCS_'])
print(values['_SUMMARY_'])