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
        line = line.split()
        queryType = line[0]
        queryName = line[1]
        # qItems represent the actual words that are being looked for in the query
        qItems = line[2:]
        # and type query
        #=============== AND TYPE QUERY =================
        if queryType == "and":
            tempSet1 = set()
            for e in qItems:
                # no spaces in query
                # single word query
                # if ' ' not in e:
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
                # # space in query
                # # multi word query
                # else:
                #     # e is now a phrase of words which we are looking for
                #     # specifically, we are attempting to see which documents contain this phrase of words
                #     e = e.split()
                #     tempSet2 = set()
                #     # the way I am implementing this is to use a counter system
                #     # first, we are going to look for documents that contain word 1
                #     # for each document that contains word one, we are going to check if that document also contains word two

            # converting our set to a list for easier sorting
            tempList = list(tempSet1)
            tempList.sort()
            for i in range(len(tempList)):
                string = '{0: <15}'.format(queryName) + ' skip ' + '{0: <20}'.format(tempList[i]) + '{0: <5}'.format(str(i+1)) + '{:.3f}'.format(1.0) + ' mjchen' + '\n'
                toWrite.write(string)
        #=============== OR TYPE QUERY =================
        elif queryType == "or":
            tempSet = set()
            for e in qItems:
                # index[e] tells us every docID which contains the word e
                # x is essentially every 
                for x in index['data'][e]:
                    tempSet.add(x)
            tempList = list(tempSet)
            tempList.sort()
            for i in range(len(tempList)):
                string = '{0: <15}'.format(queryName) + ' skip ' + '{0: <20}'.format(tempList[i]) + '{0: <5}'.format(str(i+1)) + '{:.3f}'.format(1.0) + ' mjchen' + '\n'
                toWrite.write(string)
        #=============== QL TYPE QUERY =================
        elif queryType == "ql":
            tempSet = set()
            # first, generate a list of documents that contains any of the words
            # can copy or function
            for e in qItems:
                for x in index['data'][e]:
                    tempSet.add(x)
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
                    if e in index['data'][q]:
                        f = len(index['data'][q][e])
                    else:
                        f = 0
                    # c represnets the number of times a query word appears in the entire collection
                    # first check the cache to see if the value is already there
                    if q not in cCache:
                        c = 0
                        for x in index['data'][q]:
                            c = c + len(index['data'][q][x])
                        cCache[q] = c
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
            tempSet = set()
            # first, generate a list of documents that contains any of the words
            # can copy or function
            for e in qItems:
                for x in index['data'][e]:
                    tempSet.add(x)

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
            # for each document
            for e in tempSet:
                # print(e)
                score = 0
                # calculating normalization function
                # dl is the length of the document (document e)
                dl = index['stats'][e]
                # print('dl: ' + str(dl))
                # avdl is the average document length
                avdl = index['stats']['avgWords']
                print('avdl: ' + str(avdl))
                bigK = k1 * ((1 - b) + b * (dl/avdl))
                # print()
                # print(qItems)
                # for each query term
                for q in qItems:
                    # print(q)
                    # qf is the number of time this term appears in the query
                    qf = counter[q]
                    # print('qf: ' + str(qf))
                    # we have no relevance information so R and r are both going to be 0
                    r = 0
                    # n represents the number of documents that q appears in
                    n = len(index['data'][q])
                    # print('n: ' + str(n))
                    # f represents the number of times this word appears in the document we are scoring
                    if e not in index['data'][q]:
                        f = 0
                    else:
                        f = len(index['data'][q][e])
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
                print(score)
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
