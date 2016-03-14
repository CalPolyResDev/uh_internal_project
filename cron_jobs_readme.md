Cron Job ReadMe
===============

Purpose
-------

The Purpose of this file is to track all of the cron jobs that are scheduled on
the server to avoid overlapping tasks that may impact each other. 

Tasks that happen more than once per hour are excluded because these should be
designed to not be taxing enough to impact other services.


Task List
---------

Task list is organized in order from least frequent to most.

* __0 1 * * *__ Session Cleaner
    * Location: UWSGI.ini
* __0 2 * * *__ Database Backup
    * Location: UWSGI.ini
* __0 3 * * *__ Server Update including Reboot
    * Location: Root's crontab
* __0 4 * * *__ Airwaves ID Updater
    * Location: UWSGI.ini