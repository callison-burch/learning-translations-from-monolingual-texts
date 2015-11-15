# Learning Translations from Monolingual Texts

Bilingual Lexicon Induction is the task of inducing word translations from monolingual corpora in two languages. The first
step involves mining of data from various monlingual sources like Wikipedia and the Web in general for the source langauge
and then the second step involves using discriminative supervised techniques to match English candidate words which could 
be possible translations of unknown foreign words.

Currently this repo only has the files to do the second part. rerank_refactored.py is the runner file which given the input
directories, will generate a list of candidate English words for the given unknown foreign words.
