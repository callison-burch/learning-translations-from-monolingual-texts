#HOW TO RUN

## Command
> python **rerank_refactored.py** --language $1 --subdirectory withAffixFeatsNoAffixCands/ --config_file rerankll.m3ps.evalonly.config --l1 $NUM --l2 $NUM (--nn neural_network_layers)

e.g. 
> python **rerank_refactored.py** --language az --subdirectory withAffixFeatsNoAffixCands/ --config_file rerankll.m3ps.evalonly.config --l1 0.01 --l2 0.01 --nn 10

## Pre-requisites
For this to work you directory should have:

1. A language directory (the subdirectory option) with crawled data e.g. az
	a. this language directory should have the input data for the language which could be wiki or crawled data processed by Babel. e.g. az/crawls-minf10
2. A burstinessMeasures directory with burst.<$language$>.en and burst.<$language$>.<$language$> files
3. a config file, which specifies various configuration options. An example would be:

    > useprefix=true
    > useprefixcands=false
    > inputDataDirectory=.
    > burstinessMeasuresDirectory=burstinessMeasures
    > wikipredir=wiki-minf10-Prefix/output
    > crawlspredir=crawls-minf10-Prefix/output
    > usesuffix=true
    > usesuffixcands=false
    > wikisufdir=wiki-minf10-Suffix/output
    > crawlssufdir=crawls-minf10-Suffix/output
    > byfreq=false
    > crawlsdir=crawls-minf10/output
    > wikidir=wiki-minf10/output
    > frwikiwords=wiki-minf10/output/srcinduct.list
    > frcrawlswords=crawls-minf10/output/srcinduct.list
    > dictfile=/nlp/users/shreejit/MTurkDicts/mturk.$LANG$
    > useLog=true
    > readData=true
    > writeData=true
    > doClassification=true

4. An MTurk dictionary file as specified in the config file. which has individual word translations as gathered by MTurk HITS


The wikipredir, crawlspredir, wikisufdir, wikidir, crawlsdir, frwikiwords, frcrawlswords options assume that these directories are within the language subdirectory i.e. within inputDataDirectory/subDirectory/<$wikipredir$> etc...

This will then generate the directory mentioned as in the --subdirectory with a directory <language> inside it. If the writeData is set to true, then it will recreate training, test and blind data (where training and testing is used for learning parameters, and blind data is used for evaluation).

So in the subdirectory/language you should have 3 sets of data
1. train.<suffix>
2. test.<suffix>
3. blind.<suffix>

The learning is done with the vowpal wabbit tool so that needs to be installed as well.

The script will run the evaluation and print out the scores for the rankings. The Cand1, Cand10 and Cand100 numbers are to be interpreted as the number of correct translations in the top n candiates.

## Steps
1. This is an example of a full run with the Azeri language. First make sure you have mturk.az in /nlp/users/shreejit/MTurkDicts (according to the example config file)
2. Make sure you have the az/crawls-minf10/output directory, where az is in the inputDataDirectory. It should have the following files:
    > aggmrr.eval
    > aggmrr.scored
    > context.eval
    > context.scored
    > edit.eval
    > edit.scored
    > srcinduct.list
    > time.eval
    > time.scored
3. Make sure you have the burstinessMeasures directory in the inputDataDirectory (the cwd). It should have:
    - burst.az.az
    - burst.az.en
4. Make sure you have the config file. It should look something like this:
    - >useprefix=true
    > useprefixcands=false
    > inputDataDirectory=.
    > burstinessMeasuresDirectory=burstinessMeasures
    > wikipredir=wiki-minf10-Prefix/output
    > crawlspredir=crawls-minf10-Prefix/output
    > usesuffix=true
    > usesuffixcands=false
    > wikisufdir=wiki-minf10-Suffix/output
    > crawlssufdir=crawls-minf10-Suffix/output
    > byfreq=false
    > crawlsdir=crawls-minf10/output
    > wikidir=wiki-minf10/output
    > frwikiwords=wiki-minf10/output/srcinduct.list
    > frcrawlswords=crawls-minf10/output/srcinduct.list
    > dictfile=/nlp/users/shreejit/MTurkDicts/mturk.$LANG$
    > useLog=true
    > readData=true
    > writeData=true
    > doClassification=true
5. Run the command with all directories, the dictionary and the config file in the appropriate places. E.g.
    - > python rerank_refactored.py --language az --subdirectory withAffixFeatsNoAffixCands/ --config_file rerankll.m3ps.ref.config --l1 0.01 --l2 0.01
6. You should now have a withAffixFeatsNoAffixCands directory, with az inside it in the current working directory. It should have the following files:
    - az.NoEnRanked
    - blind.data
    - blind.data.index
    - test.data
    - test.data.index
    - test.predictions
    - test.rankcompare
    - test.reranked.scored
    - test.scores
    - train.data
    - train.data.cache
    - train.data.index
    - train.model
    - train.model.readable
7. The program should also give the accuracy of the run in a format like so:
    - > Mean reciprocal rank of AGG-MRR ranks: 0.0
      > Mean reciprocal rank of ML-learned weighted ranks: 0.132917895797
      >
      > Accuracy in top-1:
      > MRR: 1.0
      > Cand: 0.0771670190275
      > 
      > Accuracy in top-10:
      > MRR: 1.0
      > Cand: 0.233615221987
      > 
      > Accuracy in top-100:
      > MRR: 1.0
      > Cand: 0.492600422833
