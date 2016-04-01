from __future__ import division
import codecs, sys, os, operator, random, math, time, re, cProfile, numpy
from collections import defaultdict

# This script uses half of the dictionary entries for supervision in training and half for evaluation

# read and return config info
def readConfig(infile,lang):
    config={}
    inputfile=codecs.open(infile,'r')
    line=inputfile.readline()
    while line:
        if not line[0]=="#":
            line=re.sub("\$LANG\$",lang,line)
            line=line.strip().split("=")
            if len(line)==2:
                name=line[0].strip()
                value=line[1].strip()
                config[name]=value
        line=inputfile.readline()
    return config

# open a score file and call functions to read and save its info, with the given name
def scoredFile(filename,scorename, allScores):
    print "Reading", filename, "..."
    openedfile=codecs.open(filename,'r','utf-8')
    if scorename.endswith("-pre"):
        scoredict,frwords=readCFileAffix(openedfile,True)
    elif scorename.endswith("-suf"):
        scoredict,frwords=readCFileAffix(openedfile,False)
    else:
        scoredict,frwords=readCFile(openedfile)
    if scorename not in allScores.keys():
        print "Initializing score dict for ", scorename
        allScores[scorename]={}
    allScores=addInfo(scoredict, scorename, allScores)
    return frwords, allScores #list of fr words scored in this file

# Given a particular open scored file, return dictionaries with scored parts
# Keeping this separate from addInfo (below) in case later want to do something with frequency binned output files
def readCFile(openfile, ed=False):
    scoreDict={}
    frwords=defaultdict(int)
    line=openfile.readline()
    word="NONE"
    while line:
        line=line.strip()
        if len(line)>0:
            if line[0]=="<":
                word=line.strip("<").strip(">")
                frwords[word]+=1
            else:
                # ignore the *: in some files will only be indicated on exact matches anyway, only trust the dictionary for correct translations
                if line[0]=="*":
                    line=line[1:].strip()
                line=line.split(" ")
                score=float(line[0].strip("[").strip("]"))
                translations=line[1:]
                for trans in translations:
                    trans=trans.strip()
                    if ed:
                        score=1-(score/(len(word)+len(trans))) # normalize edit distance scores
                    if word not in scoreDict:
                        scoreDict[word]={}
                    scoreDict[word][trans]=score
                    #if word.startswith("mamlakatlar"):
                    #    print word, trans
        line=openfile.readline()
    return scoreDict, frwords

# Given a particular open scored file, return dictionaries with scored parts
# Keeping this separate from addInfo (below) in case later want to do something with frequency binned output files
# This format is slightly different: all suffixes of word prefixes listed
def readCFileAffix(openfile,prefixFile=True):
    scoreDict={}
    frwords=defaultdict(int)
    line=openfile.readline()
    currentfrwords=["NONE"]
    while line:
        line=line.strip()
        if len(line)>0:
            # start of new src word
            if line[0]=="<":
                currentfrwords=[]
                if prefixFile:
                    #line=re.sub("\<|\>|\}","",line)
                    line=line.strip("<").strip(">").split("{")
                    prefix=line[0].strip()
                else:
                    #line=re.sub("\<|\>|\}","",line)
                    line=line.strip("<").strip(">").split("}")                    
                    if len(line)>1:
                        suffix=line[1].strip()
                    else:
                        suffix=line[0].strip()
                if len(line)>1:
                    if prefixFile:
                        #affixes=re.sub("\<|\>|\}","",line[1])
                        affixes=line[1].strip("}").split(", ")
                    else:
                        #affixes=re.sub("\{|\}","",line[0]).split(", ")
                        affixes=line[0].strip("{").split(", ")
                    for aff in affixes:
                        aff=aff.strip("-")
                        if prefixFile:
                            newword=prefix+aff
                        else:
                            newword=aff+suffix
                        currentfrwords.append(newword)
                        frwords[newword]+=1
                else:
                    if prefixFile:
                        currentfrwords.append(prefix)
                        frwords[prefix]+=1
                    else:
                        currentfrwords.append(suffix)
                        frwords[suffix]+=1
            # not start of new src word
            else:
                # ignore the *: in some files will only be indicated on exact matches anyway, only trust the dictionary for correct translations
                if line[0]=="*":
                    line=line[1:].strip()
                if not prefixFile:
                    line=line.replace("}","} ")
                line=line.split(" ")
                #score=float(re.sub("\[|\]","",line[0]))
                score=float(line[0].strip("[").strip("]"))
                nextword=True
                alltranslations=[]
                if prefixFile:
                    index=1
                    insideSuffixes=False
                    listofsuffixes=[]
                    while index<len(line):
                        item=line[index].strip()
                        if not insideSuffixes and len(item)>0 and not item[0]=="{":
                            alltranslations.append(item)
                        elif len(item)>0 and item[0]=="{":
                            #listofsuffixes.append(re.sub("\{|\}|,","",item.strip("-")))
                            listofsuffixes.append(item.strip("{").strip("-").strip(","))
                            insideSuffixes=True
                        elif insideSuffixes and len(item)>0:
                            #listofsuffixes.append(re.sub("\{|\}|,","",item.strip("-")))
                            listofsuffixes.append(item.strip("}").strip("-").strip(","))
                            if item[-1]=="}":
                                prevword=alltranslations[-1]
                                alltranslations[-1]=prevword+listofsuffixes[0]
                                for suf in listofsuffixes[1:]:
                                    alltranslations.append(prevword+suf)
                                insideSuffixes=False
                        index+=1
                else:
                    index=1
                    insidePrefixes=False
                    listofprefixes=[]
                    nextWordAppend=False
                    while index<len(line):
                        item=line[index].strip()
                        if not insidePrefixes and len(item)>0 and not item[0]=="{":
                            if nextWordAppend:
                                for pre in listofprefixes:
                                    alltranslations.append(pre+item)
                                listofprefixes=[]
                            else:
                                alltranslations.append(item)
                        elif len(item)>0 and item[0]=="{":
                            #listofprefixes.append(re.sub("\{|\}|,","",item.strip("-")))
                            listofprefixes.append(item.strip("{").strip("-").strip(","))
                            insidePrefixes=True
                        elif insidePrefixes and len(item)>0:
                            #listofprefixes.append(re.sub("\{|\}|,","",item.strip("-")))
                            listofprefixes.append(item.strip("{").strip("}").strip("-").strip(","))                            
                            if item[-1]=="}":
                                nextWordAppend=True
                                insidePrefixes=False
                        index+=1
                for word in currentfrwords:
                    if word in allFRWords:  #only need to remember for fr words actually in list. if using affix candidates, that's still included in en list below
                        if word not in scoreDict:
                            scoreDict[word]={}
                        for trans in alltranslations:
                            trans=trans.strip()
                            scoreDict[word][trans]=score
        line=openfile.readline()
    return scoreDict, frwords

