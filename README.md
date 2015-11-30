# Learning Translations from Monolingual Texts

Bilingual Lexicon Induction is the task of inducing word translations from monolingual corpora in two languages. The first
step involves mining of data from various monlingual sources like Wikipedia and the Web in general for the source langauge
and then the second step involves using discriminative supervised techniques to match English candidate words which could 
be possible translations of unknown foreign words.

Currently this repo only has the files to do the second part. rerank_refactored.py is the runner file which given the input
directories, will generate a list of candidate English words for the given unknown foreign words.

Check How to Run (short version).md to get started and get to know which directories are needed to run the config.

On the nlp grid, this was successfully run in /nlp/users/shreejit/one-language so you could take a look there, along with the config files to see which directories are needed to recreate the experiment.

The How to Run (long version).md is a lengthier description of what the code does, which will be updated as and when I get to more about the experiments performed.