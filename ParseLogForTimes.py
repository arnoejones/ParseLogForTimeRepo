# -----------------------------------------------------------------------
# <copyright file = "ParseLogForTimes.py" company = "IGT">
#     Copyright © 2019 IGT.  All rights reserved.
# </copyright>
# -----------------------------------------------------------------------

import os
import re
import pandas as pd
from datetime import datetime

# sample line for the following regex to match: Log Entry : 9:50:13 AM 09:50:13.902
pattern = r"([0-9]+:[0-9]+:[0-9]+.[0-9]+)|(\d+(/|-){1}\d+(/|-){1}\d{2,4}|([0-9]+:[0-9]+:[0-9]+\s[A|P]M))"
raw_logs_location = "\\\\USNVR-W1005006\\PublicShare\\BaccaratLogs"
logs_results_location = '\\\\USNVR-W1005006\\PublicShare\\BaccaratLogsCSV'

timeFormat = '%H:%M:%S.%f'

time_differences = []

files_read = []

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