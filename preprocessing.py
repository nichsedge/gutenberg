import string

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt')

from collections import Counter

def read_book(title_path): 
    """Read a book and return it as a string""" 
    with open(title_path,"r",encoding = "utf8") as current_file:            
        return current_file.read() 

def pre_processing(document, is_stopwords=True):
    document = document.replace("\n","").replace("\r","") 
    document = document.lower()
    document = document.translate(str.maketrans('', '', string.punctuation+'“'+'”'))

    # TODO: remove stopwords
    stop_words = set(stopwords.words('english')) 
    word_tokens = word_tokenize(document)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    document_clean = ' '.join(filtered_sentence)
    return document_clean

def pos_tagging(text):
    tokens = word_tokenize(text)
    tags = nltk.pos_tag(tokens, tagset = "universal")
    counts = Counter( tag for word,  tag in tags)
    print(counts)

document = read_book(r"C:\Users\ichsan\Documents\proj\gitenberg\books\51710.txt") 
document = pre_processing(document)



document = pos_tagging(document)






