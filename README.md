# Web Crawler

## Overview
The Web Crawler is a Python-based tool designed to traverse and extract information from websites. It systematically browses web pages, collects data, and saves it for further analysis. This tool can be used for various purposes, such as web scraping, data mining, and research.

## Features
- **Recursive Crawling**: Automatically follows links on web pages to crawl an entire website.
- **Data Extraction**: Extracts text data from web pages.
- **Error Handling**: Manages and logs errors encountered during the crawling process.
- **Download Management**: Handles downloading and saving of web page content.
- **Visited/Unvisited Management**: Tracks visited and unvisited URLs to avoid redundant processing.

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
To start the web crawler, run the web_crawler.py script with a starting URL:

  ```bash
  python web_crawler.py
  ```

Replace inital_urls in the web_crawler.py file with the URL of the website you want to crawl.

## Customization
You can customize the behavior of the web crawler by modifying the following files:

- **web_crawler.py: Main script to start the crawler.**
- **handle_downloads.py: Manages downloading and saving web content.**
- **handle_error.py: Contains error handling logic.**
- **handle_visited_unvisited.py: Manages the lists of visited and unvisited URLs.**
- **text_extraction.py: Handles text extraction from web pages.**

## Project Structure

- **web_crawler.py: Main script to initiate and control the web crawler.**
- **handle_downloads.py: Module to manage downloading and saving web page content.**
- **handle_error.py: Module for error handling and logging.**
- **handle_visited_unvisited.py: Module to manage tracking of visited and unvisited URLs.**
- **text_extraction.py: Module to extract and process text data from web pages.**
- **requirements.txt: List of Python dependencies.**

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.
