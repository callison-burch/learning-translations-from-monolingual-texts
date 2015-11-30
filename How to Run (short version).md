#HOW TO RUN

python rerank_refactored.py --language $1 --subdirectory withAffixFeatsNoAffixCands/ --config_file rerankll.m3ps.evalonly.config --l1 $NUM --l2 $NUM

e.g. python rerank.py az withAffixFeatsNoAffixCands_ReTrain /home/ccb/AnnRerankSubDir/rerankll.m3ps.evalonly.config

For this to work you directory should have:

1. a language directory with crawled data e.g. az
	a. this language directory should have the input data for the language which could be wiki or crawled data processed by Babel. e.g. az/crawls-minf10
2. a burstinessMeasures directory with burst.<language>.en and burst.<language>.<language> files
3. a config file, which specifies various configuration options. An example would be:

useprefix=true
useprefixcands=false
inputDataDirectory=.
burstinessMeasuresDirectory=burstinessMeasures
wikipredir=wiki-minf10-Prefix/output
crawlspredir=crawls-minf10-Prefix/output
usesuffix=true
usesuffixcands=false
wikisufdir=wiki-minf10-Suffix/output
crawlssufdir=crawls-minf10-Suffix/output
byfreq=false
crawlsdir=crawls-minf10/output
wikidir=wiki-minf10/output
frwikiwords=wiki-minf10/output/srcinduct.list
frcrawlswords=crawls-minf10/output/srcinduct.list
dictfile=/nlp/users/shreejit/MTurkDicts/mturk.$LANG$
useLog=true
readData=true
writeData=true
doClassification=true

4. A MTurk dictionary file as specified in the config file. which has individual word translations as gathered by MTurk HITS


The wikipredir, crawlspredir, wikisufdir, wikidir, crawlsdir, frwikiwords, frcrawlswords assume that these directories are within the inputDataDirectory.

This will then generate the directory mentioned as in the --subdirectory with a directory <language> inside it. If the writeData is set to true, then it will recreate training, test and blind data (where training and testing is used for learning parameters, and blind data is used for evaluation).

So in the subdirectory/language you should have 3 sets of data
1. train.<suffix>
2. test.<suffix>
3. blind.<suffix>

The learning is done with the vowpal wabbit tool so that needs to be installed as well.

The script will run the evaluation and print out the scores for the rankings. The Cand1, Cand10 and Cand100 numbers are to be interpreted as the number of correct translations in the top n candiates.