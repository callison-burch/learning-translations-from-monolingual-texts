#HOW TO RUN

	python rerank_refactored.py --language $1 --subdirectory withAffixFeatsNoAffixCands/ --config_file rerankll.m3ps.evalonly.config --l1 $NUM --l2 $NUM


For this to work you directory should have:

 1.  A language directory with crawled data e.g. az
     - this language directory should have the input data for the language which could be wiki or crawled data processed by Babel. e.g. az/crawls-minf10
 2.  A burstinessMeasures directory with burst.<language>.en and burst.<language>.<language> files
 3.  A config file, which specifies various configuration options. An example would be:

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


The config file must contain options as mentioned below for the language it is run

		Config read:
		prefix
		prefix candidates
		suffix
		suffix candidates
		do frequency
		read/write data
		do classification
		do logistic regression

If the readData option is set to true, then it reads 4 files in the language crawls sub directory

If byfreq is set to true, then the script will read

		edit.NUM.scored
		time.NUM.scored
		aggmrr.NUM.scored
		context.NUM.scored
		if not then reads
		context.scored
		time.scored
		aggmrr.scored
		edit.scored
which are present in the <language>/<crawl/wiki>/output directory e.g. az/crawls-minf10/output

If dofreq and readData options are set to true, then 10 runs are done over the whole training and evalation (though data is only generated once). These are added to a scores array which should have

		crawls context
		crawls time
		edit
		crawls aggmrr
		unique set of words for each freq bin

After this, 1/3 of the data is written to training, test and blind data sets in the vowpal wabbit.

Vowpal wabbit is used for the supervised learning. It will either run linear or logistic regression depending on the option in the config.

After this it computes the accuracies of the predictions and checks if any of the correct answers are in the top sorted candidates or not.

##VOWPAL Section

The following can be done about the reviewers’ comments:
1. The vw package has a neural network mode, as well as the option to add quadratic and cubic features automatically. We can test with them individually to check the accuracy.
2. Vowpal also has —l1 and —l2 regularization modes that can help cut down on the feature space. We could try the elastic net and keep very small weights like 0.0001 on both and see how that works.

To run one language based on the model of another language, use crossLangTrainEval.py

Use evalIndFeats.py to evaluate individual features

##VW

In the `<subdirectory>/<language dir>`
We have 

		train.data - which is the vowpal wabbit formatted input file. 
		<label> | <featurename>:<featurevalue> <featurename>:<featurevalue>…
		train.data.index - which is the word representation of the negative and positive samples.
		e.g. if you have 
		-1 | …
		-1 | …
		-1 | …
		1 | …
		this means that the first 3 are negative samples, and in the index they’ll be something like 
		bir     inrested        False
		bir     mib     False
		bir     dougie  False
		olan    the     True
		which means the first 3 are negative samples of bir not being the 3 words, and olan being the

How the scoring works is that:
1. Vowpal is given training data with positive and negative samples and the feature weights
2. It learns the weights and uses it to predict the scores on the test set, which are basically a line aligned score and fr word - english candidate tuple in the test.predictions and test.data.index respectively. 
3. The test.predictions is read (which has scores only) along with the test.data.index (which is of the form <fr> <en> <answer>). Then a dictionary of the form:
4. 
		{ 
			fr1 : { en1: score, en2 : score… },
			fr2 : …
		} 
is created
4. The english translations are reverse sorted based on their scores, and then the MTurk seed dictionary is checked to see if the correct english word is present in the english candidates or not
5. The top-k accuracy is then found on this ranked list

OUTPUT

This file generates:
1. if write, `<sub_dir>/<lang>/`, 

		train.data
		train.data.index
		test.data
		test.data.index

2. otherwise will always generate
`test.rankcompare`

3. will print out
4. 
		mean reciprocal rank of MRR
		mean reciprocal rank of discriminative (ML) method
		top1,10 and 100 accuracies for 
