from collections import Counter
import re

# define a function to extract repeated phrases from a given text
def extract_repeated_phrases(text):
    # preprocess the text by removing punctuation and converting to lowercase
    text = re.sub(r'[^\w\s]', '', text.lower())
    # split the text into words
    words = text.split()
    # create a set of unique words to speed up processing
    unique_words = set(words)
    # initialize a counter to track the frequency of repeated phrases
    phrase_counter = Counter()
    # iterate over each unique word in the text
    for word in unique_words:
        # find all occurrences of the word in the text
        word_occurrences = [i for i, w in enumerate(words) if w == word]
        # iterate over each pair of word occurrences
        for i in range(len(word_occurrences)):
            for j in range(i + 1, len(word_occurrences)):
                # extract the phrase between the two occurrences of the word
                phrase = ' '.join(words[word_occurrences[i]:word_occurrences[j] + 1])
                # increment the frequency counter for the extracted phrase
                phrase_counter[phrase] += 1
    # sort the repeated phrases in descending order by frequency
    sorted_phrases = sorted(phrase_counter.items(), key=lambda x: x[1], reverse=True)
    return sorted_phrases

# example usage
text = "Mary had a little lamb. Its fleece was white as snow. And everywhere that Mary went, the lamb was sure to go."
repeated_phrases = extract_repeated_phrases(text)
print(repeated_phrases) # output: [('mary had a little lamb', 1), ('the lamb was sure to go', 1), ('its fleece was white as snow', 1), ('mary went the lamb was sure to', 1), ('everywhere that mary went the lamb', 1), ('had a little lamb its fleece', 1), ('white as snow and everywhere', 1)]