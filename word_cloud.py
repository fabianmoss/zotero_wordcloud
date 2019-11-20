import numpy as np
from collections import Counter
import re
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud
# lower max_font_size, change the maximum number of word and lighten the background:
from wordcloud import ImageColorGenerator

stop_words = [
    "of", "the", "and", "a", "an",
    "in", "for", "to", "is", "by", "this",
    "as", "are", "with", "that", "from",
    "on", "oxford", "handbook", "we", "between",
    "how", "using", "", "can", "it", "new", "-",
    "international", "conference", "be","role",
    "has", "two", "through", "der", "which",
    "some", "its", "not", "towards"
    ]

def extract_words(bib_file):
    with open('library.bib', encoding="utf8") as bibtex_file:
        s = str(bibtex_file.read().encode("utf-8"))

    itemlist = [" ".join(entry.split("\\n\\t")) for entry in s.split("\\n@")[1:]]

    entries = []
    for entry in itemlist:
        entry_dict = {}
        m1 = re.match("(?P<type>\w*){(?P<id>\S*),", entry)
        if m1:
            entry_dict["type"] = m1.group("type")
            entry_dict["id"] = m1.group("id")
        m2 = re.match(".*title\s*=\s*{(?P<title>[\w\s\{\}\:\-\'\"]*),", entry)
        if m2:
            entry_dict["title"] = m2.group("title").replace("{", "").replace("}", "")
        m3 = re.match(".*abstract\s*=\s*{(?P<abstract>[\w\s\\n\\t\.\,]*)}", entry)
        if m3:
            entry_dict["abstract"] = m3.group("abstract").replace("{", "").replace("}", "") # remove curly brackets
        m4 = re.match(".*keywords\s*=\s*{(?P<keywords>[\w\,\s]*)}", entry)
        if m4:
            entry_dict["keywords"] = m4.group("keywords").replace("{", "").replace("}", "") # remove curly brackets
        m5 = re.match(".*booktitle\s*=\s*{(?P<booktitle>[\w\s\{\}\:\-\'\"]*),", entry)
        if m5:
            entry_dict["booktitle"] = m5.group("booktitle").replace("{", "").replace("}", "") # remove curly brackets

        entries.append(entry_dict)

    word_lists = [ entry[item].split() for item in ["title", "booktitle", "abstract", "keywords"] \
        for entry in entries if item in entry.keys() ]

    words = [ w.lower().strip(":") for word_list in word_lists \
        for w in word_list if w.lower() not in stop_words ]

    text = " ".join(words)
    return text

if __name__ == "__main__":
    text = extract_words("library.bib")

    # setting mask image
    mask = np.array(Image.open("./econ.png"))

    #creating wordcloud
    wordcloud = WordCloud(
        mask=mask,
        width=2000,
        height=1000,
        contour_color="black",
        max_words=10000,
        relative_scaling=0,
        background_color="white").generate(text)
    image_colors = ImageColorGenerator(mask)
    plt.figure(figsize=[20,15])
    plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
    plt.axis("off")
    plt.savefig("wordcloud.pdf")
    plt.show()
