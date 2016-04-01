import nltk
import os.path
import cPickle
import argparse
import sys
#
# read test.reranked.scored for the language
# and extract the highest scored en word
def read_translations(test_reranked_file, count=None):
    i = 0
    fr_en_dict = {}
    with test_reranked_file as f:
        en_translation = False
        for line in f.readlines():
            # print "Line is {}".format(line)
            if line.startswith("<"):
                fr_word = line.strip().replace("<", "").replace(">", "")
                # print "Foreign word is {}".format(fr_word)
                en_translation = True
            elif en_translation:
                en_word = line.strip().split("]")[1].strip()
                # print "translation is {}".format(en_word)
                fr_en_dict[fr_word] = en_word
                en_translation = False
                i += 1
                if count != None:
                    if i >= count:
                        break
            else:
                continue

    return fr_en_dict


def translate_dict_to_n_prefix(fr_en_dict, n):
    fr_en_prefix_dict = {}
    for key in fr_en_dict:
        fr_en_prefix_dict[key[:n]] = fr_en_dict[key]
    return fr_en_prefix_dict


def read_flat_file(text_file):
    all_line_tokens = []
    with text_file as f:
        for line in f.readlines():
            try :
                line_tokens = nltk.word_tokenize(line)
            except:
                line_tokens = line.split()
            all_line_tokens.extend(line_tokens)
    return all_line_tokens


def translate_text_with_dict(tokens, dict, prefix=None):
    t = 0
    output_tokens = []
    for raw_token in tokens:
        token = raw_token.strip().lower()[:prefix]
        if token in dict:
            output_tokens.append(dict[token])
            t += 1
        else:
            output_tokens.append(token)

    return output_tokens, t / float(len(tokens))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Given the induced translation file and text file, outputs the translated"
                                                 " text",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--text_file", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input text file")
    parser.add_argument("--translation_file", "-t", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="translation file")
    try:
        args = parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))

    translation_file = args.translation_file
    text_file = args.text_file

    dict_pickle_file = "hun.p"
    if os.path.isfile(dict_pickle_file):
        print "Reading dict file from serialized file"
        fr_en_dict = cPickle.load(open(dict_pickle_file, "rb"))
    else:
        print "Generating dict file and saving"
        fr_en_dict = read_translations(translation_file)
        cPickle.dump(fr_en_dict, open(dict_pickle_file, "wb"))

    print "Dictionary found {} of size {}".format(fr_en_dict, len(fr_en_dict))
    tokens = flat_tokens = read_flat_file(text_file)
    translated, metrics = translate_text_with_dict(tokens, fr_en_dict)
    print metrics

    prefix_fr_en_dict = {}
    for i in xrange(4, 8):
        prefix_fr_en_dict[i] = translate_dict_to_n_prefix(fr_en_dict, i)
        print "Dictionary found {} of size {}".format(prefix_fr_en_dict[i], len(prefix_fr_en_dict[i]))
        translated, metrics = translate_text_with_dict(tokens, prefix_fr_en_dict[i], i)
        print "Metrics for prefix length i={} {}".format(i, metrics)