# Given output of readCFile and name of that score, add counts to dictionary 
def addInfo(scoredict, scorename, allScores):
    for fr in scoredict:
        if fr not in allScores[scorename]:
            allScores[scorename][fr]={}
        for en in scoredict[fr]:
            allScores[scorename][fr][en]=scoredict[fr][en]
    print "Done adding score", scorename
    return allScores

# Used in feature functions. If not on a ranked list, give rank of len(sortedscores)
# Assume input is sorted!
def getRank(sortedscores,myen):
    myrank=1
    for en, score in sortedscores:
        if en==myen:
            return myrank
        else:
            myrank+=1
    return myrank

# Return dictionary of words mapped to their ranks so don't have to iterate through ranked list everytime to retrieve rank
def getWordToRankDict(sortedscores):
    outdict={}
    myrank=1
    for en, score in sortedscores:
        outdict[en]=myrank
        myrank+=1
    outdict["UNKNOWNWORD"]=myrank
    return outdict


# Given fr word and output file (train/dev/test) and list of true and false EN words, return two strings: 
# one to write to features file and one to index file
def returnFeatures(fr, allENTrue, allENFalse, swc, twc, twct, swct, sn, allSc, af, afs, burstS, burstT, idfS, idfT, varS, varT, entropyS, entropyT, downsample=False, samplevalue=0.0008, writeLabels=True):
    # Preliminaries
    allen=[]
    outfile=""
    outfileindex=""
    for x in allENTrue:
        allen.append(x)
    for x in allENFalse:
        allen.append(x)
    # For baseline comparison: lookup EN, get MRR
    baselineMRR=defaultdict(list)
    fullScorenames=[x for x in sn]
    # Sort score lists for ranking
    allsorted={}
    for scorename in sn:
        if scorename=="edit":
            allsorted[scorename]=sorted(allSc[scorename].get(fr,{}).iteritems(), key=operator.itemgetter(1), reverse=False) # lower is better
        else:
            allsorted[scorename]=sorted(allSc[scorename].get(fr,{}).iteritems(), key=operator.itemgetter(1), reverse=True) # higher is better
    # Set up frequency and burstiness features
    # TO DO: also variance and entropy? (varS, varT, entropyS, entropyT)
    freq={}
    burst={}
    idf={}
    srccount=swc[fr]
    srcBurst=burstS[fr]
    srcIDF=idfS[fr]
    for en in allen:
        trgcount=twc[en]/(twct/swct) #scale English counts to src counts
        trgBurst=burstT[en]
        trgIDF=idfT[en]
        if srccount>0 and trgcount>0:
            freqscore=math.fabs(math.log(srccount)-math.log(trgcount))
        elif srccount>0:
            freqscore=(math.log(srccount))
        elif trgcount>0:
            freqscore=(math.log(trgcount))                
        else:
            freqscore=0.0
        freq[en]=freqscore
        if trgBurst>0 and srcBurst>0:
            burst[en]=min((srcBurst/trgBurst),(trgBurst/srcBurst))
        else:
            burst[en]=0.0 # Default value 0 b/c if one value is 0 then maximally different?; this should only happen for words not in wikipedia corpus at all
        if srcIDF>0 and trgIDF>0:
            idf[en]=min((srcIDF/trgIDF),(trgIDF/srcIDF))
        else:
            idf[en]=0.0
    allsorted["freq"]=sorted(freq.iteritems(), key=operator.itemgetter(1), reverse=False) # lower is better
    fullScorenames.append("freq")
    allsorted["burst"]=sorted(burst.iteritems(), key=operator.itemgetter(1), reverse=True) # higher is better
    fullScorenames.append("burst")
    allsorted["idf"]=sorted(idf.iteritems(), key=operator.itemgetter(1), reverse=True) # higher is better
    fullScorenames.append("idf")
    allRanked={}
    for scorename in fullScorenames:
        allRanked[scorename]=getWordToRankDict(allsorted[scorename])
    #Now actually write features
    for en in allen:
        write=True
        if en not in allENTrue and downsample: #only down-sample training data and only if not a correct example
            if random.random()>samplevalue:
                write=False
        if write:
            if en in allENTrue:
                if writeLabels:
                    outfileindex+=fr+"\t"+en+"\t"+"True"+"\n"
                    outfile+="+1 | "
                else:
                    outfileindex+=fr+"\t"+en+"\n"
                    outfile+="| "
            else:
                if writeLabels:
                    outfileindex+=fr+"\t"+en+"\t"+"False"+"\n"
                    outfile+="-1 | "
                else:
                    outfileindex+=fr+"\t"+en+"\n"
                    outfile+="| "
            outfile+="1:"+str(allSc["crawls-context"].get(fr,{}).get(en,0.0))+" " #Feature 1: crawls context score
            outfile+="2:"+str(allSc["edit"].get(fr,{}).get(en,((len(fr)+len(en))/2)))+" " #Feature 2: edit distance score
            outfile+="3:"+str(allSc["crawls-time"].get(fr,{}).get(en,0.0))+" " #Feature 3: crawls time score
            ranks={}
            for scorename in fullScorenames:
                #myscorerank=getRank(allsorted[scorename],en) # SLOOOOW: getting rank for all EN words
                myscorerank=allRanked[scorename].get(en,allRanked[scorename]["UNKNOWNWORD"])
                ranks[scorename]=myscorerank
                baselineMRR[en].append(1/myscorerank)
            outfile+="4:"+str(allSc["wiki-context"].get(fr,{}).get(en,0.0))+" " # Feature 4: wiki context score
            outfile+="5:"+str(allSc["wiki-topic"].get(fr,{}).get(en,0.0))+" " # Feature 5: wiki topic score
            if af:
                outfile+="6:"+str(allSc["wiki-context-pre"].get(fr,{}).get(en,0.0))+" " # Feature 6: prefix wiki context score
                outfile+="7:"+str(allSc["wiki-topic-pre"].get(fr,{}).get(en,0.0))+" "   # Feature 7: prefix wiki topic score            
                outfile+="8:"+str(allSc["crawls-context-pre"].get(fr,{}).get(en,0.0))+" " # Feature 8: prefix crawls context score
                outfile+="9:"+str(allSc["crawls-temp-pre"].get(fr,{}).get(en,0.0))+" "   # Feature 9: prefix crawls temporal score            
            if afs:
                outfile+="10:"+str(allSc["wiki-context-suf"].get(fr,{}).get(en,0.0))+" " # Feature 10: suffix wiki context score
                outfile+="11:"+str(allSc["wiki-topic-suf"].get(fr,{}).get(en,0.0))+" "   # Feature 11: suffix wiki topic score                            
                outfile+="12:"+str(allSc["crawls-context-suf"].get(fr,{}).get(en,0.0))+" " # Feature 12: suffix crawls context score
                outfile+="13:"+str(allSc["crawls-temp-suf"].get(fr,{}).get(en,0.0))+" "   # Feature 13: suffix crawls temporal score                            
            if fr==en:
                outfile+="14:"+str(1)+" " # Feature 14: is-identical
            else:
                outfile+="14:"+str(0)+" "
            outfile+="15:"+str(freq.get(en,0.0))+" " # Feature 15: absolute value of difference between log frequencies
            if twc[en]>0:
                outfile+="16:"+str(1/math.log(twc[en]+1))+" " # Feature 16: inverse log-raw target frequency
            else:
                outfile+="16:"+str(1.0)+" " # like frequency of 1
            tc=twc[en]/(twct/swct)
            sc=swc[fr]
            outfile+="17:"+str(burst.get(en,0.0))+" " # Feature 17: minimum of burstiness ratios (s/t vs t/s)
            outfile+="18:"+str(idf.get(en,0.0))+" " # Feature 18: minimum of idf ratios (s/t vs t/s)
            outfile+="\n"
    return outfile, outfileindex, baselineMRR

