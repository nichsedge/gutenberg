import math
from collections import Counter
import pandas as pd

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

def tf_idf(document):
    # split the document into words
    words = document.split()

    # calculate term frequency and document frequency
    tf = Counter(words)
    df = Counter(set(words))

    # calculate inverse document frequency
    num_docs = 1  # assuming only one document in the input file
    idf = {word: math.log(num_docs / count) for word, count in df.items()}

    # calculate tf-idf weight
    tfidf = {word: freq * idf[word] for word, freq in tf.items()}

    # create a list of tuples with the data
    data = [(i+1, word, freq, freq/len(words)*100, df[word], idf[word], tfidf[word])
            for i, (word, freq) in enumerate(tf.most_common())]

    # create a pandas DataFrame from the data
    df = pd.DataFrame(data, columns=['Rank', 'Word', 'Term Frequency', 'TF Percentage',
                                    'Document Frequency', 'Inverse Document Frequency', 'TFIDF Weight'])

    return df

document = "The quick brown fox jumps over the lazy dog."
wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                min_font_size = 10).generate(document)
 
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()