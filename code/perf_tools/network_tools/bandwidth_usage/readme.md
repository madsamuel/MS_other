python bandwidth_usage.py --interval 2 --threshold 5 --interface eth0 --csv-output bandwidth_log.csv

--interval 2 measures usage every 2 seconds.
--threshold 5 triggers a warning if more than 5 MB are sent or received during one interval.
--interface eth0 focuses on the eth0 interface rather than all interfaces.
--csv-output bandwidth_log.csv logs data to a CSV file.