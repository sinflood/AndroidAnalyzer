import argparse, os
import math, string, sys, fileinput, traceback
import re
from random import choice
import backend

doKeyAnalysis = True
doHTTPAnalysis = False
doTwitterAnalysis = True
doDropboxAnalysis = True
doLibraryImports = True

saveProgressToLog = False
resumeProgressFromLog = False
logFile = 'progress.log'

#NOT config parameters. Don't change
resumeFlag = False
lastFileParsed = ''


'''
Iterate files in application's directory and analyze each file
'''
def processApp(path, dictionary, max_len, c):
    global resumeFlag
    global resumeProgressFromLog
    global saveProgressToLog
    
    # derive package name from PlayDrone formated directory title
    tmpPath, packageNameWithNumber = os.path.split(path)
    packageName, playDroneNumber = packageNameWithNumber.split('-')

    appID = backend.saveApp(packageName, path, c, 0, 0) #TODO: fix package name
    #for each file in directory(recursive)
    shortFileNames = 0
    longFileNames = 0
    alphabeticalFileNameBuckets = [0]*26
    for root, dirs, files in os.walk(path):
        for f in sorted(files):
            if f.endswith('.java'):
                if(resumeProgressFromLog):
                    if(not resumeFlag):
                        if(lastFileParsed == os.path.join(root, f)):
                            resumeFlag = True
                            continue #We just reached the point where the last run exited
                        else:
                            continue #We haven't yet reaced the point where the last run exited
                    #else do nothing (we had reached the point of resuming in some previous iteration
                #else fo nothing (we are not resuming progress from log) 
                           
                processJavaFile(os.path.join(root, f), appID, dictionary, max_len, c)
                #print 'Processing', os.path.join(root, f)
                if(saveProgressToLog):    
                    lf = open(logFile, 'w')
                    lf.write(os.path.join(root, f))
                    lf.close()
                if len(f.split('.')[0]) == 1:
                    shortFileNames += 1
                    alphaIndex = ord(f.split('.')[0]) - ord('a')
                    if alphaIndex >= 0 and alphaIndex < 26:
                        alphabeticalFileNameBuckets[alphaIndex] = 1
                else:
                    longFileNames += 1
    # concluded walk through all source code
    shortAlphabeticalFileNamesContiguous = 0
    shortAlphaFileNameCount = 0
    keepCountingContiguous = True
    for x in range(0, 25):
        val = alphabeticalFileNameBuckets[x]
        shortAlphaFileNameCount += val
        
        if val == 0 and keepCountingContiguous:
            keepCountingContiguous = False
        if keepCountingContiguous:
            shortAlphabeticalFileNamesContiguous += val
    containsADotJava = alphabeticalFileNameBuckets[0]
    try:
        backend.saveFileNameLengths(appID, c, shortFileNames, longFileNames, shortAlphabeticalFileNamesContiguous, shortAlphaFileNameCount, containsADotJava)
    except:
        traceback.print_exc(file=sys.stdout)

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

def handleTwitter(appID, filename, toks, line, cursor):
    #print line.strip()
    params = '('.join(line.split('(')[1:]).strip()[:-2]
    paramList = params.split(',')
    
    if 'setOAuthConsumer(' in line and len(paramList) >=2:
        keyval = paramList[1]
        if keyval.strip().startswith('"'):
            backend.saveKey(appID, filename, None, 'Twitter', keyval, c)
        else: #we have a variable. Check to see if we have seen it before.
            if not 'String ' in keyval: #make sure this isn't a method declaration
                #print "Keyval: " + keyval
                endpiece = keyval.split('.')[-1]
                res = backend.getKey(endpiece, appID, c)
                if res != -1 and res != None:
                    print "Success twitter: " + str(res)
                    backend.updateKeyType(res, 'Twitter', cursor)
                elif keyval.startswith('getString('):
                    backend.saveKey(appID, filename, keyval, 'Twitter', None, c)
                else:
                    if not 'twitter4j' in filename: #some apps were adding the library as source code. This omits those files.
                        print "failed twitter: " + keyval
                        print line.strip()
                        print "----------------------------"
                        lf = open("./missedLines.txt", 'a')
                        lf.write("------------------------------------------------------------\n")
                        lf.write("Missed Twitter call. App id: "+ str(appID) + " file: " + filename + "\n")
                        lf.write(line.strip()+ "\n")
                        lf.write("------------------------------------------------------------"+ "\n")
                        lf.close()
                
    if 'setOAuthConsumerSecret' in line and not line.strip().startswith('//') and len(paramList)>= 1:
        keyval = paramList[0]
        if keyval.strip().startswith('"'):
            backend.saveKey(appID, filename, None, 'Twitter', keyval, c)
        else: #we have a variable. Check to see if we have seen it before.
            if not 'String ' in keyval: #make sure this isn't a method declaration
                #print "Keyval: " + keyval
                endpiece = keyval.split('.')[-1]
                res = backend.getKey(endpiece, appID, c)
                if res != -1 and res != None:
                    print "Success twitter: " + str(res)
                    backend.updateKeyType(res, 'Twitter', cursor)
                elif keyval.startswith('getString('):
                    backend.saveKey(appID, filename, keyval, 'Twitter', None, c)
                else:
                    if not 'twitter4j' in filename: #some apps were adding the library as source code. This omits those files.
                        print "failed twitter: " + keyval
                        print line.strip()
                        print "----------------------------"
                        lf = open("./missedLines.txt", 'a')
                        lf.write("------------------------------------------------------------"+ "\n")
                        lf.write("Missed Twitter call. App id: "+ str(appID) + " file: " + filename+ "\n")
                        lf.write(line.strip()+ "\n")
                        lf.write("------------------------------------------------------------"+ "\n")
                        lf.close()
                

