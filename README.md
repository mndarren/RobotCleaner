# Introduction 
This Robot cleaner is a microservice running background to schedule a time to clean specific files.
Since it's a microservice, user can trigger it to clean the specific files.

## Config file
- port: is for the port for service URL port number
- file_path: is the folder to be cleaned
- filename_pattern: specipy the filename pattern
- keep_days: keep the files whose age is less than the days
- start_time: scheduled time to do the cleaning
- max: keep latest max number of files

## How to Use the tool
```
curl -X POST http://localhost:8521/cleanup
# Please put the robot_cleaner_config.json file in the user home directory
```

&copy; 2024