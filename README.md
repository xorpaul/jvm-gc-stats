JVM-GC-STATS
============

SUMMARY
-------
A python script to parse Java Virtual Machine (JVM) garbage collection
trace output, push the data into Ganglia and alert on anomolies.
The data and graphs produced are intended to support operational
monitoring and inform GC tuning decisions.

The JVM is assumed to be Java6 and invoked with the following flags:

    -verbosegc
    -XX:+PrintGCDetails
    -XX:+PrintGCTimeStamps
    supports either
        -Xloggc:gc-`date +%F-%H-%M`.log
      or
        -Xloggc:gc.log

    optional: 
    -XX:+PrintGCDateStamps
    -XX:+PrintTenuringDistribution


DESCRIPTION
-------

    parse-gc.py -c CONFIGFILE

Will print GC metrics in JSON format for every line it can parse.
Collected data can be cleared if the URI in the GET requests contains reset=1


Example calls:

    parse-gc.py -c config/example.conf

Example config file:
<pre>
# [general]
# port at which the HTTP server will run
# port: 5000
# If no general config section is found the
# default values 5000 for port and 1 second sleeptime between logfile
# seeks will be used.

# [services]
# SERVICENAME: logfile
# GC logfile you want to follow and parse with fuzzy name support
# The script will use the file with the most recent ctime
# noticed logrotate from gc-2012-01-15-21-08.log to gc-2012-01-15-21-09.log
# noticed logrotate in gc-2012-01-15-21-09.log

