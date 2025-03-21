import os
import requests
import shutil
from urllib.parse import urlparse
from pathlib import Path

def download_image(url, save_path):
    
    #Download an image from a URL and save it to the specified path.
    #Returns True if successful, False otherwise.
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        #check if the content is actually an image
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            print(f"Warning: URL {url} does not point to an image (Content-Type: {content_type})")
            return False
            
        with open(save_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def replace_txt_with_jpeg(base_dir):
    """
    Traverse directory structure, read text files containing image URLs,
    download those images, and replace the text files with the downloaded JPEGs.
    """
    #get absolute path
    base_dir = os.path.abspath(base_dir)
    print(f"Processing directory: {base_dir}")
    
    #Keep track of statistics
    total_processed = 0
    successful_downloads = 0
    
    #iterate through all subdirectories
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.txt'):
                txt_path = os.path.join(root, file)
                
                #Read the URL from the text file
                try:
                    with open(txt_path, 'r') as f:
                        url = f.read().strip()
                    
                    #Check if the URL seems valid
                    if not url.startswith(('http://', 'https://')):
                        print(f"Invalid URL in {txt_path}: {url}")
                        continue
                    
                    total_processed += 1
                    
                    #Determine the save path for the JPEG
                    #we'll temporarily save to a .tmp file to avoid issues if download fails
                    temp_jpeg_path = txt_path + '.tmp'
                    final_jpeg_path = txt_path.rsplit('.', 1)[0] + '.jpg'
                    
                    print(f"Downloading {url} to replace {txt_path}")
                    
                    #Download the image to a temporary file
                    if download_image(url, temp_jpeg_path):
                        #Remove the original text file
                        os.remove(txt_path)
                        
                        #Rename the temporary file to the final JPEG name
                        os.rename(temp_jpeg_path, final_jpeg_path)
                        
                        successful_downloads += 1
                        print(f"Successfully replaced {txt_path} with {final_jpeg_path}")
                    else:
                        #Clean up the temporary file if download failed
                        if os.path.exists(temp_jpeg_path):
                            os.remove(temp_jpeg_path)
                
                except Exception as e:
                    print(f"Error processing {txt_path}: {e}")
    
    #Print summary
    print(f"\nSummary:")
    print(f"Total text files processed: {total_processed}")
    print(f"Successfully downloaded and replaced: {successful_downloads}")
    print(f"Failed: {total_processed - successful_downloads}")
#driver code
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = input("Enter the base directory path: ")
    
    replace_txt_with_jpeg(directory)