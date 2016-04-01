# Translator

The translator.py translates a given text file with the induced translations in the test.reranked.scored file in the
output directories created by rerank_refactored.py. 

## How to Run
> python translator.py -i text_file -t translation_file -o translation_output_file
> 

## Prerequisites
    1. The text file to be translated
    2. The file with induced translations

The input text file, if given in the elisa xml format, can be changed to a flat file using the xml_text_extractor.py.

> python xml_text_extractor.py -i jmist.dryrun.hun.src.xml -s seg -f seg -o text.hun.txt

This is telling the extractor to output all the text in the "seg" xml element into the output file "text.hun.txt".