import os
import requests
import argparse
from collections import deque
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from text_extraction import extract_text, save_text
from handle_visted_unvisted import save_link, get_links, get_downloaded_links
from handle_downloads import extract_links_from_file, download_file
from handle_error import log_error
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import time
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


def use_dynamic_crawling(urls, url, cookie_to_be_accepted, cookie_class, visited_links_file, unvisited_links_file, failed_links_file, visited_links, unvisited_links, failed_links, downloaded_files, driver):
    try:
        # Open the web page
        driver.get(url)
        if cookie_to_be_accepted and cookie_class:
            # Wait for the cookie popup to appear
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME, "body")))

            # Find the accept button using CSS selector
            # Class = pcf-button button button--normalised button--secondary pull-right cookie-button
            accept_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"button[class*='{cookie_class}']")))

            # Scroll into view if necessary
            driver.execute_script("arguments[0].scrollIntoView(true);", accept_button)

            # Click the accept button
            accept_button.click()
            cookie_to_be_accepted = False
    except Exception as e:
        failed_links.add(url)
        # Saving failed urls
        save_link(url, failed_links_file)
        log_error(f"Failed to accept cookie at URL using ChromeDriver {url}: {e}")
    try:
        #Pausing for the driver to load
        time.sleep(2)
        # Extract content from the body tag
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
        text = driver.find_element(By.XPATH, "//body").text
        file_name = urlparse(url).netloc.replace('.', '_') + urlparse(url).path.replace('/', '_')
        save_text(text, file_name)
        # Saving the newly visiting url
        save_link(url, visited_links_file)
        visited_links.add(url)

        # Find all anchor tags (links) on the page
        links = driver.find_elements(By.TAG_NAME, "a")

        # Extract link URLs from anchor tags
        for link in links:
            full_url = link.get_attribute("href")
            if full_url:  # Check if href is not None (to avoid errors)
                if not full_url in visited_links and not full_url in unvisited_links and not full_url in failed_links:
                    # If the file ends with the below words then it is a downloadble URL, if not then send the crawler to newly found url
                    if full_url.endswith(('.pdf', '.docx', '.csv', '.xls', '.xlsx', '.txt', '.zip', '.mp4', '.mp3', '.cgi')):
                        downloadable_files(full_url, urls, visited_links_file, unvisited_links_file, failed_links_file, visited_links, unvisited_links, failed_links, downloaded_files)
                    else:
                        #Adding the new url to que and saving it 
                        unvisited_links.add(full_url)
                        urls.append(full_url)
                        save_link(full_url, unvisited_links_file)
        return cookie_to_be_accepted
    except Exception as e:
        log_error(f"Error processing URL {url}: {e}")


def use_static_crawling(urls, url, visited_links_file, unvisited_links_file, failed_links_file, visited_links, unvisited_links, failed_links, downloaded_files):
    try:
        #Fetching response
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        failed_links.add(url)
        # Saving failed urls
        save_link(url, failed_links_file)
        log_error(f"Failed to fetch URL {url}: {e}")
        return
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


def crawl(urls, visited_links_file, unvisited_links_file, failed_links_file, visited_links, unvisited_links, failed_links, downloaded_files, driver = None, cookie_class=None):
    """_summary_

    :param url: URL where we intend to send the crawler
    """
    cookie_to_be_accepted=True # Need to do this only once
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
        if not driver:
            use_static_crawling(urls, url, visited_links_file, unvisited_links_file, failed_links_file, visited_links, unvisited_links, failed_links, downloaded_files)
        else:
            cookie_to_be_accepted = use_dynamic_crawling(urls, url, cookie_to_be_accepted, cookie_class, visited_links_file, unvisited_links_file, failed_links_file, visited_links, unvisited_links, failed_links, downloaded_files, driver)
                


# Starting point
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Web crawler script with Selenium and Beautiful Soup options.')
    parser.add_argument('--use_selenium', action='store_true', help='Use Selenium with Chrome for crawling')
    parser.add_argument('--cookie_class', type=str, help='Class name of the cookie accept button', default=None)
    
    args = parser.parse_args()

    driver = None

    if args.use_selenium:
        # Set up Chrome options to handle downloads
        chrome_options = Options()
        prefs = {
            "download.default_directory": 'downloads',  # Change default directory for downloads
            "download.prompt_for_download": False,  # To auto download the file
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True  # To enable safe browsing
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

       # Set up the WebDriver (make sure the path to the ChromeDriver is correct)
        chrome_service = ChromeService(executable_path='/opt/homebrew/bin/chromedriver')
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    visited_links_file = 'links/visited_links.txt'
    unvisited_links_file = 'links/unvisited_links.txt'
    failed_links_file = 'links/failed_links.txt'
    
    visited_links = get_links(visited_links_file)
    unvisited_links = get_links(unvisited_links_file)
    failed_links = get_links(failed_links_file)
    downloaded_files = get_downloaded_links('downloads')

    if len(unvisited_links):
        crawl(deque(unvisited_links), visited_links_file, unvisited_links_file, failed_links_file, set(visited_links), set(unvisited_links), set(failed_links), set(downloaded_files), driver, args.cookie_class)
    else:   
        initial_urls = deque(['https://www.enisa.europa.eu/publications#c3=2014&c3=2024&c3=false&c5=publicationDate&reversed=on&b_start=0', 
                              'https://www.enisa.europa.eu/publications#c3=2014&c3=2024&c3=false&c5=publicationDate&reversed=on&b_start=0&c4=cyber+security',
                              'https://www.enisa.europa.eu/publications/corporate-documents#c5=2014&c5=2024&c5=false&c6=effective&reversed=on&b_start=0&c4=cyber+security',
                              'https://www.enisa.europa.eu/publications/info-notes#c3=2014&c3=2024&c3=false&c6=infonote_publication_date&reversed=on&b_start=0&c4=cyber+security',
                              'https://www.enisa.europa.eu/publications/enisa-position-papers-and-opinions#c1=Deliverable&c1=File&c2=effective&reversed=on&b_start=0&c4=cyber+security',
                              'https://www.enisa.europa.eu/publications/ed-speeches#c1=Deliverable&c1=File&c3=effective&reversed=on&b_start=0&c4=cyber+security',
                              'https://www.enisa.europa.eu'])
        crawl(initial_urls, visited_links_file, unvisited_links_file, failed_links_file, set(visited_links), set(unvisited_links), set(failed_links), set(downloaded_files), driver, args.cookie_class)

    # Once you're done, close the browser
    if driver:
        driver.quit()
    
    print("Crawling completed.")

