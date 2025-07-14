import re
import requests
import os
import json
import logging
from urllib.request import urlopen
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# download html and return parsed doc or None on error
def download_url(urlpath):
    try:
        # open a connection to the server
        with urlopen(urlpath, timeout=3) as connection:
            # read the contents of the html doc
            return connection.read()
    except:
        # bad url, socket timeout, http forbidden, etc.
        return None

# decode downloaded html and extract all <a href=""> links
def get_urls_from_html(content):
    # decode the provided content as ascii text
    html = content.decode('utf-8')
    # parse the document as best we can
    soup = BeautifulSoup(html, 'html.parser')

    nietzsche_section = None
    for h2_tag in soup.find_all('h2'):
        if "Nietzsche, Friedrich Wilhelm" in h2_tag.text:
            nietzsche_section = h2_tag
            break

    res = []
    if nietzsche_section:
        # Find the next <ul> sibling after the Nietzsche section
        ul_tag = nietzsche_section.find_next_sibling('ul')
        if ul_tag:
            for li_tag in ul_tag.find_all('li'):
                a_tag = li_tag.find('a')
                if a_tag:
                    href = a_tag.get('href')
                    if href and href.startswith('/ebooks/'):
                        match = re.search(r'/ebooks/(\d+)', href)
                        if match:
                            ebook_id = match.group(1)
                            title = a_tag.text.strip()
                            # Extract language from title, e.g., "Title (English)"
                            lang_match = re.search(r'\((.*?)\)', title)
                            language = lang_match.group(1) if lang_match else "Unknown"
                            # Remove language from title for cleaner metadata
                            clean_title = re.sub(r'\s*\(.*\)', '', title).strip()
                            res.append({'id': ebook_id, 'title': clean_title, 'language': language})
    return res

# download one book from project gutenberg
def download_books(ebook_data, format='.epub'):
    if not os.path.exists("books"): os.makedirs("books")
    all_metadata = []

    for book in ebook_data:
        e_id = book['id']
        title = book['title']
        language = book['language']
        filepath = os.path.join("books", f"pg{e_id}{format}")

        if language != "English":
            logging.info(f"Skipping {title} (ID: {e_id}) - not in English ({language}).")
            continue

        if os.path.exists(filepath):
            logging.info(f"Skipping {title} (ID: {e_id}) - already exists.")
            all_metadata.append(book) # Add existing book to metadata
            continue

        url = f'https://www.gutenberg.org/cache/epub/{e_id}/pg{e_id}{format}'
        logging.info(f"Attempting to download {title} (ID: {e_id}) from {url}")
        try:
            r = requests.get(url, stream=True)
            r.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=8192):
                    fd.write(chunk)
            logging.info(f"Successfully downloaded {title} (ID: {e_id}).")
            all_metadata.append(book) # Add downloaded book to metadata

        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading {title} (ID: {e_id}): {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred for {title} (ID: {e_id}): {e}")
    
    # Save all metadata to a single file
    metadata_filepath = os.path.join("books", "nietzsche_books_metadata.json")
    with open(metadata_filepath, 'w') as f:
        json.dump(all_metadata, f, indent=4)
    logging.info(f"Saved all metadata to {metadata_filepath}.")

# download all books from project gutenberg
def download_all_books(url, save_path, format='.epub'):
    # download the page that lists top books
    data = download_url(url)
    if data is None:
        logging.error(f"Failed to download URL: {url}")
        return
    logging.info(f'Downloaded {url}')
    # extract all links from the page
    ebook_data = get_urls_from_html(data)
    download_books(ebook_data, format)

# entry point
URL = 'https://www.gutenberg.org/ebooks/author/779'
DIR = 'books'

if __name__ == "__main__":
    # download top books
    download_all_books(URL, DIR)