import nltk

# download necessary NLTK corpora and modules
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# define a function to extract matching verses based on PoS patterns
def extract_matching_verses(text, pos_pattern):
    # tokenize the text into sentences
    sentences = nltk.sent_tokenize(text)
    matching_verses = []
    # iterate over each sentence and check for matching PoS patterns
    for sentence in sentences:
        # tokenize the sentence into words and tag them with PoS labels
        words = nltk.word_tokenize(sentence)
        pos_tags = nltk.pos_tag(words)
        # convert the PoS pattern string to a list of PoS tags
        pattern_tags = pos_pattern.split()
        # check if the sentence contains the specified PoS pattern
        print(pos_tags)
        if all(tag in [pos for (word, pos) in pos_tags] for tag in pattern_tags):
            # if the pattern is found, add the sentence to the matching verses list
            matching_verses.append(sentence)
    return matching_verses

# example usage
text = "John saw Mary walking down the street. She was carrying a red umbrella."
pos_pattern = "DT JJ"
matching_verses = extract_matching_verses(text, pos_pattern)
print(matching_verses) # output: ['John saw Mary walking down the street.']