def readFreqFile(filename,mydict,total):
    openfile=codecs.open(filename,'r','utf-8')
    line=openfile.readline()
    while line:
        line=line.strip().split(" ")
        if len(line)>1:
            freq=int(line[0])
            word=line[1]
            mydict[word]+=freq
            total+=freq
        line=openfile.readline()
    return mydict, total

# Given filename, read tab separated dictionary and return dict object
def readDict(dictfile):
    print "Reading dictionary"
    dicttrans=defaultdict(list)
    openfile=codecs.open(dictfile,'r','utf-8')
    dictline=openfile.readline()
    i=0
    while dictline:
        i+=1
        dictline=dictline.strip().split("\t")
        if len(dictline)>1:
            fr=dictline[0].strip(" ").strip(".").strip(",").strip("?")
            en=dictline[1].strip(" ").strip(".").strip(",").strip("?")
            if len(fr.split(" "))==1 and len(en.split(" "))==1 and len(fr)>0 and len(en)>0:
                if en not in dicttrans[fr]:
                    dicttrans[fr].append(en)
        try:
            dictline=openfile.readline()
        except UnicodeDecodeError:
            print "ERROR: Dictionary at ",dictfile," line number:", i
            exit()
    return dicttrans


def getTruthPairs(outfile):
    numwordstoclassify=0
    frenTruthPairs={} # indexed by fr word, then "true" or "false" strings -> value list of en words
    for fr in allFRWords:
        frenTruthPairs[fr]={}
        frenTruthPairs[fr]["true"]=[]
        frenTruthPairs[fr]["false"]=[]    
        found=False
        if len(dicttrans[fr])>0:
            for scorename in encand_scorenames:
                for en in allScores[scorename].get(fr,{}).keys():
                    if en in dicttrans[fr]:
                        found=True
                        frenTruthPairs[fr]["true"].append(en)
                    else:
                        frenTruthPairs[fr]["false"].append(en)
            if not found:
                outfile.write(fr+"\t"+" ".join(dicttrans[fr])+"\n")
            else:
                numwordstoclassify+=1
    print "Number of words for which a correct English word appears in any ranked list:", numwordstoclassify, "or %.2f percent" % (100*numwordstoclassify/len(allFRWords))
    return frenTruthPairs


def getFreqs(lang):
    trgcounts=defaultdict(int)
    srccounts=defaultdict(int)
    trgcountsTotal=0
    srccountsTotal=0
    srcdir="wikiFreqs/"+lang+"/src/"
    trgdir="wikiFreqs/"+lang+"/trg/"
    for filename in os.listdir(srcdir):
        if filename.endswith("wordscounted"):
            srccounts,srccountsTotal=readFreqFile(srcdir+filename,srccounts,srccountsTotal)
    for filename in os.listdir(trgdir):
        if filename.endswith("wordscounted"):
            trgcounts,trgcountsTotal=readFreqFile(trgdir+filename,srccounts,trgcountsTotal)
    return srccounts, trgcounts, srccountsTotal, trgcountsTotal

def readBurstyFile(infile):
    openfile=codecs.open(infile,'r','utf-8')
    line=openfile.readline()
    burstiness=defaultdict(float)
    idf=defaultdict(float)
    variance=defaultdict(float)
    entropy=defaultdict(float)
    rawfreq=defaultdict(float)
    totalcounts=0
    while line:
        word,b,i,v,e,r=line.strip().split("\t")
        burstiness[word]=float(b)
        idf[word]=float(i)
        variance[word]=float(v)
        entropy[word]=float(e)
        rawfreq[word]=int(r)
        totalcounts+=int(r)
        line=openfile.readline()
    return burstiness, idf, variance, entropy, rawfreq, totalcounts

