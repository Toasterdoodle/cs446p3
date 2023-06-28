# import package ...
import gzip
import json
import math
import sys


def buildIndex(inputFile):
    index = dict()
    # key of index['data']: terms
    # value of index['data']: another dictionary with the key being doc-ids
    # the value of that dictionary will then be a list containing all the positions that the term appears in
    f = gzip.open(inputFile, 'r')
    toWrite = open('indexChecker.json', 'w')
    data = json.load(f)
    # totWords keeps track of how many words are in the corpus in total
    totWords = 0
    # totDocs represents the total number of documents in the corpus
    totDocs = 0
    # keeping track of longest doc
    longestDoc = None
    # keeping track of shortest doc
    shortestDoc = None
    # key of index['stats']: statistics regarding how many words exist total in each document, and totwords
    index['data'] = dict()
    index['stats'] = dict()
    for e in data['corpus']:
        # variable to contain how many words are within a certain document
        docWords = 0
        totDocs = totDocs + 1
        text = e['text']
        text = text.split()
        for i in range(len(text)):
            docWords = docWords + 1
            totWords = totWords + 1
            # important: text is 1-indexed
            # so begin with 1 and then move on
            # if the term does not yet exist inside of our index
            if text[i] not in index['data']:
                # add the term to our index and create a new dict to keep track of story IDs and indices
                index['data'][text[i]] = dict()
                # if the storyID has not been encountered yet
                if e['storyID'] not in index['data'][text[i]]:
                    index['data'][text[i]][e['storyID']] = []
                # add 1 since index begins at 1
                index['data'][text[i]][e['storyID']].append(i+1)
            else:
                # if the storyID has not been encountered yet
                if e['storyID'] not in index['data'][text[i]]:
                    index['data'][text[i]][e['storyID']] = []
                index['data'][text[i]][e['storyID']].append(i+1)
        index['stats'][e['storyID']] = docWords
        # calculating shortest and longest documents
        if shortestDoc == None:
            shortestDoc = docWords
        elif docWords < shortestDoc:
            shortestDoc = docWords
        if longestDoc == None:
            longestDoc = docWords
        elif docWords > longestDoc:
            longestDoc = docWords

    index['stats']['totWords'] = totWords
    index['stats']['totDocs'] = totDocs
    # avgWords represents the average number of words per doc
    index['stats']['avgWords'] = totWords/totDocs
    index['stats']['longestDoc'] = longestDoc
    index['stats']['shortestDoc'] = shortestDoc
    # print(index)
    json.dump(index, toWrite)
    return index

# helper function to run the or function
# will take in an index, and the query items, and will return a set containing all the items with that query
def runOr(index, qItems):
    tempSet = set()
    for e in qItems:
        # if there are no phrases (no spaces)
        if ' ' not in e:
        # index[e] tells us every docID which contains the word e
        # x is essentially every 
            for x in index['data'][e]:
                tempSet.add(x)
        # if there exists a phrase
        else:
            e = e.split()
            tempSet = set()
            for x in index['data'][e[0]]:
                for y in index['data'][e[0]][x]:
                    if checkPhrase(index, e, y, x) == True:
                        tempSet.add(x)
                        break
    return tempSet

# helper function to run the and function
def runAnd(index, qItems):
    tempSet1 = set()
    for e in qItems:
        # no spaces in query
        # single word query
        if ' ' not in e:
            tempSet2 = set()
            # index[e] tells us every docID which contains the word e
            for x in index['data'][e]:
                # this compiles a set which contains every docID that contains this word
                tempSet2.add(x)
            if len(tempSet1) == 0:
                tempSet1 = tempSet2
            else:
                # we want to find articles that have ALL the terms
                # that's why we want to keep taking the intersection-
                tempSet1 = tempSet1.intersection(tempSet2)
        # space in query
        # multi word query
        else:
            # e is now a phrase of words which we are looking for
            # specifically, we are attempting to see which documents contain this phrase of words
            e = e.split()
            tempSet2 = set()
            # start with the first word in the wordList
            # and then check if the rest of the words follow
            # remember, x is the key within a dictionary containing the name of all documents containing
            # a certain word
            for x in index['data'][e[0]]:
                # y represents every index of the occurance of word e[0] within document x
                for y in index['data'][e[0]][x]:
                    if checkPhrase(index, e, y, x) == True:
                        tempSet2.add(x)
                        break
            if len(tempSet1) == 0:
                tempSet1 = tempSet2
            else:
                tempSet1 = tempSet1.intersection(tempSet2)
    return tempSet1

# given a list of words, an index to start at, and a document name,
# this function will return if the next n words starting at startIndex match the phrase given in wordList
def checkPhrase(index, wordList, startIndex, docName):
    # this essentially starts at the first index and says
    # does the index we are looking for exist within this word and this document?
    # if the answer is no, we return false
    # if the answer is yes FOR EVERY WORD IN wordList, we return true
    # this allows us to know if there is a phrase beginning at startIndeex
    for i in range(len(wordList)):
        # if the next word does not exist within the document
        if docName not in index['data'][wordList[i]]:
            # print(wordList[i] + ' does not exist within document ' + docName)
            return False
        else:
            # if it does exist but is not in the correct position
            if startIndex + i not in index['data'][wordList[i]][docName]:
                # print(wordList[i] + ' does not exist within document ' + docName + ' at position ' + str(startIndex + i))
                return False
        # print(wordList[i] + ' found in ' + docName + ' at ' + str(startIndex + i))
    return True