def handleDropbox(appID, filename, toks, line, cursor):
    #print line.strip()
    params = '('.join(line.split('(')[1:]).strip()[:-2]
    paramList = params.split(',')
    if len(paramList) >=2:
        keyval = paramList[1]
        if keyval.strip().startswith('"'):
            #print "found key: " + keyval
            keyval = keyval.strip().strip(')').strip('"')
            backend.saveKey(appID, filename, None, 'Dropbox', keyval, c)
        else: #we have a variable. Check to see if we have seen it before.
            if not 'String ' in keyval: #make sure this isn't a method declaration
                #print "Keyval: " + keyval
                endpiece = keyval.split('.')[-1]
                res = backend.getKey(endpiece, appID, c)
                if res != -1 and res != None:
                    #print "Success Dropbox: " + str(res)
                    backend.updateKeyType(res, 'Dropbox', cursor)
                
                else:
                    print "failed Dropbox: "
                    lf = open("./missedLines.txt", 'a')
                    lf.write("------------------------------------------------------------"+ "\n")
                    lf.write("Missed Dropbox call. App id: "+ str(appID) + " file: " + filename+ "\n")
                    lf.write(line.strip()+ "\n")
                    lf.write("------------------------------------------------------------"+ "\n")
                    lf.close()
    else:
        print "failed Dropbox: "
        lf = open("./missedLines.txt", 'a')
        lf.write("------------------------------------------------------------"+ "\n")
        lf.write("Missed Dropbox call. App id: "+ str(appID) + " file: " + filename+ "\n")
        lf.write(line.strip()+ "\n")
        lf.write("------------------------------------------------------------"+ "\n")
        lf.close()

'''                
Pull out features from a single Java file and save to database.
'''
def processJavaFile(filename, appID, dictionary, max_len, c):
    try:
        #print"Processing Java file " + filename
        f = open(filename, 'r')
        facebookUse = False        
        for line in f:
            if "com.facebook" in line:
                facebookUse = True
                #print "found facebook use"
            toks = line.lower().strip().split()
            #print line.strip()
            if doKeyAnalysis:
                if ('static' in toks or 'final' in toks) and 'string' in toks and '=' in toks and not 'tag' in toks:
                    #This is a static final string.
                    #split the variable declaration from it's value
                   
                    valspl = line.lower().strip().split('=')
                    #get the name of the variable
                    varname = valspl[0].split()[-1] #[-1] is last item in list
                    #clean up the value data
                    val = valspl[1].strip().strip(';').strip('"')
                    #print "found something: " + str(val)
                    #check if key
                    if not '.' in val and not '_' in val and not ' ' in val and not val.startswith('abcdef') and not val.startswith('0123456') and not val.startswith('x-ebay') and not val.startswith('()<>')and not val.startswith('yyyy'):
                        if len(val) > 14 and(valspl[1].strip().startswith('"') or valspl[1].strip().startswith("'")):
                            if findWords(val, dictionary, max_len, MIN) ==0:
                                #print "FOUND KEY!!!!\n" + line
                                #if calcEntropy(valspl[1].strip().strip('"'), range_printable) > 2.5:
                                keyType = None
                                if facebookUse or varname == "fb_app_signature":
                                    #print "found facebook key"
                                    keyType = "Facebook"
                                if varname == 'dropbox_app_secret':
                                    #print "FOUND DROPBOX!"
                                    keyType = "Dropbox"
                                if 'twitter' in varname:
                                    #print "FOUND DROPBOX!"
                                    keyType = "Twitter"
                                if val.startswith('AKIA') or val.startswith('akia'):
                                    keyType = "AWS"                                    
                                #print "Creating new key: " + str(val)
                                backend.saveKey(appID, filename, varname, keyType, val, c)
            if doHTTPAnalysis:
                '''
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
            if doTwitterAnalysis:
                if 'setOAuthConsumer' in line:
                    #get second param of call
                    #if constant, then add to keys
                    #if var, try to lookup in keys
                        #if found, update keys with type twitter
                    #if not found, create new key entry with just var name and type (no value)
                    #print 'found twitter!'
                    handleTwitter(appID, filename, toks, line, c)
            if doDropboxAnalysis:
                if "new AppKeyPair("  in line:
                    #get second param of call
                    #if constant, then add to keys
                    #if var, try to lookup in keys
                        #if found, update keys with type twitter
                    #if not found, create new key entry with just var name and type (no value)
                    #print 'found twitter!'
                    handleDropbox(appID, filename, toks, line, c) 
            
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
        #print library," is interesting"
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

if(resumeProgressFromLog):
    if(os.path.isfile(logFile)):
        f = open(logFile, 'r')
        lastFileParsed = f.readline()
        f.close()
        if(lastFileParsed == ''):
            resumeFlag = True
    else:
        print 'Progress log not found. Restarting parsing from beginning'
        resumeProgressFromLog = False
    
#for each directory in the input directory
for d in os.walk( os.path.join(args.directory,'.')).next()[1]:
    print "dir " + os.path.join(args.directory,d)
    processApp(os.path.join(args.directory,d), dictionary, max_len, c)
    try:
        backend.commit()
    except:
        traceback.print_exc(file=sys.stdout)

backend.close()

print "done"
