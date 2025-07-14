import re
import nltk
from ebooklib import epub
import ebooklib
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def extract_text_from_epub(file_path):
    """Extract text from an epub file."""
    book = epub.read_epub(file_path)
    text = ''
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            text += item.get_content().decode('utf-8')
    return text

def clean_text(text):
    """Clean the text by removing HTML tags, punctuation, stopwords, and lemmatizing."""
    # Remove HTML tags
    text = re.sub('<[^<]+?>', '', text)

    # Tokenize the text
    tokens = nltk.word_tokenize(text)

    # Remove punctuation and convert to lowercase
    tokens = [token.lower() for token in tokens if token.isalpha()]

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if not token in stop_words]

    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Convert the list of tokens back to text
    clean_text = ' '.join(tokens)

    return clean_text

if __name__ == '__main__':
    file_path = 'books/1998.epub'

    # Extract text from epub file
    text = extract_text_from_epub(file_path)

    # Clean the text
    clean_text = clean_text(text)
    print(clean_text)


    # Print the title and language of the book
    book = epub.read_epub(file_path)
    print(book.title, book.language)