def getBurstiness(lang, burstinessMeasuresDirectory):
    trgcounts=defaultdict(int)
    srccounts=defaultdict(int)
    trgcountsTotal=0
    srccountsTotal=0
    srcfile=burstinessMeasuresDirectory + "/burst."+lang+"."+lang
    trgfile=burstinessMeasuresDirectory + "/burst."+lang+".en"
    burstiness_src, idf_src, variance_src, entropy_src, rawfreq_src, srccountsTotal = readBurstyFile(srcfile)
    burstiness_trg, idf_trg, variance_trg, entropy_trg, rawfreq_trg, trgcountsTotal = readBurstyFile(trgfile)
    return burstiness_src, idf_src, variance_src, entropy_src, rawfreq_src, srccountsTotal, burstiness_trg, idf_trg, variance_trg, entropy_trg, rawfreq_trg, trgcountsTotal

def get_vw_train_command_from_config(config):
    subdirectory = config.get("subdirectory", "withAffixFeatsNoAffixCandidates")
    language = config.get("language", "az")
    languageSubdirectory = config.get("languageSubdirectory", "")
    cachefile = subdirectory + "/" + language + "/" + languageSubdirectory + "/" + config.get("cachefile", "train.cache")
    modelfile = subdirectory + "/" + language + "/" + languageSubdirectory + "/" + config.get("modelfile", 'train.model')
    readablemodelfile = subdirectory + "/" + language + "/" + languageSubdirectory + "/" + config.get("readablemodelfile", "train.model.readable")

    testprediction = config.get("testprediction", "test.predictions")
    testscores = config.get("testscores", "test.scores")
    if config.get("useLog", "false").startswith("true"):
        loss_function = "logistic"
    else:
        loss_function = "squared"

    norm_config = {
        "l1": " --l1 0.5 ",
        "l2": " --l2 0.5 ",
        "l1l2": " --l1 0.5 --l2 0.5 "

    }
    norm = norm_config.get(config.get("norm", "").strip(), "")
    neural_network = " --nn 60 " if config.get("useNeuralNetwork", "").startswith("true") else ""

    cmd = "rm -rf " + cachefile + " && "
    cmd += " $vw -d " + subdirectory + "/" + language + "/" + languageSubdirectory + "/train.data" \
        + " -f " + modelfile \
        + " -k -c --passes 100 " \
        + norm \
        + neural_network \
        + " --loss_function " + loss_function \
        + " --exact_adaptive_norm --power_t 0.5 " \
        + " --readable_model " + readablemodelfile

    return cmd

def get_vw_test_command_from_config(config):
    subdirectory = config.get("subdirectory", "withAffixFeatsNoAffixCandidates")
    language = config.get("language", "az")
    languageSubdirectory = config.get("languageSubdirectory", "")
    modelfile = subdirectory + "/" + language + "/" + languageSubdirectory + "/" + config.get("modelfile", 'train.model')

    testpredictions = subdirectory + "/" + language + "/" + languageSubdirectory + "/" + config.get("testpredictions", "test.predictions")
    testscores =  subdirectory + "/" + language + "/" + languageSubdirectory + "/" + config.get("testscores", "test.scores")

    cmd = " $vw -i " + modelfile \
        + " -t -d " + testpredictions \
        + " -r " + testscores

    return cmd
######## Main script
#global allFRWords
#allFRWords=[]
import argparse

