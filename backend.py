import sqlite3

#Set this to true to send debug data to std out rather than db.
debug = False

#the global database connection object.
conn = None

'''
Creats a SQLite db and tables.
Returns the cursor for the db.
'''
def getDB(path):
   #get SQLite connection
    global conn
    conn = sqlite3.connect(path)
    c = conn.cursor()

    createDB(c)
    return c
'''
Create SQLite database from schema
'''
def createDB(cursor):
    cursor.execute('''
	CREATE TABLE IF NOT EXISTS app (
		id INTEGER PRIMARY KEY UNIQUE,
		package TEXT,
		appname TEXT
	);
	''')
    cursor.execute('''
	CREATE TABLE IF NOT EXISTS keys (
		id INTEGER PRIMARY KEY UNIQUE,
		appID INTEGER,
		varName TEXT,
		value TEXT,
		filename TEXT,
		FOREIGN KEY(appID) REFERENCES app(id)
	);
	''')
    cursor.execute('''
	CREATE TABLE IF NOT EXISTS http (
		id INTEGER PRIMARY KEY UNIQUE,
		appID INTEGER,
		type TEXT,
		filename TEXT,
		value TEXT,
                FOREIGN KEY(appID) REFERENCES app(id)
	);
	''')

'''
Saves key data to the SQLite database
'''
def saveKey(appID, filename, keyID, value, cursor):
    if debug:
        print keyID
        print value
        #print calcEntropy(value, range_printable)
    else:
        cursor.execute("INSERT INTO keys VALUES (?, ?, ?, ?, ?)",
            [None,  # let sqlite3 pick an ID for us
            appID, keyID, value, filename])

'''
Saves http data to the SQLite database
'''
def saveHTTP(appID, filename, urlstr, cursor):
    if debug:
        print urlstr.strip()
    else:
        cursor.execute("INSERT INTO http VALUES (?, ?, ?, ?, ?)",
        [None,  # let sqlite3 pick an ID for us
        appID, 'http', filename, urlstr])
'''
Saves app information to the SQLite database.
Returns the database ID.
'''
def saveApp(package, appName, cursor):
    cursor.execute("INSERT INTO app VALUES (?, ?, ?)",
        [None,  # let sqlite3 pick an ID for us
        package, appName])
    if cursor.lastrowid != None:
            return cursor.lastrowid
    else:
            return -1

'''
Cleans up and commits any dirty database data.
'''
def close():
    global conn
    if conn != None:
        conn.commit()
    else:
        print " CONN= NONE!"
