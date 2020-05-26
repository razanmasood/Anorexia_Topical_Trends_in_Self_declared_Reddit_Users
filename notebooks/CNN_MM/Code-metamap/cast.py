import os
f = open("./semantic_groups.txt", "rb").read().decode("utf-8")
f = {x.split("|")[0]: x.split("|")[2] for x in f.split("\n")}
f["UnknownType"] = "UnknownType"
print(f)
for x in os.listdir("output/"):
    if x.endswith(".csv") and not x.startswith("."):
        fil = []
        y = open("output/"+x, "rb").read().decode("utf-8")
        ini = 1
        for l in y.split("\n"):
            if not len(l) == 0:
                t = l.split("\t")
                if len(t) > 1:
                    if not t[0] in ["(", ")", "as", "?", "!", "are", "am", "not", "of", "is", "to", "if",
                                    "do", "a", "the", ".", ",", "I", "i", "at", '"', "'", "you", "they",
                                    "we", "-", "/", "*", "+"]:
                        try:
                            label = "O" if t[1].strip() == "O" else \
                                t[1].strip().split("-")[0] + "-" + f[t[1].split("-")[1].replace("[", "").replace("]", "")]
                            if "B-" in label:
                                ini = 2
                        except:
                            label = "O"
                            ini = 1
                    else:
                        label = "O"
                        ini = 1
                    if not ini == 2:
                        label = "O"
                    fil.append(t[0]+"\t"+label)
            else:
                fil.append("")
        y = open("output/" + x + ".output", "wb")
        y.write("\n".join(fil).encode("utf-8"))
        y.close()
