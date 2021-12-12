import argparse
import re
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
import pandas as pd
from PyPDF2 import PdfFileReader

stop_words = [
    "of", "the", "and", "a", "an",
    "in", "for", "to", "is", "by", "this",
    "as", "are", "with", "that", "from",
    "on", "oxford", "handbook", "we", "between",
    "how", "using", "", "can", "it", "new", "-",
    "international", "conference", "be","role",
    "has", "two", "through", "der", "which",
    "some", "its", "not", "towards",
    "introduction", "paper", "proceedings", "their", "und", "or",
    "more", "about", "one", "these", "have", "beyond", "use", "used",
    "different", "other", "most", "", "within", "across", "2021", "than",
    "cambridge", "into", "first", "at", "our", "https", "http", "doi", "pp", "et", "e. g.",
    "e.g.", "io", "pp.", "th", "mj", "css", "no.", "al.",
    "such", "also", "but", "they", "vol", "(pp", "all", "was", "r2", "ch", "pdf",
    "much"
    ]

custom_mappings = {
    "studies": "study",
    '"music,music"' : "music",
    "musical" : "music",
    "harmonic" : "harmony",
    "music psychology" : "psychology",
    "music theory" : "theory",
    "music perception" : "perception",
    "music cognition" : "cognition",
    "cognitive" : "cognition",
    "modelling" : "modeling",
    "syntactic" : "syntax",
    "theory,music": "music theory",
    "theories" : "theory",
    "sciences" : "science",
    "melodies" : "melody",
    "concepts" : "concept",
    "nir" : "mir"
}

items = ["title", "booktitle", "abstract", "keywords"]

def clean(word_lists):
    words = [ re.sub("[:,\.\-\"\s]*$", "", w.lower()) for word_list in word_lists \
        for w in word_list if w.lower() not in stop_words ]

    words = [ custom_mappings.get(item,item) for item in words if len(item) > 1 ] # custom replacement
    return words

def extract_from_bib(file):
    with open(file, encoding="utf8") as f:
        s = str(f.read().encode("utf-8"))

    itemlist = [" ".join(entry.split("\\n\\t")) for entry in s.split("\\n@")[1:]]

    entries = []
    for entry in itemlist:
        entry_dict = {}
        m1 = re.match(r"(?P<type>\w*){(?P<id>\S*),", entry)
        if m1:
            entry_dict["type"] = m1.group("type")
            entry_dict["id"] = m1.group("id")
        m2 = re.match(r".*title\s*=\s*{(?P<title>[\w\s\{\}\:\-\'\"]*),", entry)
        if m2:
            entry_dict["title"] = m2.group("title").replace("{", "").replace("}", "")
        m3 = re.match(r".*abstract\s*=\s*{(?P<abstract>[\w\s\\n\\t\.\,]*)}", entry)
        if m3:
            entry_dict["abstract"] = m3.group("abstract").replace("{", "").replace("}", "") # remove curly brackets
        m4 = re.match(r".*keywords\s*=\s*{(?P<keywords>[\w\,\s]*)}", entry)
        if m4:
            entry_dict["keywords"] = m4.group("keywords").replace("{", "").replace("}", "") # remove curly brackets
        m5 = re.match(r".*booktitle\s*=\s*{(?P<booktitle>[\w\s\{\}\:\-\'\"]*),", entry)
        if m5:
            entry_dict["booktitle"] = m5.group("booktitle").replace("{", "").replace("}", "") # remove curly brackets

        entries.append(entry_dict)

    word_lists = [ entry[item].split() for item in items \
        for entry in entries if item in entry.keys() ]

    text = "\n".join(clean(word_lists))
    return text

def extract_from_pdf(file):
    with open(file, "rb") as f:
        word_lists = [ p.extractText().split() for p in PdfFileReader(f).pages ]
        text = "\n".join(clean(word_lists))
        return text

def extract_words(file):
    if file.endswith(".bib"): 
        return extract_from_bib(file)
    elif file.endswith(".pdf"): 
        return extract_from_pdf(file)
    else:
        print("Don't recognize file extension.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--fnames", type=str, help="filename(s) to extract words from", nargs='+')
    parser.add_argument("--topwords", type=int, help="number of most frequent words to consider", default=200)
    args = parser.parse_args()

    text = "\n".join([ extract_words(f) for f in args.fnames ])
    
    with open("text.txt", "w") as f:
        f.write(text)

    # setting mask image
    mask = np.array(Image.open("./rectangle.png"))

    #creating wordcloud
    wordcloud = WordCloud(
        mask=mask,
        width=1600,
        height=900,
        contour_color="black",
        max_words=args.topwords if args.topwords < len(text) else len(text),
        relative_scaling=0,
        background_color="white").generate(text)

    # lower max_font_size, change the maximum number of word and lighten the background:
    image_colors = ImageColorGenerator(mask)

    plt.figure(figsize=[12,8], dpi=300)
    plt.imshow(
        wordcloud.recolor(color_func=image_colors),
        interpolation="bilinear"
        )
    plt.axis("off")

    plt.tight_layout()
    outfile = "wordcloud.pdf"
    plt.savefig(outfile)
    # plt.show()

    ## same word counts
    s = pd.Series(text.split("\n"))
    s.value_counts().to_csv("counts.csv")
