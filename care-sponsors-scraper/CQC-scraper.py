import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse, urljoin
import time

def get_root_path(url):
    parsed_url = urlparse(url)
    root_path = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return root_path

print("Running CQC scraper")

def get_file(url, link_cls, download_path):
    # Get the current directory of the python file
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Set the download folder relative to the current directory
    download_path = os.path.join(current_directory, download_path)

    # Sending a GET request to the webpage
    response = requests.get(url)

    # Parsing the content of the page using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Finding the `a` tag with the specific class
    a_tag = soup.find('a', class_=link_cls)

    # Checking if the tag exists and retrieving the href attribute
    if a_tag:
        link = a_tag['href']
        print("Link found:", link)

        # Download the file
        if link.startswith('/'):
            # Making sure the link is complete if it's relative
            url_root = get_root_path(url)
            link = urljoin(url_root, link)
        
        file_response = requests.get(link)
        
        # Check if the request was successful
        if file_response.status_code == 200:           
            with open(download_path, 'wb') as f:
                f.write(file_response.content)
            print(f"File has been downloaded: {download_path}")
        else:
            print("Failed to download the file.")

    else:
        print("No link found with the specified class.")

get_file(
    "https://www.cqc.org.uk/search/all?query=&location-query=&radius=&display=list&sort=relevance&last-published=&filters[]=archived:active&filters[]=careHomes:all&filters[]=lastPublished:all&filters[]=more_services:all&filters[]=services:care-home&filters[]=specialisms:all",
    "download-report__link",
    "data-in/care-data/care-homes-active.csv"
)
time.sleep(5)
get_file(
    "https://www.cqc.org.uk/search/all?query=&location-query=&radius=&display=list&sort=relevance&last-published=&filters[]=archived:deactive&filters[]=careHomes:all&filters[]=lastPublished:all&filters[]=more_services:all&filters[]=services:care-home&filters[]=specialisms:all",
    "download-report__link",
    "data-in/care-data/care-homes-archived.csv"
)
time.sleep(5)
get_file(
    "https://www.cqc.org.uk/search/all?query=&location-query=&radius=&display=list&sort=relevance&last-published=&filters[]=archived:active&filters[]=lastPublished:all&filters[]=more_services:all&filters[]=services:homecare-agencies&filters[]=specialisms:all",
    "download-report__link",
    "data-in/care-data/homecare-agencies-active.csv"
)
time.sleep(5)
get_file(
    "https://www.cqc.org.uk/search/all?query=&location-query=&radius=&display=list&sort=relevance&last-published=&filters[]=archived:deactive&filters[]=lastPublished:all&filters[]=more_services:all&filters[]=services:homecare-agencies&filters[]=specialisms:all",
    "download-report__link",
    "data-in/care-data/homecare-agencies-archived.csv"
)