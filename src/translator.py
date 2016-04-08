import nltk
import os.path
import cPickle
import argparse
import sys
import string
#
# read test.reranked.scored for the language
# and extract the highest scored en word

puncts = set(string.punctuation)
def read_k_translations(test_reranked_file, k, count=None, prefix=None):
    i = 0; en_count = 0
    fr_en_dict = {}
    with test_reranked_file as f:
        en_translation = False
        for line in f.readlines():
            # print "Line is {}".format(line)
            if line.startswith("<"):
                fr_word = line.strip().replace("<", "").replace(">", "")[:prefix]
                # print "Foreign word is {}".format(fr_word)
                en_translation = True
                i += 1
                if count != None:
                    if i >= count:
                        break
            elif en_translation:
                en_word = line.strip().split("]")[1].strip()
                # print "translation is {}".format(en_word)
                if fr_word in fr_en_dict:
                    fr_en_dict[fr_word].append(en_word)
                else:
                    fr_en_dict[fr_word] = [en_word]
                # fr_en_dict[fr_word] = en_word
                en_count += 1
                if en_count >= k:
                    en_translation = False
                    en_count = 0

            else:
                continue

    return fr_en_dict


def read_mturk_dict(mturk_dict_file):
    mturk_dict = {}
    with mturk_dict_file as f:
        for line in f.readlines():
            fr_word = line.strip().split("\t")[0]
            en_word = line.strip().split("\t")[1]
            mturk_dict[fr_word] = en_word
            # print "MTurk {} = {}".format(fr_word, en_word)
    return mturk_dict

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
            all_line_tokens.extend([line_token for line_token in line_tokens if line_token not in puncts])
    return all_line_tokens


def translate_text_with_dict(tokens, induced_dict, mturk_dict, prefix=None):
    t = 0
    output_tokens = []
    token_translation_dict = {}
    file_name = "all_tokens" + str(prefix) + ".hun.txt" if not prefix is None else "all_tokens.hun.txt"
    with open(file_name, "w") as f:
        for raw_token in tokens:
            output_line = []
            token = raw_token.strip().lower()[:prefix]
            output_line.append(token)

            if token in mturk_dict:
                output_line.append(mturk_dict[token])
                # print "Md {} = {}".format(token, mturk_dict[token])
            else:
                output_line.append("__")

            if token in induced_dict:
                if token not in token_translation_dict:
                    token_translation_dict[token] = induced_dict[token]
                output_tokens.append(induced_dict[token][0])
                # print "Id {} = {}".format(token, induced_dict[token][0])
                output_line.append(" ".join(induced_dict[token]))
                t += 1
            else:
                output_tokens.append(token)
                output_line.append("__")

            # print "output line {}".format(output_line)
            f.write("\t:\t".join(output_line) + "\n")

    return output_tokens, token_translation_dict, t / float(len(tokens))

def write_dict_to_file(trans_dict, output_file):
    text = ""
    for key in trans_dict:
        line = key + " : " + " ".join(trans_dict[key]) + "\n"
        text += line
    # print "Writing {} to {}".format(text, output_file)
    output_file.write(text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Given the induced translation file and text file, outputs the translated"
                                                 " text",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--text_file", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input text file")
    parser.add_argument("--mturk_dict_file", "-m", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="mturk dictionary file file")
    parser.add_argument("--top_k_translations", "-k", nargs='?', type=int, default=1, help="top k translation candidates to be used")
    parser.add_argument("--translation_file", "-t", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="translation file")
    parser.add_argument("--output_file", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdin, help="translations output file")

    try:
        args = parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))

    translation_file = args.translation_file
    mturk_dict_file = args.mturk_dict_file
    text_file = args.text_file
    k = args.top_k_translations

    dict_pickle_file = "hun.p"
    if os.path.isfile(dict_pickle_file):
        print "Reading dict file from serialized file"
        induced_dict = cPickle.load(open(dict_pickle_file, "rb"))
    else:
        print "Generating dict file and saving"
        induced_dict = read_k_translations(translation_file, k)
        cPickle.dump(induced_dict, open(dict_pickle_file, "wb"))

    print "Dictionary found {} of size {}".format(induced_dict, len(induced_dict))
    print "Induced Dictionary size {}".format(len(induced_dict))
    mturk_dict = read_mturk_dict(mturk_dict_file)
    print "MTurk Dirct {}".format(mturk_dict)
    print "MTurk Dictionary size {}".format(len(mturk_dict))
    tokens = read_flat_file(text_file)

    translated, transdict, metrics = translate_text_with_dict(tokens, induced_dict, mturk_dict)
    print metrics

    write_dict_to_file(transdict, args.output_file)

    prefix_fr_en_dict = {}
    induced_prefix_dict = {}
    for i in xrange(4, 8):
        prefix_fr_en_dict[i] = translate_dict_to_n_prefix(induced_dict, i)
        # print "Dictionary found {} of size {}".format(prefix_fr_en_dict[i], len(prefix_fr_en_dict[i]))
        translated, transdict, metrics = translate_text_with_dict(tokens, prefix_fr_en_dict[i], mturk_dict, i)
        print "Metrics for prefix length i={} {}".format(i, metrics)
