import requests
from bs4 import BeautifulSoup
import os

print("Running visa sponsor scraper")

# URL of the page to scrape
url = "https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"

# Get the current directory of the python file
current_directory = os.path.dirname(os.path.abspath(__file__))
# Set the download folder relative to the current directory
download_folder = os.path.join(current_directory, "sponsors-lists/csv")

# Sending a GET request to the webpage
response = requests.get(url)

# Parsing the content of the page using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Finding the `a` tag with the specific class
a_tag = soup.find('a', class_='gem-c-attachment__link')

# Checking if the tag exists and retrieving the href attribute
if a_tag:
    link = a_tag['href']
    print("Link found:", link)

    # Download the file
    if link.startswith('/'):
        # Making sure the link is complete if it's relative
        link = f'https://www.gov.uk{link}'
    
    file_response = requests.get(link)
    
    # Check if the request was successful
    if file_response.status_code == 200:
        # Get the filename from the content-disposition header or default to a name
        content_disposition = file_response.headers.get('content-disposition')
        if content_disposition:
            filename = content_disposition.split('filename=')[1]
        else:
            filename = link.split('/')[-1]
        
        if filename.startswith('"'):
            filename = filename[1:]
        if filename.endswith('"'):
            filename = filename[:-1]
        
        # Writing the file to disk
        path = os.path.join(download_folder, filename)
        with open(path, 'wb') as f:
            f.write(file_response.content)
        print(f"File has been downloaded: {path}")
    else:
        print("Failed to download the file.")

else:
    print("No link found with the specified class.")
