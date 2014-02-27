import argparse, os
import math, string, sys, fileinput
from random import choice
import backend

doKeyAnalysis = True
doHTTPAnalysis = False

'''
Iterate files in application's directory and analyze each file
'''
def processApp(path, dictionary, max_len, c):
    appID = backend.saveApp('something', path, c) #TODO: fix package name
    #for each file in directory(recursive)
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.java'):
                processJavaFile(os.path.join(root, f), appID, dictionary, max_len, c)
                
'''                
Pull out features from a single Java file and save to database.
'''
def processJavaFile(filename, appID, dictionary, max_len, c):
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
                        #if calcEntropy(valspl[1].strip().strip('"'), range_printable) > 2.5:
                        backend.saveKey(appID, filename, varname, val, c)
        if doHTTPAnalysis:
            if 'httpget' in toks or 'httpurlconnection' in toks:
                backend.saveHTTP(appID, filename, line, c)
                




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

