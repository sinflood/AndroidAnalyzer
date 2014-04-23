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
   #get MySQL connectionsaveKe
    global conn
    #User and password for MySQL
    conn = mysql.connector.connect(user='root', password='craig', buffered=True)
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
    `shortFileNames` INT(11) NULL,
    `longFileNames` INT(11)NULL,
    `shortAlphaFileNameCountContig` INT(11)NULL,
    `shortAlphaFileNameCount` INT(11)NULL,
	PRIMARY KEY (`id`)
    );
	''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `keys` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`appID` INT(11) NOT NULL,
	`varName` TEXT NULL,
	`value` TEXT NULL,
	`keytype` TEXT NULL,
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
	CREATE TABLE IF NOT EXISTS `httpParams` (
		`id` INT(11) NOT NULL AUTO_INCREMENT,
		`httpID` INT(11) NOT NULL,
		`orderNum` INT(11),
		`type` TEXT NULL,
		`value` TEXT NULL,
        PRIMARY KEY (`id`),
        CONSTRAINT `FK__httpParams__http` FOREIGN KEY (`httpID`) REFERENCES `http` (`id`)
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
def saveKey(appID, filename, keyID, keytype, value, cursor):
    if debug:
        print keyID
        print value
        #print calcEntropy(value, range_printable)
    else:
        cursor.execute("INSERT INTO apps.keys(appID, varName, value, keytype, filename) VALUES (%s, %s, %s, %s, %s)", [appID, keyID, value, keytype, filename])
        return cursor.lastrowid
    
def getKey(variable, appID, cursor):
    if debug:
        print variable
        print appID
    else:
        cursor.execute("select id from apps.keys where appID = " + str(appID) + " and varName = '" + str(variable) + "'")
        res = cursor.fetchone()
        if res != None:
            return res[0]

def updateKeyType(keyID, keytype, cursor):
    if debug:
        print keyID
        print keytype
    else:
        cursor.execute("update apps.keys set keytype= '" + keytype + "' where id = " + str(keyID))
        return cursor.lastrowid
'''
Saves http data to the MySQL database
'''
def saveHTTP(appID, filename, conntype, urlstr, cursor):
    if debug:
        print urlstr.strip()
    else:
        cursor.execute("INSERT INTO apps.http(appID, type, filename, value) VALUES (%s, %s, %s, %s)", [appID, conntype, filename, urlstr])
        return cursor.lastrowid

def saveHTTPParam(httpID, order, paramType, value, cursor):
    if debug:
        print httpID
        print value
    else:
        cursor.execute("INSERT INTO apps.httpParams(httpID, orderNum, type, value) VALUES (%s, %s, %s, %s)", [httpID, order, paramType, value])
        return cursor.lastrowid
'''
Saves app information to the MySQL database.
Returns the database ID.
'''
def saveApp(package, appName, cursor, shortFileNames, longFileNames):
    cursor.execute("INSERT INTO apps.app(package, appname, shortFileNames, longFileNames) VALUES (%s, %s, %s, %s)", [package, appName, shortFileNames, longFileNames])
    if cursor.lastrowid != None:
            return cursor.lastrowid
    else:
            return -1

'''
Updates app information with filename length counts
'''
def saveFileNameLengths(appID, cursor, shortFileNames, longFileNames, shortAlphaFileNameCountContig, shortAlphaFileNameCount):
    cursor.execute("UPDATE apps.app SET shortFileNames = %s, longFileNames = %s, shortAlphaFileNameCountContig = %s, shortAlphaFileNameCount = %s WHERE id = %s", [shortFileNames, longFileNames, shortAlphaFileNameCountContig, shortAlphaFileNameCount, appID])
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
    return cursor.lastrowid
'''
Cleans up and commits any dirty database data.
'''
def commit():
    global conn
    if conn != None:
        conn.commit()            
'''
Cleans up and commits any dirty database data.
'''
def close():
    global conn
    if conn != None:
        conn.commit()
    else:
        print " CONN= NONE!"
