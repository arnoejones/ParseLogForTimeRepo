import os
import re
import pandas as pd
from datetime import datetime

# sample line to search for: Log Entry : 9:50:13 AM 09:50:13.902

location = "\\\\USNVR-W1005006\\PublicShare"
#pattern = r"\d{2}:\d{2}:\d{2}\.\d{3}\b"
# pattern = r"([0-9]+:[0-9]+:[0-9]+.[0-9]+)|(\d+(/|-){1}\d+(/|-){1}\d{2,4})" # this is the one for Log Entry : 3/1/2019 2:46:25 PM 02:46:25.066
pattern = r"([0-9]+:[0-9]+:[0-9]+.[0-9]+)|(\d+(/|-){1}\d+(/|-){1}\d{2,4}|([0-9]+:[0-9]+:[0-9]+\s[A|P]M))"

timeFormat = '%H:%M:%S.%f'

time_differences = []

for filename in os.listdir(location):
    print(filename)
    old = '00:00:00.000'
    with open(location + '/' + filename) as f:
        fileContents = f.read()
        counter = 0
        matches = re.findall(pattern, fileContents, re.MULTILINE)
        temp_list = []
        for matchNum, match in enumerate(matches):
            log_entry_date = matches[counter + 0][1]
            log_entry_time = matches[counter + 1][1]
            game_event_timestamp = matches[counter + 2][0]
            print("Iteration: {match_number}, "
                  "Log entry date: {log_entry_date}, "
                  "Log entry time: {log_entry_time}, "
                  "Game event timestamp: {game_event_timestamp}".format(match_number=matchNum,
                                                                       log_entry_date=log_entry_date,
                                                                       log_entry_time=log_entry_time,
                                                                       game_event_timestamp=game_event_timestamp))
            # temp_list.append(filename)
            # temp_list.append(log_entry_date)
            # temp_list.append(log_entry_time)
            new = game_event_timestamp
            deltaT = datetime.strptime(new, timeFormat) - datetime.strptime(old, timeFormat)

            print('deltaT: ', deltaT)
            old = new
            temp_list.append([filename, log_entry_date, log_entry_time, str(deltaT)])
            # temp_list.append(str(deltaT))

            if (matchNum < len(matches)/3 -1): # 3 elements per match -1 for index out of range
                counter += 3
            else:
                for i in range(2):
                    temp_list.pop(0)
                break
        time_differences.append(temp_list)
    # for i in range(4):
    #     time_differences.pop(0)
        # time_differences.pop(0)  # get rid of the first entry which is 0 - the timestamp
    # for diff in time_differences:
    #         print('Time elapsed is: ', diff)
df = pd.DataFrame(time_differences)
df = df.transpose()
df.columns = ['Client EGM','Log Entry Date','Log Entry Time','Elapsed Time']
print(df)
print('MAX!!!', df['Elapsed Time'].max())