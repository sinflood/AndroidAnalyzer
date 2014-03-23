import argparse, os
import math, string, sys, fileinput, traceback
import re
from random import choice
import backend

doKeyAnalysis = True
doHTTPAnalysis = True
doLibraryImports = True

'''
Iterate files in application's directory and analyze each file
'''
def processApp(path, dictionary, max_len, c):
    appID = backend.saveApp('something', path, c, 0, 0) #TODO: fix package name
    #for each file in directory(recursive)
    shortFileNames = 0
    longFileNames = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.java'):
                processJavaFile(os.path.join(root, f), appID, dictionary, max_len, c)
                if len(f.split('.')[0]) == 1:
                    shortFileNames += 1
                else:
                    longFileNames += 1
    backend.saveFileNameLengths(appID, c, shortFileNames, longFileNames)

def handleHttpGet(httpID, toks, line, cursor):
    pieces = line.split('=')
    #print line.strip()
    if len(pieces) > 1:
        end = '='.join(pieces[1:]).strip()
        if end.startswith('new'):
            params = '('.join(end.split('(')[1:]).strip()[:-2]
            paramType = 'var'
            if params.startswith('"'):
               paramType = 'const'
            #print params
            backend.saveHTTPParam(httpID, 0, paramType, params, cursor)
   
'''                
Pull out features from a single Java file and save to database.
'''
def processJavaFile(filename, appID, dictionary, max_len, c):
    try:
        f = open(filename, 'r')
        for line in f:
            toks = line.lower().strip().split()
            if doKeyAnalysis:
                if ('static' in toks or 'final' in toks) and 'string' in toks and '=' in toks and not 'tag' in toks:
                    #This is a static final string.
                    #split the variable declaration from it's value
                    valspl = line.lower().strip().split('=')
                    #get the name of the variable
                    varname = valspl[0].split()[-1] #[-1] is last item in list
                    #clean up the value data
                    val = valspl[1].strip().strip(';').strip('"')
                    #check if key
                    if not '.' in val and not '_' in val and not ' ' in val and not val.startswith('abcdef') and not val.startswith('0123456') and not val.startswith('x-ebay') and not val.startswith('()<>')and not val.startswith('yyyy'):
                        if len(val) > 14 and(valspl[1].strip().startswith('"') or valspl[1].strip().startswith("'")):
                            if findWords(val, dictionary, max_len, MIN) ==0:
                                #print "FOUND KEY!!!!\n" + line
                                #if calcEntropy(valspl[1].strip().strip('"'), range_printable) > 2.5:
                                backend.saveKey(appID, filename, varname, val, c)
            if doHTTPAnalysis:
                '''
                Need point where actual URL is created.
                1. httpget(url)
                2. httppost(url)
                3. Not sure how to do https version of 1 or 2. Ex.:
                    http://hc.apache.org/httpcomponents-client-ga/httpclient/examples/org/apache/http/examples/client/ClientCustomSSL.java
                    http://stackoverflow.com/questions/5485415/android-java-how-to-create-https-connection
                    http://stackoverflow.com/questions/16504527/android-https-post-how-to-do
                3. http(s)urlconnection needs: URL url = new URL("http://www.android.com/");
                4. new android http 3rd party libraries
                '''
                if 'httpget' in toks or 'httppost' in toks or'httpurlconnection' in toks:
                    httpID = backend.saveHTTP(appID, filename, 'http', line, c)
                    if 'httpget' in toks or 'httppost' in toks:
                            handleHttpGet(httpID, toks, line, c)
                if 'httpsurlconnection' in toks:
                    backend.saveHTTP(appID, filename, 'https', line, c)
            
            if doLibraryImports:
                if len(toks) >= 2:
                    if toks[0] == 'import':
                        library = toks[1]
                        if interestingLibrary(library):
                            backend.saveLibrary(appID, filename, library, c)
    except:
        traceback.print_exc(file=sys.stdout)
                    
def interestingLibrary(library):
    if re.search(r'\.amazon\.', library):
        print library," is interesting"
        return True
    return False
                    
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
    #text = ''.join([choice(string.ascii_lowercase) for i in xrange(28000)])
    #text += '-'+text[::-1] #append the reverse of the text to itself
    
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
parser.add_argument("-d", "--directory", type=str,default='./decompiled',  help="The directory with the source code folders")
parser.add_argument("-o", "--outputDB", type=str,default='./results.sqlite',  help="The output database where features will be written to.")
parser.add_argument("-w", "--wordlist", type=str,default='./words.txt',  help="The wordlist for finding words in a string. ex. /usr/share/dict/words")
args = parser.parse_args()

#get SQLite cursor
c = backend.getDB(args.outputDB)


dictionary = set(open(args.wordlist,'r').read().lower().split())
max_len = max(map(len, dictionary)) #longest word in the set of words
MIN = 4
    
#for each directory in the input directory
for d in os.walk( os.path.join(args.directory,'.')).next()[1]:
    print "dir " + os.path.join(args.directory,d)
    processApp(os.path.join(args.directory,d), dictionary, max_len, c)

backend.close()

