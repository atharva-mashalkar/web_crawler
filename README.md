# Web Crawler

## Overview
The Web Crawler is a Python-based tool designed to traverse and extract information from websites. It systematically browses web pages, collects data, and saves it for further analysis. This tool can be used for various purposes, such as web scraping, data mining, and research.

## Features

- **Recursive Crawling**: Automatically follows links on web pages to crawl an entire website.
- **Data Extraction**: Extracts text data from web pages.
- **Error Handling**: Manages and logs errors encountered during the crawling process.
- **Download Management**: Handles downloading and saving of web page content.
- **Visited/Unvisited Management**: Tracks visited and unvisited URLs to avoid redundant processing.
- **Dynamic Crawling**: (Planned) Support for crawling pages that load content dynamically using JavaScript.

## Prerequisites

- Python 3.x
- Required Python libraries (install via `requirements.txt`)

## Installation
1. **Clone the Repository**
   ```bash
   git clone https://github.com/atharva-mashalkar/web_crawler.git
   cd web_crawler
   ```
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
    ```
  
## Usage

1. Basic Usage
    To start the web crawler, run the `web_crawler.py` script with a starting URL:
    ```sh
    python web_crawler.py
    ```
    Replace `initial_urls` in the `web_crawler.py` file with the URL of the website you want to crawl.
2. For Dynamic Crawling
   For website which render JavaScript content use the below patch
   ```sh
   python web_crawler.py --use_selenium --cookie_class << pass class name of the cookie click button on you required domain >>
   ```
   This will use Selenium to load JavaScript content from your required website.

## Customization

You can customize the behavior of the web crawler by modifying the following files:

- **web_crawler.py**: Main script to start the crawler.
- **handle_downloads.py**: Manages downloading and saving web content.
- **handle_error.py**: Contains error handling logic.
- **handle_visited_unvisited.py**: Manages the lists of visited and unvisited URLs.
- **text_extraction.py**: Handles text extraction from web pages.

## Adding Dynamic Crawling

To add support for dynamic crawling, you can use a tool like Selenium or Playwright. Here's a basic example using Selenium:

1. Install Selenium:
    ```sh
    pip install selenium
    ```

2. Update `requirements.txt` to include Selenium.

3. Add dynamic crawling logic to `web_crawler.py`:
    ```python
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    def dynamic_crawl(url):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        content = driver.page_source
        driver.quit()
        return content
    ```

4. Integrate `dynamic_crawl` function into the crawling workflow.

## Project Structure


- **web_crawler.py**: Main script to initiate and control the web crawler.
- **handle_downloads.py**: Module to manage downloading and saving web page content.
- **handle_error.py**: Module for error handling and logging.
- **handle_visited_unvisited.py**: Module to manage tracking of visited and unvisited URLs.
- **text_extraction.py**: Module to extract and process text data from web pages.
- **requirements.txt**: List of Python dependencies.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

***Star the repo if you like it***

