import json
from pymetamap import MetaMap, ConceptMMI
import os
import csv
from tokenizer import tokenizer
import re
from nltk.tokenize import sent_tokenize
import numpy as np


def sent2bioes(sent, annotations):
    words, s = [], "O"
    splitters = "\n \t\r"
    word, i = "", 0
    o = -1
    for ch in sent:
        if ch in splitters and len(word) > 0:
            words.append(word + "\t" + s)
            s = "I-" + annotations[o]["type"] if o > -1 and annotations[o]["end"] >= i+1 else "O"
            word = ""
            i += 1
        elif ch in splitters and len(word) == 0:
            words.append("")
        else:
            word += ch
            if i in annotations:
                o = i
                s = "B-"+annotations[o]["type"]
            i += 1
    words.append(word + "\t" + s)
    return words


def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])


def process(row, configuration, mm, aux):
    R = tokenizer.RedditTokenizer(preserve_url=False, preserve_emoji=False, preserve_len=False, regularize=True,
                                  preserve_handles=False)
    sents = " ".join(R.tokenize(row))
    res = []
    for sent in sent_tokenize(sents):
        annotations = {}
        if sent in aux:
            concepts, error = aux[sent]
        else:
            concepts, error  = mm.extract_concepts([sent], restrict_to_sts=configuration["restrict_to_sts"],
                                                   word_sense_disambiguation=True)
            aux[sent] = (concepts, error)
        for concept in [c for c in concepts if type(c) == ConceptMMI and ";" not in c.pos_info
                        and len([x for x in c.semtypes.split(",")
                                if x.replace("[","").replace("]", "") in configuration["restrict_to_sts"]]) > 0]:
            semtype = [x.replace("[","").replace("]", "") for x in concept.semtypes.split(",")
                       if x.replace("[","").replace("]", "") in configuration["restrict_to_sts"]][0]
            for s_an in concept.pos_info.split(","):
                s_an = "".join([c for c in s_an if not c in "[]"])
                e_an = int(s_an.split("/")[1])-1
                s_an = int(s_an.split("/")[0])
                e_an = s_an + e_an
                trigger = concept.trigger.split('"')
                if (len(trigger[3].lower()) > 5 or levenshtein(trigger[1].lower(), trigger[3].lower()) < 2) and \
                        (s_an not in annotations or float(concept.score) < annotations[s_an]["score"]):
                    annotations[s_an] = {"end": e_an, "type": semtype, "score": float(concept.score)}
        res.append("\n".join(sent2bioes(sent, annotations)))
    return "\n".join(res)


configuration = json.load(open("configuration.json","rb"))
mm = MetaMap.get_instance(configuration["metamap_path"])
for fichero in os.listdir(configuration["corpus_path"]):
    if fichero.endswith("csv") and not fichero.startswith(".") and \
            fichero not in os.listdir(configuration["output_path"]):
        with open(configuration["corpus_path"]+"/"+fichero) as csv_file:
            f = open(configuration["output_path"]+fichero, "wb")
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    aux = {}
                    tittle = process(re.sub("(\n\s*\n)+", "\n", row[6]).strip(), configuration, mm, aux)
                    text = process(re.sub("(\n\s*\n)+", "\n", row[5]).strip(), configuration, mm, aux)
                    line_count += 1
                    f.write(("####POST####\n").encode("utf-8"))
                    f.write((str(row[1])+"\n").encode("utf-8"))
                    f.write((str(row[3])+"\n").encode("utf-8"))
                    f.write((str(row[7])+"\n").encode("utf-8"))
                    f.write(("####TITLE####\n").encode("utf-8"))
                    f.write((tittle+"\n").encode("utf-8"))
                    f.write(("####TEXT####\n").encode("utf-8"))
                    f.write((text+"\n").encode("utf-8"))
                    f.write(("\n\n\n####END-POST####\n\n\n").encode("utf-8"))
            f.close()
