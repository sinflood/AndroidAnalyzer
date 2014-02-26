import argparse, os
import math, string, sys, fileinput, sqlite3
from random import choice

doKeyAnalysis = True
doHTTPAnalysis = False

'''
Iterate files in application's directory and analyze each file
'''
def processApp(path, appID, dictionary, max_len):
    #for each file in directory(recursive)
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.java'):
                processJavaFile(os.path.join(root, f), appID, dictionary, max_len)
                
'''                
Pull out features from a single Java file and save to database.
'''
def processJavaFile(filename, appID, dictionary, max_len):
    f = open(filename, 'r')
    for line in f:
        toks = line.lower().strip().split()
        if doKeyAnalysis:
            if 'static' in toks and 'final' in toks and 'string' in toks and '=' in toks and not 'tag' in toks:
                #This is a static final string.
                #split the variable declaration from it's value
                valspl = line.lower().strip().split('=')
                #get the name of the variable
                varname = valspl[0].split()[-1] #[-1] is last item in list
                #clean up the value data
                val = valspl[1].strip().strip(';').strip('"')
                #check if key
                if not '.' in val and not '_' in val and not ' ' in val and len(val) > 10 and(valspl[1].strip().startswith('"') or valspl[1].strip().startswith("'")):
                    if findWords(val, dictionary, max_len, MIN) ==0: 
                        #if H(valspl[1].strip().strip('"'), range_printable) > 2.5:
                        saveKey(appID, filename, varname, val)
        if doHTTPAnalysis:
            if 'httpget' in toks or 'httpurlconnection' in toks:
                saveHTTP(appID, filename, line)
                
'''
Just prints the data to stdout. Eventually want to write data to database.
'''
def saveKey(appID, filename, keyID, value):
    print keyID
    print value
    print calcEntropy(value, range_printable)

'''
Just prints the LoC to stdout. Eventually want to write data to database.
'''
def saveHTTP(appID, filename, urlstr):
    print urlstr.strip()

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
		type TEXT,
		filename TEXT
	);
	''')

#for shannon entropy http://pythonfiddle.com/shannon-entropy-calculation/
def range_bytes (): return range(256)
def range_printable(): return (ord(c) for c in string.printable)
def calcEntropy(data, iterator=range_printable):
    if not data:
        return 0
    entropy = 0
    for x in iterator():
        p_x = float(data.count(chr(x)))/len(data)
        if p_x > 0:
            entropy += - p_x*math.log(p_x, 2)
    return entropy


'''
Returns the number of words present in a string given a wordlist.
http://stackoverflow.com/questions/19338113/how-to-find-possible-english-words-in-long-random-string
'''
def findWords(text, dictionary, max_len, minLength):
    text = ''.join([choice(string.ascii_lowercase) for i in xrange(28000)])
    text += '-'+text[::-1] #append the reverse of the text to itself

    words_found = set() #set of words found, starts empty
    for i in xrange(len(text)): #for each possible starting position in the corpus
        chunk = text[i:i+max_len+1] #chunk that is the size of the longest word
        for j in xrange(1,len(chunk)+1): #loop to check each possible subchunk
            word = chunk[:j] #subchunk
            if len(word) > minLength and word in dictionary: #constant time hash lookup if it's in dictionary
                words_found.add(word) #add to set of words
                return len(words_found)

    return len(words_found)

#Script starts here.
#parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", type=str,default='.',  help="The directory with the source code folders")
parser.add_argument("-o", "--outputDB", type=str,default='./results.sqlite',  help="The output database where features will be written to.")
parser.add_argument("-w", "--wordlist", type=str,default='./words.txt',  help="The wordlist for finding words in a string. ex. /usr/share/dict/words")
args = parser.parse_args()

#get SQLite connection
conn = sqlite3.connect(args.outputDB)
c = conn.cursor()

createDB(c)

dictionary = set(open(args.wordlist,'r').read().lower().split())
max_len = max(map(len, dictionary)) #longest word in the set of words
MIN = 4
    
#for each directory in the input directory
for d in os.walk( os.path.join(args.directory,'.')).next()[1]:
    print "dir " + os.path.join(args.directory,d)
    processApp(os.path.join(args.directory,d), d, dictionary, max_len)