def main():
    parser = argparse.ArgumentParser(description = "Run the ranking of candidate english words for foreign word")
    parser.add_argument("-s", '--subdirectory', dest='subdirectory', type=str, help='subdirectory to place files in')
    parser.add_argument("-l", '--language', dest='language', type=str, help='language to evaluate (directory ./(subdirectory)/language) will be created')
    parser.add_argument("-c", '--config_file', dest='config_file', type=str, help='config file location')
    parser.add_argument("--l1", dest='l1', type=float, help='l1 regularization')
    parser.add_argument("--l2", dest='l2', type=float, help='l2 regularization')
    parser.add_argument("--nn", dest='nn', type=int, help='neural network hidden layers')
    args = parser.parse_args()
	#print args.l1

    global dicttrans
    global encand_scorenames
    global allScores
    global allFRWords
    

    lang = args.language
    subdir = args.subdirectory
    os.system("mkdir -p " + subdir + "/" + lang)
    config=readConfig(args.config_file, lang)
    useprefix=config.get("useprefix", "false")
    if useprefix.startswith("true"):
        affixFeats=True
        print "Using prefix features"
    else:
        affixFeats=False
    useprefixcands=config.get("useprefixcands","false")
    if useprefixcands.startswith("true"):
        affixFeatsCands=True
        print "Using candidates from prefix scores"
    else:
        affixFeatsCands=False
    usesuffix=config.get("usesuffix","false")
    if usesuffix.startswith("true"):
        affixFeatsS=True
        print "Using suffix features"
    else:
        affixFeatsS=False
    usesuffixcands=config.get("usesuffixcands","false")
    if usesuffixcands.startswith("true"):
        affixFeatsCandsS=True
        print "Using candidates from suffix scores"
    else:
        affixFeatsCandsS=False
    doByFreq=False
    if config.get("byfreq","false").startswith("true"):
        doByFreq=True

    inputDataDirectory = config.get("inputDataDirectory")
    readDirectory = inputDataDirectory + "/" + lang
    wikiwords=readDirectory + "/" + config.get("frwikiwords")
    crawlswords=readDirectory + "/" + config.get("frcrawlswords")
    burstinessMeasuresDirectory=config.get("burstinessMeasuresDirectory")
    print "Input Data Directory:", inputDataDirectory
    print "Wiki induced words:", wikiwords
    print "Crawls induced words:", crawlswords
    print "Burstiness measures directory:", burstinessMeasuresDirectory

    readData=True
    if config.get("readData","true").startswith("false"):
        readData=False
        print "Not reading data..."
    else:
        print "Reading data..."

    writeData=True
    if config.get("writeData","true").startswith("false"):
        writeData=False
        print "Not writing data..."
    else:
        print "Writing data..."

    doClassification=True
    if config.get("doClassification","true").startswith("false"):
        doClassification=False
        print "Skipping classification..."
    else:
        print "Doing classification"

    logistic=False
    if config.get("useLog","false").startswith("true"):
        logistic=True
    print "Using logistic regression..."

    trainAmount=float(config.get("trainAmount","1.0"))
    print "Percent of 1/3 data reserved for training actually used: "+str(trainAmount)

    print "Doing analysis by frequency:", doByFreq #will expect files like context.0.scored
    underLangSubdir=config.get("underlangdir","")

    dictfile=config["dictfile"]
    dicttrans=readDict(dictfile)


    if readData:
        print "Reading burstiness files"
        burstiness_src, idf_src, variance_src, entropy_src, srcWordCounts, srcWordCountsTotal, burstiness_trg, idf_trg, variance_trg, entropy_trg, trgWordCounts, trgWordCountsTotal = getBurstiness(lang, burstinessMeasuresDirectory)
        #srcWordCounts, trgWordCounts, srcWordCountsTotal, trgWordCountsTotal=getFreqs(lang)

        print "Reading crawls and wiki scored files in ", readDirectory
        if doByFreq:
            contextfile_crawls=readDirectory+"/"+config["crawlsdir"]+"/context.NUM.scored"
            editfile_crawls=readDirectory+"/"+config["crawlsdir"]+"/edit.NUM.scored"
            timefile_crawls=readDirectory+"/"+config["crawlsdir"]+"/time.NUM.scored"
            aggmrrfile_crawls=readDirectory+"/"+config["crawlsdir"]+"/aggmrr.NUM.scored"
        else:
            contextfile_crawls=readDirectory+"/"+config["crawlsdir"]+"/context.scored"
            editfile_crawls=readDirectory+"/"+config["crawlsdir"]+"/edit.scored"
            timefile_crawls=readDirectory+"/"+config["crawlsdir"]+"/time.scored"
            aggmrrfile_crawls=readDirectory+"/"+config["crawlsdir"]+"/aggmrr.scored"    
        contextfile_wiki=readDirectory+"/"+config["wikidir"]+"/context.scored"
        editfile_wiki=readDirectory+"/"+config["wikidir"]+"/edit.scored"
        timefile_wiki=readDirectory+"/"+config["wikidir"]+"/time.scored"
        aggmrrfile_wiki=readDirectory+"/"+config["wikidir"]+"/aggmrr.scored"
        if affixFeats:
            precontextfile_wiki=readDirectory+"/"+config["wikipredir"]+"/context.scored"
            pretimefile_wiki=readDirectory+"/"+config["wikipredir"]+"/time.scored"
            precontextfile_crawls=readDirectory+"/"+config["crawlspredir"]+"/context.scored"
            pretimefile_crawls=readDirectory+"/"+config["crawlspredir"]+"/time.scored"
        if affixFeatsS:
            sufcontextfile_wiki=readDirectory+"/"+config["wikisufdir"]+"/context.scored"
            suftimefile_wiki=readDirectory+"/"+config["wikisufdir"]+"/time.scored"
            sufcontextfile_crawls=readDirectory+"/"+config["crawlssufdir"]+"/context.scored"
            suftimefile_crawls=readDirectory+"/"+config["crawlssufdir"]+"/time.scored"

    # List of all words scored for wiki and crawls (intersection of two lists)
    allFRWords_wiki=[x.strip().split("\t")[1] for x in codecs.open(wikiwords,'r','utf-8').readlines()]  
    allFRWords_crawls=[x.strip().split("\t")[1] for x in codecs.open(crawlswords,'r','utf-8').readlines()]
    allFRWords_crawls_dict = defaultdict(allFRWords_crawls)
    allFRWords=[x for x in allFRWords_wiki if x in allFRWords_crawls_dict]

    allScores={} #allScores[scorename][fr][en]=score
    allFRWords_Scored=[] # List of all words that were ACTUALLY scored

    ######## Read scored files: from crawls, wikipedia, prefixed wikipedia
    if doByFreq and readData:
        frWordGroups=[]
        for i in range(0,10): # from crawls, in binned frequencies
            frwords_c, allScores=scoredFile(contextfile_crawls.replace("NUM",str(i)),"crawls-context",allScores)      # Crawls context
            frwords_t, allScores=scoredFile(timefile_crawls.replace("NUM",str(i)),"crawls-time", allScores)           # Crawls time
            frwords_e, allScores=scoredFile(editfile_crawls.replace("NUM",str(i)),"edit", allScores)                  # Crawls edit
            frwords_a, allScores=scoredFile(aggmrrfile_crawls.replace("NUM",str(i)),"crawls-aggmrr", allScores)       # Crawls aggmrr
            uniqFRWords=set(frwords_c.keys()+frwords_t.keys()+frwords_e.keys()+frwords_a.keys())
            frWordGroups.append(uniqFRWords) # set of fr words for this frequency bin
            for f in uniqFRWords:
                if f not in allFRWords_Scored:
                    allFRWords_Scored.append(f)
    elif readData:
        frwords_c, allScores=scoredFile(contextfile_crawls,"crawls-context", allScores)      # Crawls context
        frwords_t, allScores=scoredFile(timefile_crawls, "crawls-time", allScores)           # Crawls time
        frwords_e, allScores=scoredFile(editfile_crawls, "edit", allScores)                  # Crawls edit
        frwords_a, allScores=scoredFile(aggmrrfile_crawls, "crawls-aggmrr", allScores)       # Crawls aggmrr
        uniqFRWords=set(frwords_c.keys()+frwords_t.keys()+frwords_e.keys()+frwords_a.keys())
        for f in uniqFRWords:
            if f not in allFRWords_Scored:
                allFRWords_Scored.append(f)

    if readData:
        frwords_cw, allScores=scoredFile(contextfile_wiki,"wiki-context", allScores)       # Wiki context
        frwords_tw, allScores=scoredFile(timefile_wiki,"wiki-topic", allScores)            # Wiki topic
        frwords_ew, allScores=scoredFile(editfile_wiki,"edit", allScores)                  # Wiki edit
        frwords_aw, allScores=scoredFile(aggmrrfile_wiki,"wiki-aggmrr", allScores)         # Wiki aggmrr
        uniqFRWords=set(frwords_cw.keys()+frwords_tw.keys()+frwords_ew.keys()+frwords_aw.keys())
        for f in uniqFRWords:
            if f not in allFRWords_Scored:
                allFRWords_Scored.append(f)
        if affixFeats:
            frwords_cwp, allScores=scoredFile(precontextfile_wiki,"wiki-context-pre", allScores)       # Wiki context - prefixed
            frwords_twp, allScores=scoredFile(pretimefile_wiki,"wiki-topic-pre", allScores)            # Wiki topic - prefixed
            frwords_ccp, allScores=scoredFile(precontextfile_crawls,"crawls-context-pre", allScores)   # Crawls context - prefixed
            frwords_tcp, allScores=scoredFile(pretimefile_crawls,"crawls-temp-pre", allScores)           # Crawls temporal - prefixed
        if affixFeatsS:
            frwords_cws, allScores=scoredFile(sufcontextfile_wiki,"wiki-context-suf", allScores)       # Wiki context - suffixed
            frwords_tws, allScores=scoredFile(suftimefile_wiki,"wiki-topic-suf", allScores)            # Wiki topic - suffixed
            frwords_ccs, allScores=scoredFile(sufcontextfile_crawls,"crawls-context-suf", allScores)   # Crawls context - suffixed
            frwords_tcs, allScores=scoredFile(suftimefile_crawls,"crawls-temp-suf", allScores)         # Crawls temporal - suffixed

        print "Number of FR words scored by both wiki and crawls:", len(allFRWords)
        print "Total number of FR words scored by either:", len(allFRWords_Scored)

        scorenames=["crawls-context","crawls-time","edit","crawls-aggmrr","wiki-context","wiki-topic","edit","wiki-aggmrr"]
        if affixFeats:
            scorenames.append("wiki-context-pre")
            scorenames.append("wiki-topic-pre")
            scorenames.append("crawls-context-pre")
            scorenames.append("crawls-temp-pre")
        if affixFeatsS:
            scorenames.append("wiki-context-suf")
            scorenames.append("wiki-topic-suf")
            scorenames.append("crawls-context-suf")
            scorenames.append("crawls-temp-suf")

        # Get candidates from which scored files?
        encand_scorenames=[]
        for sn in scorenames:
            if sn.endswith("-pre"):
                if affixFeatsCands: # only append sn if affixFeatsCands is true
                    encand_scorenames.append(sn)
            elif sn.endswith("-suf"):
                if affixFeatsCandsS: # only append sn if affixFeatsCandsS is true
                    encand_scorenames.append(sn)        
            else:
                encand_scorenames.append(sn)        
        print "Using English candidates from the following scored files:", encand_scorenames

        # For each fr, sort en candidate words into true and false piles
        os.system("mkdir -p "+subdir+"/"+lang+"/"+underLangSubdir)
        outfile=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/"+lang+".NoEnRanked",'w','utf-8')
        frenTruthPairs=getTruthPairs(outfile)

    #### Now write training and testing files
    # Classification: +1 is correct, -1 is incorrect
    frWordsBaseline=defaultdict(lambda : defaultdict(list))
    if writeData:
        outTrain=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/train.data","w","utf-8")
        outTest=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/test.data","w","utf-8")
        outBlind=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/blind.data","w","utf-8")
        outTrainIndex=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/train.data.index","w","utf-8")
        outTestIndex=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/test.data.index","w","utf-8")
        outBlindIndex=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/blind.data.index","w","utf-8")
        i=0
        # 1/3 of fr words for testing HERE, 1/3 for training here, 1/3 held out for later experiments
        writeErrors=0
        for fr in allFRWords:
            if len(dicttrans[fr])>0: # go ahead and train on all, whether or not correct english word is in a ranked list or not; only if reachable in dictionary at all
                allENTrue=set(frenTruthPairs[fr]["true"])
                allENFalse=set(frenTruthPairs[fr]["false"])
                if i<1:
                    #write to train if sampled
                    if random.random()<trainAmount:
                        out,outindex,baselineMRR=returnFeatures(fr, allENTrue, allENFalse, swc=srcWordCounts, twc=trgWordCounts, swct=srcWordCountsTotal, twct=trgWordCountsTotal, sn=scorenames, allSc=allScores, af=affixFeats, afs=affixFeatsS, burstS=burstiness_src, burstT=burstiness_trg, idfS=idf_src, idfT=idf_trg, varS=variance_src, varT=variance_trg, entropyS=entropy_src, entropyT=entropy_trg, downsample=True)
                        try:
                            outTrain.write(out)
                            outTrainIndex.write(outindex)
                            frWordsBaseline[fr]=baselineMRR
                            i+=1
                        except UnicodeDecodeError:
                            writeErrors+=1
                elif i<2:
                    #write to test
                    out,outindex,baselineMRR=returnFeatures(fr, allENTrue, allENFalse, swc=srcWordCounts, twc=trgWordCounts, swct=srcWordCountsTotal, twct=trgWordCountsTotal, sn=scorenames, allSc=allScores, af=affixFeats, afs=affixFeatsS, burstS=burstiness_src, burstT=burstiness_trg, idfS=idf_src, idfT=idf_trg, varS=variance_src, varT=variance_trg, entropyS=entropy_src, entropyT=entropy_trg)
                    try:
                        outTest.write(out)
                        outTestIndex.write(outindex)
                        frWordsBaseline[fr]=baselineMRR
                        i+=1
                    except UnicodeDecodeError:
                        writeErrors+=1
                else:
                    #write to blind
                    out,outindex,baselineMRR=returnFeatures(fr, allENTrue, allENFalse, swc=srcWordCounts, twc=trgWordCounts, swct=srcWordCountsTotal, twct=trgWordCountsTotal, sn=scorenames, allSc=allScores, af=affixFeats, afs=affixFeatsS, burstS=burstiness_src, burstT=burstiness_trg, idfS=idf_src, idfT=idf_trg, varS=variance_src, varT=variance_trg, entropyS=entropy_src, entropyT=entropy_trg) 
                    try:
                        outBlind.write(out)
                        outBlindIndex.write(outindex)
                        frWordsBaseline[fr]=baselineMRR
                        i=0
                    except UnicodeDecodeError:
                        writeErrors+=1
        outTestIndex.close()
        outTrainIndex.close()
        outBlindIndex.close()
        outTrain.close()
        outTest.close()
        outBlind.close()
        print "Done writing train/test/blind data. Number of write errors:", writeErrors

    #### VW classification
    cachefile=subdir+"/"+lang+"/"+underLangSubdir+"/train.cache"
    modelfile=subdir+"/"+lang+"/"+underLangSubdir+"/train.model"
    readablemodelfile=subdir+"/"+lang+"/"+underLangSubdir+"/train.model.readable"
    testpredictions=subdir+"/"+lang+"/"+underLangSubdir+"/test.predictions"
    testscores=subdir+"/"+lang+"/"+underLangSubdir+"/test.scores"

    if doClassification:
        if logistic:
            print "Running VW logistic learning..."
            print "Command:"
            cmd = "rm -f "+cachefile+" && $vw --l1 " + ("%.10f" % args.l1) + " --l2 " + ("%.10f" % args.l2) + " -d  "+subdir+"/"+lang+"/"+underLangSubdir+"/train.data"+" -f "+modelfile+" -c --passes 100 --loss_function logistic --adaptive --power_t 0.5 --readable_model "+readablemodelfile
			#cmd = "rm -f "+cachefile+" && $vw --nn " + str(args.nn) + " -d  "+subdir+"/"+lang+"/"+underLangSubdir+"/train.data"+" -f "+modelfile+" -c --passes 100 --loss_function logistic --adaptive --power_t 0.5 --readable_model "+readablemodelfile
            print cmd
            os.system(cmd)
        else:
            print "Running VW linear learning..."
            print "Command:"
            cmd = "rm -f "+cachefile+" && $vw -d "+subdir+"/"+lang+"/"+underLangSubdir+"/train.data"+" -f "+modelfile+" -c --passes 100 --exact_adaptive_norm --power_t 0.5 --readable_model "+readablemodelfile
            print cmd
            os.system(cmd)
        time.sleep(60)
        print "Doing prediction:"
        print "Command:"
        print "$vw -i "+modelfile+" -t -d "+subdir+"/"+lang+"/"+underLangSubdir+"/test.data"+" -p "+testpredictions+" -r "+testscores
        os.system("$vw -i "+modelfile+" -t -d "+subdir+"/"+lang+"/"+underLangSubdir+"/test.data"+" -p "+testpredictions+" -r "+testscores)
        time.sleep(60)

    #### Rerank based on test scores and evaluate
    print "Doing reranking and evaluation..."
    outTestIndex=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/test.data.index","r","utf-8")
    indexline=outTestIndex.readline()
    scoresfile=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/test.scores",'r','utf-8')
    scoresline=scoresfile.readline()
    scoresDict={}
    outFile=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/test.reranked.scored",'w','utf-8')
    while indexline and scoresline:
        indexline=indexline.strip().split("\t")
        fr=indexline[0]
        en=indexline[1]
        answer=indexline[2]
        if fr not in scoresDict:
            scoresDict[fr]={}
        scoresDict[fr][en]=float(scoresline.split(" ")[-1])
        indexline=outTestIndex.readline()
        scoresline=scoresfile.readline()

    #lookup fr word, get score of correct answer
    candScores=defaultdict(float)
    #lookup fr word, get rank of highest ranked correct answer
    candRanks=defaultdict(int)
    for fr in scoresDict.keys():
        sortedscores = sorted(scoresDict[fr].iteritems(), key=operator.itemgetter(1), reverse=True)
        outFile.write("<"+fr+">\n")
        # indicates if top ranked correct answer has been found or not
        found=False
        for en, score in sortedscores:
            outFile.write("\t")
            if en in dicttrans[fr]:
                outFile.write("* ")
                if not found:
                    candScores[fr]=score
                    found=True
            outFile.write("["+str(score)+"] "+en+"\n")
        notfoundcount=0
        if found:
            numTied=-1
            candRanks[fr]=1
            for en, score in sortedscores:
                if score>candScores[fr] and en not in dicttrans[fr]:
                    candRanks[fr]+=1
                elif score==candScores[fr]:
                    numTied+=1 # will be 0 if no ties 
            smoothedRank=candRanks[fr]+(numTied/2)
            candRanks[fr]=smoothedRank
        else:
            candRanks[fr]=9999999 # maximum value outside of ranked range will ever care about
            notfoundcount+=1
    print "Correct EN not found in CAND rankings:", notfoundcount

    aggmrrRanks=defaultdict(int)
    notfoundcount=0
    # Only do comparison if had read data...
    if readData:
        for fr in scoresDict:
            #tempdict=allScores["crawls-aggmrr"].get(fr,{})    # Old way of doing this comparison
            tempdict=defaultdict(float)
            for en in frWordsBaseline[fr]:
                tempdict[en]=numpy.mean(frWordsBaseline[fr][en])
            sortedscores = sorted(tempdict.iteritems(), key=operator.itemgetter(1), reverse=True) # use true baseline here, defined in calls to returnFeatures
            myrank=1
            found=False
            for en, score in sortedscores:
                if en in dicttrans[fr] and not found:
                    aggmrrRanks[fr]=myrank
                    found=True # this keeps from populating rank with another good but lower ranked translation
                else:
                    myrank+=1
            if not found:
                aggmrrRanks[fr]=9999999 # maximum value outside of ranked range will ever care about
                notfoundcount+=1
        print "Correct EN not found in AGGMRR rankings:", notfoundcount

    #print "Foreign Word - Old Rank of Correct EN - New Rank of Correct EN"
    mrrCand=[]
    mrrAGGMRR=[]
    grouped_mrrCand={}
    grouped_mrrAGGMRR={}
    outFile=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/test.rankcompare",'w','utf-8')
    for i in range(0,10):
        grouped_mrrCand[i]=[]
        grouped_mrrAGGMRR[i]=[]
    for fr in scoresDict:
        mrrCand.append(candRanks[fr])
        mrrAGGMRR.append(aggmrrRanks[fr])
        outFile.write(fr+"\t"+" ".join(dicttrans[fr])+"\t"+str(aggmrrRanks[fr])+"\t"+str(candRanks[fr])+"\n")
        if doByFreq:
            for i in range(0,10):
                if fr in frWordGroups[i]:
                    grouped_mrrCand[i].append(candRanks[fr])
                    grouped_mrrAGGMRR[i].append(aggmrrRanks[fr])

    if len(mrrAGGMRR)>0:
        print "\nMean reciprocal rank of AGG-MRR ranks:", sum([1/x for x in mrrAGGMRR if x>0])/len(mrrAGGMRR)
    if len(mrrCand)>0:
        print "Mean reciprocal rank of ML-learned weighted ranks:", sum([1/x for x in mrrCand if x>0])/len(mrrCand)

    #### Accuracy in top-k

    print "\nAccuracy in top-1:"
    if len(mrrAGGMRR)>0:
        acc_top1_aggmrr=len([x for x in mrrAGGMRR if x<2])/len(mrrAGGMRR)
        print "MRR:", acc_top1_aggmrr
    if len(mrrCand)>0:
        acc_top1_cand=len([x for x in mrrCand if x<2])/len(mrrCand)
        print "Cand:", acc_top1_cand
    print "\nAccuracy in top-10:"
    if len(mrrAGGMRR)>0:
        acc_top10_aggmrr=len([x for x in mrrAGGMRR if x<11])/len(mrrAGGMRR)
        print "MRR:", acc_top10_aggmrr
    if len(mrrCand)>0:
        acc_top10_cand=len([x for x in mrrCand if x<11])/len(mrrCand)
        print "Cand:", acc_top10_cand
    print "\nAccuracy in top-100:"
    if len(mrrAGGMRR)>0:
        acc_top100_aggmrr=len([x for x in mrrAGGMRR if x<101])/len(mrrAGGMRR)
        print "MRR:", acc_top100_aggmrr
    if len(mrrCand)>0:
        acc_top100_cand=len([x for x in mrrCand if x<101])/len(mrrCand)
        print "Cand:", acc_top100_cand

    if doByFreq:
        grouped_acc_top1_aggmrr=[]
        grouped_acc_top1_cand=[]
        grouped_acc_top10_aggmrr=[]
        grouped_acc_top10_cand=[]
        grouped_acc_top100_aggmrr=[]
        grouped_acc_top100_cand=[]
        for i in range(0,10):
            if len(grouped_mrrAGGMRR[i])>0 and len(grouped_mrrCand[i])>0:
                grouped_acc_top1_aggmrr.append(100*len([x for x in grouped_mrrAGGMRR[i] if x<2])/len(grouped_mrrAGGMRR[i]))
                grouped_acc_top1_cand.append(100*len([x for x in grouped_mrrCand[i] if x<2])/len(grouped_mrrCand[i]))
                grouped_acc_top10_aggmrr.append(100*len([x for x in grouped_mrrAGGMRR[i] if x<11])/len(grouped_mrrAGGMRR[i]))
                grouped_acc_top10_cand.append(100*len([x for x in grouped_mrrCand[i] if x<11])/len(grouped_mrrCand[i]))
                grouped_acc_top100_aggmrr.append(100*len([x for x in grouped_mrrAGGMRR[i] if x<101])/len(grouped_mrrAGGMRR[i]))
                grouped_acc_top100_cand.append(100*len([x for x in grouped_mrrCand[i] if x<101])/len(grouped_mrrCand[i]))
            else:
                grouped_acc_top1_aggmrr.append(-1)
                grouped_acc_top1_cand.append(-1)
                grouped_acc_top10_aggmrr.append(-1)
                grouped_acc_top10_cand.append(-1)
                grouped_acc_top100_aggmrr.append(-1)
                grouped_acc_top100_cand.append(-1)

        os.system("python ../getAvg.py ../"+lang+"/sepproj/run1/monoextract.txt ../"+lang+"/sepproj/run1/output/aggmrr.table")

        freqFile=codecs.open("../"+lang+"/sepproj/run1/output/aggmrr.table.avgfreq",'r','utf-8').readlines()
        freqs=[]
        for x in freqFile[1:]:
            x=x.strip().split("\t")
            freqs.append(x[0])
        print freqs

        os.system("mkdir "+subdir+"/"+lang+"/output")
        time.sleep(5)
        outTable_aggmrr=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/output/aggmrr",'w','utf-8')
        outTable_cand=codecs.open(subdir+"/"+lang+"/"+underLangSubdir+"/output/cand",'w','utf-8')

        outTable_aggmrr.write("Ave_Freq\t1\t10\t100\n")
        outTable_cand.write("Ave_Freq\t1\t10\t100\n")
        for i in range(0,10):
            if grouped_acc_top1_aggmrr[i]!=-1:
                outTable_aggmrr.write(str(freqs[i])+"\t"+str(grouped_acc_top1_aggmrr[i])+"\t"+str(grouped_acc_top10_aggmrr[i])+"\t"+str(grouped_acc_top100_aggmrr[i])+"\n")
                outTable_cand.write(str(freqs[i])+"\t"+str(grouped_acc_top1_cand[i])+"\t"+str(grouped_acc_top10_cand[i])+"\t"+str(grouped_acc_top100_cand[i])+"\n")

    print "Done."

if __name__=="__main__":
    #cProfile.run('main()')
    main()


