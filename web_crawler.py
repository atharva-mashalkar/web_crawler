import os
import requests
from collections import deque
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from text_extraction import extract_text, save_text
from handle_visted_unvisted import save_link, get_links, get_downloaded_links
from handle_downloads import extract_links_from_file, download_file
from handle_error import log_error


# Create directories
os.makedirs('documents', exist_ok=True)
os.makedirs('links', exist_ok=True)
os.makedirs('downloads', exist_ok=True)


def downloadable_files(full_url, urls, visited_links_file, unvisited_links_file, failed_links_file, visited_links, unvisited_links, failed_links, downloaded_files):
    print(f"Found a file of type : {full_url.split('.')[-1]}. Downloading it")

    # We will download and extract links from the downloaded files as well
    file_path = os.path.join('downloads', os.path.basename(full_url))
    
    # Continue if the file is already downloaded
    if file_path in downloaded_files:
        return
    if not download_file(full_url, file_path):
        
        # If failed to download the file then, it will continue without proceeding ahead
        return
    
    # Noting the downloaded file
    downloaded_files.add(file_path)
    
    # Fetching links from the downloaded files
    links = extract_links_from_file(file_path)
    
    # Extract and save text from the downloaded files
    extracted_text = extract_text(file_path)
    save_text(extracted_text, os.path.basename(file_path))
    
    #Saving every unvisited url and adding it to que
    for new_link in links:
        full_new_link = urljoin(full_url, str(new_link))
        if not full_new_link in visited_links and not full_new_link in unvisited_links and not full_new_link in failed_links:
            if full_new_link.endswith(('.pdf', '.docx', '.csv', '.xls', '.xlsx', '.txt', '.zip', '.mp4', '.mp3', '.cgi')):
                # Drownloading downlable file
                downloadable_files(full_new_link, urls, visited_links_file, unvisited_links_file, failed_links_file, visited_links, unvisited_links, failed_links, downloaded_files)
                
                # Saving the newly visiting url
                save_link(full_new_link, visited_links_file)
                visited_links.add(full_new_link)
            else:
                unvisited_links.add(full_new_link)
                urls.append(full_new_link)
                save_link(full_new_link, unvisited_links_file)


def crawl(urls, visited_links_file, unvisited_links_file, failed_links_file, visited_links, unvisited_links, failed_links, downloaded_files):
    """_summary_

    :param url: URL where we intend to send the crawler
    """
    
    while urls:
        url = urls.popleft()
        #Return if the url is already visited
        if url in visited_links:
            continue

        # If the link is already a downlable link and is added into urls by mistake
        if url.endswith(('.pdf', '.docx', '.csv', '.xls', '.xlsx', '.txt', '.zip', '.mp4', '.mp3', '.cgi')):
            downloadable_files(url, urls, visited_links_file, unvisited_links_file, failed_links_file, visited_links, unvisited_links, failed_links, downloaded_files)
            continue

        print(f"{len(urls)} urls yet to be crawled")
        print(f'Crawling: {url}')

        # Fetching content and saving text
        try:
            #Fetching response
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            failed_links.add(url)
            # Saving failed urls
            save_link(url, failed_links_file)
            log_error(f"Failed to fetch URL {url}: {e}")
            continue
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            file_name = urlparse(url).netloc.replace('.', '_') + urlparse(url).path.replace('/', '_')
            save_text(text, file_name)
            # Saving the newly visiting url
            save_link(url, visited_links_file)
            visited_links.add(url)
            # Finding all the links from the url we just visited
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                if not full_url in visited_links and not full_url in unvisited_links and not full_url in failed_links:
                    # If the file ends with the below words then it is a downloadble URL, if not then send the crawler to newly found url
                    if full_url.endswith(('.pdf', '.docx', '.csv', '.xls', '.xlsx', '.txt', '.zip', '.mp4', '.mp3', '.cgi')):
                        downloadable_files(full_url, urls, visited_links_file, unvisited_links_file, failed_links_file, visited_links, unvisited_links, failed_links, downloaded_files)
                    else:
                        #Adding the new url to que and saving it 
                        unvisited_links.add(full_url)
                        urls.append(full_url)
                        save_link(full_url, unvisited_links_file)
        
        except Exception as e:
            log_error(f"Error processing URL {url}: {e}")


# Starting point
if __name__ == "__main__":
    
    visited_links_file = 'links/visited_links.txt'
    unvisited_links_file = 'links/unvisited_links.txt'
    failed_links_file = 'links/failed_links.txt'
    
    visited_links = get_links(visited_links_file)
    unvisited_links = get_links(unvisited_links_file)
    failed_links = get_links(failed_links_file)
    downloaded_files = get_downloaded_links('downloads')

    if len(unvisited_links):
        crawl(deque(unvisited_links), visited_links_file, unvisited_links_file, failed_links_file, set(visited_links), set(unvisited_links), set(failed_links), set(downloaded_files)) 
    else:   
        initial_urls = deque(['https://www.nist.gov/cybersecurity'])
        crawl(initial_urls, visited_links_file, unvisited_links_file, failed_links_file, set(visited_links), set(unvisited_links), set(failed_links), set(downloaded_files))

    print("Crawling completed.")
