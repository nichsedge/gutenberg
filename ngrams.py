def generate_ngrams(text, n):
    """
    Generate a list of n-grams from a given text string.
    """
    # Convert the text to lowercase and remove punctuation
    text = text.lower()
    text = ''.join(c for c in text if c not in '.,;:-?!')
    
    # Split the text into words
    words = text.split()
    
    # Generate the n-grams using a sliding window
    ngrams = []
    for i in range(len(words)-n+1):
        ngrams.append(' '.join(words[i:i+n]))
    
    return ngrams

text = "The quick brown fox jumps over the lazy dog."
ngrams = generate_ngrams(text, 3)
print(ngrams)