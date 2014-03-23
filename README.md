AndroidAnalyzer
===============
We plan to create a system for automated static analysis on Android APK files. The system will decompile the app back into Java pseudo-source code files. From there we will run an analysis script over the source code to extract relevant features and store the features in a database. We plan to look for features related to three topics: hardcoded credentials, sensitive data transmitted over an unencrypted medium and indicators of application popularity. 

Some relevant parameters to look for include:
- Static final variables that look like hard coded access keys. To do this we plan two tactics:
	-Research the possibility of positively identifying a string as being a key based on knowing the characteristics of three popular keys: AWS, Google Maps and Facebook API key.
	-Search decompiled source for likely variable names: secret, key, password, api, aws, etc.
- key/value pairs from strings.XML
- Locations of http(s) connections.
- Variables referenced in url string
- Lines of code in the application
- Code or UI libraries
- Presence of social media buttons
- Ratio of Lines of UI code to regular LoC

From this data we will quantify the frequency of hardcoded credential vulnerabilities and sensitive information sent over plaintext HTTP. We will also examine features that have a strong correlation with application popularity.

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