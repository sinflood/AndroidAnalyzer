AndroidAnalyzer
===============
The AndroidAnalyzer performs static analysis on Android APK files. AndroidAnalyzer is intended to be run decompiled Android application source code to extract relevant features and store the features in a database. Current implemented functions search for hard coded credentials and signs of code obfuscation. 

Documentation
=============
 * [May 2, 2014 Presentation](https://dl.dropboxusercontent.com/u/1207310/AndroidAnalyzer/AndroidAnalyzerFinalPresentation.pdf)
 * [May 12, 2014 Paper](https://dl.dropboxusercontent.com/u/1207310/AndroidAnalyzer/AndroidAnalyzerFinalPaper.pdf)

Getting Started
===============
1. Install [MySql](http://www.mysql.com).
2. Install [Python](https://www.python.org).
3. You can follow the example path for using AndroidAnalyzer

```
/Volumes/Macintosh HDD/Columbia Security/AndroidAnalyzer [git::master *] [chrisdangelo@macmini] [15:29]
> mysql.server start
Starting MySQL
. SUCCESS! 

/Volumes/Macintosh HDD/Columbia Security/AndroidAnalyzer [git::master *] [chrisdangelo@macmini] [15:30]
> mysql -uroot
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 1
Server version: 5.6.16 Homebrew

Copyright (c) 2000, 2014, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> create database apps;
Query OK, 1 row affected (0.00 sec)

mysql> quit;
Bye

/Volumes/Macintosh HDD/Columbia Security/AndroidAnalyzer [git::master *] [chrisdangelo@macmini] [15:30]
> python appParser.py -d ../Columbia\ Security\ APKS/MyFiles/80decompiled
dir ../Columbia Security APKS/MyFiles/80decompiled/air.com.adobe.top5acrobat-1000000

...

dir ../Columbia Security APKS/MyFiles/80decompiled/thecouponsapp.coupon-904

/Volumes/Macintosh HDD/Columbia Security/AndroidAnalyzer [git::master *] [chrisdangelo@macmini] [15:32]
> mysql -uroot
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 3
Server version: 5.6.16 Homebrew

Copyright (c) 2000, 2014, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> use apps;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> select * from app;
+----+-----------+---------------------------------------------------------------------------------------------------+
| id | package   | appname                                                                                           |
+----+-----------+---------------------------------------------------------------------------------------------------+
|  1 | something | ../Columbia Security APKS/MyFiles/80decompiled/air.com.adobe.top5acrobat-1000000                  |

...

| 79 | something | ../Columbia Security APKS/MyFiles/80decompiled/thecouponsapp.coupon-904                           |
+----+-----------+---------------------------------------------------------------------------------------------------+
79 rows in set (0.00 sec)

mysql> drop database apps;
Query OK, 4 rows affected (0.01 sec)

mysql> quit;
Bye

```
