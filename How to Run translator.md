# Translator

The translator.py translates a given text file with the induced translations in the test.reranked.scored file in the
output directories created by rerank_refactored.py. 

## How to Run
> python translator.py -i text_file -t translation_file -o translation_output_file -k top_k_translations -m mturk_translation_file

The output file will contain the words that have been successfully translated by lookup of the words in the translation file in the format
> word __space__ : __space__ tab separated translation candidates in decreasing order of their score
e.g.
> éjjel : only out but more all three two made has see

In addition to this, all_text.txt and all_text.$prefix$.txt files will be generated, which will be pipe-separated (|) lines with 3 columns where each line will have
    1. the word in the given text_file
    2. the translation found in the mturk file
    3. the translation as per the induced translations

The all_text.$prefix$.txt files will have translations in the above format, but the lookup will be based on the first n characters of a word, in both the 
induced translations and text.

e.g. all_text.txt would contain
> mindenképpen  :   at any price    :   __

while all_text4.txt would contains
> mind  :   all :   they all these still often here now always around only

Lookup metrics are also printed in the format:
> Induced dictionary hit rate 9.0429258723 MTurk dictionary hit rate 54.964423062 Total hit rate 54.964423062 for prefix None

## Prerequisites
    1. The text file to be translated
    2. The file with induced translations

The input text file, if given in the elisa xml format, can be changed to a flat file using the xml_text_extractor.py.

> python xml_text_extractor.py -i jmist.dryrun.hun.src.xml -s seg -f seg -o text.hun.txt

This is telling the extractor to output all the text in the "seg" xml element into the output file "text.hun.txt".