# return statistics for analysis questions
def returnStats(index):
    # calculate which word returns in the most stories
    storyCount = 0
    word = None
    for e in index['data']:
        if len(index['data'][e]) > storyCount:
            storyCount = len(index['data'][e])
            word = e
    print('word: ' + word)
    print('Story Count: ' + str(storyCount))
    # calculate which word appears the most
    word = None
    wordCount = 0
    for e in index['data']:
        count = 0
        for s in index['data'][e]:
            count = count + len(index['data'][e][s])
        if count > wordCount:
            word = e
            wordCount = count
    print('word: ' + word)
    print('word count: ' + str(wordCount))
    numUniqueWords = len(index['data'])
    numUniqueWordsApperaingOnce = 0
    for e in index['data']:
        if len(index['data'][e]) == 1:
            for s in index['data'][e]:
                if len(index['data'][e][s]) == 1:
                    numUniqueWordsApperaingOnce = numUniqueWordsApperaingOnce + 1
    print('number of unique words: ' + str(numUniqueWords))
    print('number of unique words apperaing once: ' + str(numUniqueWordsApperaingOnce))
    print('percentage: ' + str(numUniqueWordsApperaingOnce/numUniqueWords))

def runQueries(index, queriesFile, outputFile):
    # this is a dictionary to store the total number of a specific word within the entire collection
    # given a specific word
    cCache = dict()
    toWrite = open(outputFile, 'w')
    queryFile = open(queriesFile, 'r')
    for line in queryFile:
        # this is to remove the newLine character at the end
        line = line.replace('\n', '')
        # splitting based on tabs
        line = line.split('\t')
        # print(line)
        queryType = line[0]
        queryName = line[1]
        # qItems represent the actual words that are being looked for in the query
        qItems = line[2:]
        # and type query
        #=============== AND TYPE QUERY =================
        if queryType == "and":
            tempSet1 = runAnd(index, qItems)

            # converting our set to a list for easier sorting
            tempList = list(tempSet1)
            tempList.sort()
            for i in range(len(tempList)):
                string = '{0: <15}'.format(queryName) + ' skip ' + '{0: <20}'.format(tempList[i]) + '{0: <5}'.format(str(i+1)) + '{:.3f}'.format(1.0) + ' mjchen' + '\n'
                toWrite.write(string)
        #=============== OR TYPE QUERY =================
        elif queryType == "or":
            tempSet = runOr(index, qItems)

            tempList = list(tempSet)
            tempList.sort()
            for i in range(len(tempList)):
                string = '{0: <15}'.format(queryName) + ' skip ' + '{0: <20}'.format(tempList[i]) + '{0: <5}'.format(str(i+1)) + '{:.3f}'.format(1.0) + ' mjchen' + '\n'
                toWrite.write(string)
        #=============== QL TYPE QUERY =================
        elif queryType == "ql":
            tempSet = set()
            # first, generate a list of documents that contains any of the words
            # can use or function
            tempSet = runOr(index, qItems)
            # no need to sort this time tho
            # and we can keep it as a set:
            # create a new variable called tempList
            # this is what we are going to use to store the document-score pairs
            # we are using a list so we can sort it
            tempList = []
            for e in tempSet:
                # calculate the score here
                score = 0
                # for each word in the query
                for q in qItems:
                    # f represnets how many times a word appears in a specific document
                    # e is the document

                    # q is the query
                    # assuming that q is a one word query
                    if ' ' not in q:
                        if e in index['data'][q]:
                            f = len(index['data'][q][e])
                        else:
                            f = 0
                    # if q is a multi word query (has a space in it)
                    else:
                        # need to calculate how many times a phrase appears in a certain document
                        f = 0
                        tempQ = q.split()
                        if e in index['data'][tempQ[0]]:
                            for i in index['data'][tempQ[0]][e]:
                                if checkPhrase(index, tempQ, i, e) == True:
                                    f = f + 1
                        # print('f adjusted for phrases: ' + str(f))

                    # c represnets the number of times a query word appears in the entire collection
                    # first check the cache to see if the value is already there
                    if q not in cCache:
                        if ' ' not in q:
                            c = 0
                            for x in index['data'][q]:
                                c = c + len(index['data'][q][x])
                            cCache[q] = c
                        else:
                            tempQ = q.split()
                            c = 0
                            for x in index['data'][tempQ[0]]:
                                for i in index['data'][tempQ[0]][x]:
                                    if checkPhrase(index, tempQ, i, x) == True:
                                        c = c + 1
                    else:
                        c = cCache[q]
                    # u is a constant as described by the moodle page
                    u = 300
                    # total number of words in the corpus
                    bigC = index['stats']['totWords']
                    bigD = index['stats'][e]
                    numerator = f + u * c/bigC
                    denominator = bigD + u
                    ans = numerator / denominator
                    ans = math.log(ans)
                    score = score + ans
                tempList.append([e, score])
            tempList.sort()
            tempList.sort(key=lambda x: x[1], reverse=True)
            # print(tempList)
            # now we need to print to our output file
            for i in range(len(tempList)):
                string = '{0: <15}'.format(queryName) + ' skip ' + '{0: <20}'.format(tempList[i][0]) + '{0: <5}'.format(str(i+1)) + '{:.4f}'.format(tempList[i][1]) + ' mjchen' + '\n'
                toWrite.write(string)
        #=============== BM25 TYPE QUERY =================
        elif queryType == "bm25":
            # first, generate a list of documents that contains any of the words
            # can copy or function
            tempSet = runOr(index, qItems)

            # intilizing constants as defined in the project
            k1 = 1.8
            k2 = 5
            b = 0.75
            # since we have no relevance information
            bigR = 0
            # total number of documents
            bigN = index['stats']['totDocs']
            counter = dict()

            # building counter quickly
            for e in qItems:
                if e not in counter:
                    counter[e] = 1
                else:
                    counter[e] = counter[e] + 1

            # doing actual calculations
            # initializing a tempList to contain document-score pairings
            tempList = []
            # for each document e
            for e in tempSet:
                # print(e)
                score = 0
                # calculating normalization function
                # dl is the length of the document (document e)
                dl = index['stats'][e]
                # print('dl: ' + str(dl))
                # avdl is the average document length
                avdl = index['stats']['avgWords']
                # print('avdl: ' + str(avdl))
                bigK = k1 * ((1 - b) + b * (dl/avdl))
                # print()
                # print(qItems)
                # for each query term q
                for q in qItems:
                    # print(q)
                    # qf is the number of time this term appears in the query
                    qf = counter[q]
                    # print('qf: ' + str(qf))
                    # we have no relevance information so R and r are both going to be 0
                    r = 0
                    # n represents the number of documents that q appears in
                    # if there is no space within q (one word)
                    if ' ' not in q:
                        n = len(index['data'][q])
                    # q is a phrase
                    else:
                        # need to find how many documents this phrase appears in
                        # can use runOr function
                        n = len(runOr(index, [q]))
                        # print('n adjusted for phrase: ' + str(n))
                    # print('n: ' + str(n))
                    # f represents the number of times this word appears in the document we are scoring
                    # if q is not a phrase
                    if ' ' not in q:
                        if e not in index['data'][q]:
                            f = 0
                        else:
                            f = len(index['data'][q][e])
                    else:
                        # if q is a phrase
                        # we now need to find how many times this phrase appears in the document we are seraching
                        f = 0
                        # print('phrase detected, running algorithm')
                        tempQ = q.split()
                        # print(tempQ)
                        # print(tempQ[0])
                        # print(e)
                        if e in index['data'][tempQ[0]]:
                            # print('first word exists within document, running algorithm')
                            for i in index['data'][tempQ[0]][e]:
                                # print(i)
                                if checkPhrase(index, tempQ, i, e) == True:
                                    f = f + 1
                        # print('f adjusted for phrases: ' + str(f))

                    # print('f: ' + str(f))
                    # now for the actual math
                    # for num1
                    numerator = (r + 0.5)/(bigR - r + 0.5)
                    denominator = (n - r + 0.5)/(bigN - n - bigR + r + 0.5)
                    num1 = numerator/denominator
                    # for num2
                    numerator = (k1 + 1) * f
                    denominator = bigK + f
                    num2 = numerator / denominator
                    # for num3
                    numerator = (k2 + 1) * qf
                    denominator = k2 + qf
                    num3 = numerator / denominator
                    # calculating overall score for this term
                    tempScore = math.log(num1) * num2 * num3
                    score = score + tempScore
                # print(score)
                # appending this doc-score pairing to the overall list
                tempList.append([e, score])
            # sort first by document name
            tempList.sort()
            # sort again by score
            tempList.sort(key=lambda x: x[1], reverse=True)
            for i in range(len(tempList)):
                string = '{0: <15}'.format(queryName) + ' skip ' + '{0: <20}'.format(tempList[i][0]) + '{0: <5}'.format(str(i+1)) + '{:.4f}'.format(tempList[i][1]) + ' mjchen' + '\n'
                toWrite.write(string)

if __name__ == '__main__':
    # Read arguments from command line, or use sane defaults for IDE.
    argv_len = len(sys.argv)
    inputFile = sys.argv[1] if argv_len >= 2 else "sciam.json.gz"
    queriesFile = sys.argv[2] if argv_len >= 3 else "trainQueries.tsv"
    outputFile = sys.argv[3] if argv_len >= 4 else "trainQueries.trecrun"

    index = buildIndex(inputFile)
    # if queriesFile == 'showIndex':
    #     # Invoke your debug function here (Optional)
    # elif queriesFile == 'showTerms':
    #     # Invoke your debug function here (Optional)
    # else:
    runQueries(index, queriesFile, outputFile)
    returnStats(index)

    # Feel free to change anything