[services]
test1: /var/log/jvm/gc-*.log
test2: gc.log
</pre>
USAGE
-------
<pre>
# start the parse script
$ ./parse-gc.py -c config/example.conf
# and call it from another server / shell
$ curl http://YOURIP:5000
{"errors": 0}
# you can test it by using the example files
$ cat gc-example-without-timestamps >> gc.log && cat gc-example-with-timestamps >> gc.log.1
$ curl http://YOURIP:5000
{"test2": {"count": 30, "full": {"max_newgen_kb_collected": 0, "newgen_kb_collected": 0, "total_kb_collected": 38180, "max_oldgen_kb_collected": 0, "max_sys_time": "0.01", "avg_time_between_collections": "0.00", "max_permgen_kb_collected": -2300, "avg_newgen_kb_collected": 0, "avg_oldgen_kb_collected": -3340, "max_total_kb_collected": 22021, "sys_time": "0.02", "oldgen_kb_collected": -6679, "avg_total_kb_collected": 19090, "user_time": "0.28", "max_user_time": "0.14", "max_real_time": "0.14", "avg_permgen_kb_collected": 8, "count": 2, "avg_real_time": "0.12", "avg_user_time": "0.14", "permgen_kb_collected": 17, "real_time": "0.25", "avg_sys_time": "0.01"}, "avg_time_between_any_type_collections": "0.00", "cur_total_kb_allocated": 24853, "cur_permgen_kb_allocated": 27224, "par_new": {"count": 28, "max_newgen_kb_collected": 27929, "avg_time_between_collections": "0.00", "avg_real_time": "0.01", "max_user_time": "0.05", "avg_newgen_kb_collected": 26004, "newgen_kb_collected": 728113, "total_kb_collected": 710460, "max_real_time": "0.03", "avg_user_time": "0.01", "max_sys_time": "0.01", "max_total_kb_collected": 27076, "sys_time": "0.02", "real_time": "0.19", "avg_sys_time": "0.00", "avg_total_kb_collected": 25373, "user_time": "0.35"}, "cur_newgen_kb_allocated": 521, "cur_oldgen_kb_allocated": 8246}, "test1": {"count": 66, "cms_remark": {"count": 1, "avg_time_between_collections": "0.00", "avg_real_time": "0.00", "max_user_time": 0, "max_real_time": 0, "avg_user_time": "0.00", "max_sys_time": 0, "sys_time": "0.00", "real_time": "0.00", "avg_sys_time": "0.00", "user_time": "0.00"}, "full": {"max_newgen_kb_collected": 0, "newgen_kb_collected": 0, "total_kb_collected": 506049, "max_oldgen_kb_collected": 126117, "max_sys_time": "0.01", "avg_time_between_collections": "0.00", "max_permgen_kb_collected": -4361, "avg_newgen_kb_collected": 0, "avg_oldgen_kb_collected": 5420, "max_total_kb_collected": 226988, "sys_time": "0.02", "oldgen_kb_collected": 233067, "avg_total_kb_collected": 11768, "user_time": "4.87", "max_user_time": "0.43", "max_real_time": "0.43", "avg_permgen_kb_collected": 4, "count": 43, "avg_real_time": "0.12", "avg_user_time": "0.11", "permgen_kb_collected": 173, "real_time": "5.10", "avg_sys_time": "0.00"}, "avg_time_between_any_type_collections": "0.00", "cms_initial_mark": {"count": 2, "avg_time_between_collections": "0.00", "avg_real_time": "0.00", "max_user_time": 0, "max_real_time": 0, "avg_user_time": "0.00", "max_sys_time": 0, "sys_time": "0.00", "real_time": "0.00", "avg_sys_time": "0.00", "user_time": "0.00"}, "promotion_failure": {"max_newgen_kb_collected": 22447, "newgen_kb_collected": 22447, "total_kb_collected": 1507825, "max_oldgen_kb_collected": 279126, "max_sys_time": "0.07", "avg_time_between_collections": "0.00", "avg_newgen_kb_collected": 11223, "avg_oldgen_kb_collected": 162279, "max_total_kb_collected": 1443275, "sys_time": "0.07", "oldgen_kb_collected": 324558, "avg_total_kb_collected": 753912, "user_time": "3.74", "max_user_time": "3.18", "max_real_time": "3.20", "avg_permgen_kb_collected": 0, "count": 2, "avg_real_time": "1.86", "avg_user_time": "1.87", "permgen_kb_collected": 0, "real_time": "3.72", "avg_sys_time": "0.04"}, "cms_concurrent_sweep": {"count": 1, "avg_time_between_collections": "0.00", "avg_real_time": "0.01", "max_user_time": "0.02", "max_real_time": "0.01", "avg_user_time": "0.02", "max_sys_time": 0, "sys_time": "0.00", "real_time": "0.01", "avg_sys_time": "0.00", "user_time": "0.02"}, "cur_total_kb_allocated": 111306, "cms_concurrent_reset": {"count": 1, "avg_time_between_collections": "0.00", "avg_real_time": "0.00", "max_user_time": 0, "max_real_time": 0, "avg_user_time": "0.00", "max_sys_time": 0, "sys_time": "0.00", "real_time": "0.00", "avg_sys_time": "0.00", "user_time": "0.00"}, "cur_permgen_kb_allocated": 70192, "par_new": {"count": 8, "max_newgen_kb_collected": 95441, "avg_time_between_collections": "0.00", "avg_real_time": "0.02", "max_user_time": "0.14", "avg_newgen_kb_collected": 46505, "newgen_kb_collected": 372040, "total_kb_collected": 207069, "max_real_time": "0.05", "avg_user_time": "0.05", "max_sys_time": 0, "max_total_kb_collected": 84639, "sys_time": "0.00", "real_time": "0.17", "avg_sys_time": "0.00", "avg_total_kb_collected": 25883, "user_time": "0.39"}, "cms_concurrent_preclean_start": {"count": 1, "avg_time_between_collections": "0.00"}, "cms_concurrent_mark_start": {"count": 2, "avg_time_between_collections": "0.00"}, "cms_concurrent_mark": {"count": 2, "avg_time_between_collections": "0.00", "avg_real_time": "0.14", "max_user_time": "0.26", "max_real_time": "0.16", "avg_user_time": "0.19", "max_sys_time": 0, "sys_time": "0.00", "real_time": "0.29", "avg_sys_time": "0.00", "user_time": "0.38"}, "cur_newgen_kb_allocated": 2785, "cur_oldgen_kb_allocated": 108521, "cms_concurrent_reset_start": {"count": 1, "avg_time_between_collections": "0.00"}, "cms_concurrent_sweep_start": {"count": 1, "avg_time_between_collections": "0.00"}, "cms_concurrent_preclean": {"count": 1, "avg_time_between_collections": "0.00", "avg_real_time": "0.01", "max_user_time": "0.01", "max_real_time": "0.01", "avg_user_time": "0.01", "max_sys_time": 0, "sys_time": "0.00", "real_time": "0.01", "avg_sys_time": "0.00", "user_time": "0.01"}}, "errors": 0, "seconds_since_last_reset": "10.85"}
# or using pretty print:
$ curl http://YOURIP:5000/pretty=1
{
    "errors": 0, 
    "seconds_since_last_reset": "269.02", 
    "count": 66, 
    "cur_newgen_kb_allocated": 2785, 
    "cur_oldgen_kb_allocated": 108521, 
    "cur_permgen_kb_allocated": 70192, 
    "cur_total_kb_allocated": 111306,
    "test": {
        "avg_time_between_any_type_collections": "7.17", 
        "count": 35, 
        "cur_newgen_kb_allocated": 3264, 
        "cur_oldgen_kb_allocated": 8246, 
        "cur_permgen_kb_allocated": 27224, 
        "cur_total_kb_allocated": 11521, 
        "full": {
            "avg_newgen_kb_collected": 0, 
            "avg_oldgen_kb_collected": -3340, 
            "avg_permgen_kb_collected": 8, 
            "avg_real_time": "0.12", 
            "avg_sys_time": "0.01", 
            "avg_time_between_collections": "62.74", 
            "avg_total_kb_collected": 19090, 
            "avg_user_time": "0.14", 
            "count": 4, 
            "max_newgen_kb_collected": 0, 
            "max_oldgen_kb_collected": 0, 
            "max_permgen_kb_collected": -2300, 
            "max_real_time": "0.14", 
            "max_sys_time": "0.01", 
            "max_total_kb_collected": 22021, 
            "max_user_time": "0.14", 
            "newgen_kb_collected": 0, 
            "oldgen_kb_collected": -13358, 
            "permgen_kb_collected": 34, 
            "real_time": "0.50", 
            "sys_time": "0.04", 
            "total_kb_collected": 76360, 
            "user_time": "0.56"
        }, 
        "par_new": {
            "avg_newgen_kb_collected": 25725, 
            "avg_real_time": "0.01", 
            "avg_sys_time": "0.00", 
            "avg_time_between_collections": "8.10", 
            "avg_total_kb_collected": 25104, 
            "avg_user_time": "0.01", 
            "count": 31, 
            "max_newgen_kb_collected": 27929, 
            "max_real_time": "0.03", 
            "max_sys_time": "0.01", 
            "max_total_kb_collected": 27076, 
            "max_user_time": "0.05", 
            "newgen_kb_collected": 797483, 
            "real_time": "0.22", 
            "sys_time": "0.02", 
            "total_kb_collected": 778252, 
            "user_time": "0.41"
        }
    }
}
</pre>
Fork from:
<pre>
jkalucki https://github.com/jkalucki/jvm-gc-stats
|_________ ryanking https://github.com/ryanking/jvm-gc-stats
                |_________ this here
</pre>
LICENSE
-------
Apache 2.0 License. See included license file.
