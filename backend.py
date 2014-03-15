import mysql.connector

#Set this to true to send debug data to std out rather than db.
debug = False

#the global database connection object.
conn = None

'''
Creats a MySQL db and tables.
Returns the cursor for the db.
'''
def getDB(path):
   #get MySQL connection
    global conn
    #User and password for MySQL
    conn = mysql.connector.connect(user='root', password='')
    c = conn.cursor()

    createDB(c)
    return c
'''
Create MySQL database from schema
'''
def createDB(cursor):
    cursor.execute('''
    CREATE DATABASE IF NOT EXISTS `apps`;
    ''')
    cursor.execute('''
    USE `apps`;
    ''')
    cursor.execute('''
	CREATE TABLE IF NOT EXISTS `app` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`package` TEXT NULL,
	`appname` TEXT NULL,
	PRIMARY KEY (`id`)
    );
	''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `keys` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`appID` INT(11) NOT NULL,
	`varName` TEXT NULL,
	`value` TEXT NULL,
	`filename` TEXT NULL,
	PRIMARY KEY (`id`),
	CONSTRAINT `FK__keys__app` FOREIGN KEY (`appID`) REFERENCES `app` (`id`)
    );
	''')
    cursor.execute('''
	CREATE TABLE IF NOT EXISTS `http` (
		`id` INT(11) NOT NULL AUTO_INCREMENT,
		`appID` INT(11) NOT NULL,
		`type` TEXT NULL,
		`filename` TEXT NULL,
		`value` TEXT NULL,
        PRIMARY KEY (`id`),
        CONSTRAINT `FK__http__app` FOREIGN KEY (`appID`) REFERENCES `app` (`id`)
	);
	''')
    cursor.execute('''
	CREATE TABLE IF NOT EXISTS `libraries` (
		`id` INT(11) NOT NULL AUTO_INCREMENT,
		`appID` INT(11) NOT NULL,
		`filename` TEXT NULL,
		`library` TEXT NULL,
        PRIMARY KEY (`id`),
        CONSTRAINT `FK__libraries__app` FOREIGN KEY (`appID`) REFERENCES `app` (`id`)
	);
	''')

'''
Saves key data to the MySQL database
'''
def saveKey(appID, filename, keyID, value, cursor):
    if debug:
        print keyID
        print value
        #print calcEntropy(value, range_printable)
    else:
        cursor.execute("INSERT INTO apps.keys(appID, varName, value, filename) VALUES (%s, %s, %s, %s)", [appID, keyID, value, filename])

'''
Saves http data to the MySQL database
'''
def saveHTTP(appID, filename, conntype, urlstr, cursor):
    if debug:
        print urlstr.strip()
    else:
        cursor.execute("INSERT INTO apps.http(appID, type, filename, value) VALUES (%s, %s, %s, %s)", [appID, conntype, filename, urlstr])
'''
Saves app information to the MySQL database.
Returns the database ID.
'''
def saveApp(package, appName, cursor):
    cursor.execute("INSERT INTO apps.app(package, appname) VALUES (%s, %s)", [package, appName])
    if cursor.lastrowid != None:
            return cursor.lastrowid
    else:
            return -1

            
'''
Saves library import to the database
'''
def saveLibrary(appID, filename, library, cursor):
    if debug:
        print library
    cursor.execute("INSERT INTO apps.libraries(appID, filename, library) VALUES(%s, %s, %s)", [appID, filename, library] )
            
'''
Cleans up and commits any dirty database data.
'''
def close():
    global conn
    if conn != None:
        conn.commit()
    else:
        print " CONN= NONE!"
