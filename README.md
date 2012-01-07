JVM-GC-STATS
============

SUMMARY
-------
A python script to parse Java Virtual Machine (JVM) garbage collection
trace output, push the data into Ganglia and alert on anomolies.
The data and graphs produced are intended to support operational
monitoring and inform GC tuning decisions.

The JVM is assumed to be Java6 and invoked with the following flags:

    -XX:+UseConcMarkSweepGC
    -verbosegc
    -XX:+PrintGCDetails
    -XX:+PrintGCTimeStamps

optional: 
    -XX:+PrintGCDateStamps


Fork from:

jkalucki https://github.com/jkalucki/jvm-gc-stats
|_________ ryanking https://github.com/ryanking/jvm-gc-stats
            |______ this here


USAGE
-------

 parse-gc.py -f LOGILE [-P PORT|-p PID]

Will print GC metrics in JSON format for every line it can parse.
If the java pid argument is given it will also jstat the old and perm
memory utilization using OGMX and PGMX.
jstat calls can be skipped if the URI in the GET requests contains jstat=0
Collected data can be cleared if the URI in the GET requests contains reset=1


Example calls:
    parse-gc.py -f gc.log
    parse-gc.py -f gc.log -P 5000
    parse-gc.py -f gc.log -p `pgrep java` -P 5000

LICENSE
-------
Apache 2.0 License. See included license file.
