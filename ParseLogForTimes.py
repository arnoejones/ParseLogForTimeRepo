import os
import re
import pandas as pd
from datetime import datetime

# sample line for the following regex to match: Log Entry : 9:50:13 AM 09:50:13.902
pattern = r"([0-9]+:[0-9]+:[0-9]+.[0-9]+)|(\d+(/|-){1}\d+(/|-){1}\d{2,4}|([0-9]+:[0-9]+:[0-9]+\s[A|P]M))"
location = "\\\\USNVR-W1005006\\PublicShare"

timeFormat = '%H:%M:%S.%f'

time_differences = []

def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

for filename in os.listdir(location):
    print(filename)
    old = '00:00:00.000'
    temp_list = []
    with open(location + '/' + filename) as f:
        fileContents = f.read()
        counter = 0
        matches = re.findall(pattern, fileContents, re.MULTILINE)

        for matchNum, match in enumerate(matches):
            log_entry_date = matches[counter + 0][1]
            log_entry_time = matches[counter + 1][1]
            game_event_timestamp = matches[counter + 2][0]
            # print("Iteration: {match_number}, "
            #       "Log entry date: {log_entry_date}, "
            #       "Log entry time: {log_entry_time}, "
            #       "Game event timestamp: {game_event_timestamp}".format(match_number=matchNum,
            #                                                            log_entry_date=log_entry_date,
            #                                                            log_entry_time=log_entry_time,
            #                                                            game_event_timestamp=game_event_timestamp))
            # temp_list.append(filename)
            # temp_list.append(log_entry_date)
            # temp_list.append(log_entry_time)
            new = game_event_timestamp
            deltaT = datetime.strptime(new, timeFormat) - datetime.strptime(old, timeFormat)

            deltaTinSeconds = deltaT.total_seconds()

            # deltaTinSeconds = get_sec((deltaT))
            # deltaTinSeconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(deltaT.split(":"))))
            # print('deltaT: ', deltaT)
            old = new
            temp_list.append([filename, log_entry_date, log_entry_time, (deltaTinSeconds)])

            if (matchNum < len(matches)/3 -1): # 3 elements per match -1 for index out of range
                counter += 3
            else:
                for i in range(2):
                    temp_list.pop(0)
                break
        time_differences.append(temp_list)
        flat_list = [item for sublist in time_differences for item in sublist]
df = pd.DataFrame(flat_list)

df.columns = ['Client EGM','Log Entry Date','Log Entry Time','Elapsed Time']
print(df)
df['Elapsed Time'].describe()
s = pd.Series([4])
s.describe()
print('MAX seconds', df['Elapsed Time'].max())
print('MIN seconds', df['Elapsed Time'].min())
print('SUM of all seconds', df['Elapsed Time'].sum())
print('MEAN time of the delta Ts', df['Elapsed Time'].mean())
print('STANDARD DEVIATION ', df['Elapsed Time'].std())
print('COUNT of samples', df['Elapsed Time'].count())
