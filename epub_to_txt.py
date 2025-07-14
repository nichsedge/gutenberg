import os
from epub2txt import epub2txt

def convert_epub_to_txt(file_path):
    """Convert an epub file to txt format and return the contents as a string."""
    res = epub2txt(file_path)
    return res

if __name__ == '__main__':
    # Folder Path
    path = "books"
  
    # Change the directory
    os.chdir(path)
  
    # iterate through all file
    for file in os.listdir():
        # Check whether file is in text format or not
        if file.endswith(".epub"):
            file_path = os.path.join(path, file)

            # Convert epub to txt format
            res = convert_epub_to_txt(file_path)
        
            # Write the contents to a txt file
            txt_file_path = os.path.join(path, file.replace(".epub", ".txt"))
            with open(txt_file_path, "w", encoding="utf-8") as file1:
                file1.write(res)
