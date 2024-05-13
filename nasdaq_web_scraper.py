import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import pandas as pd
from io import StringIO
import spacy
import logging
import json

def write_to_file(data, file_path):
    """
       Writes extracted company information to a text file.

       This function takes a dictionary containing company stock names, publication time,
       and author information, and writes them to a specified file in a human-readable format.

       Parameters:
       - data (dict): A dictionary containing extracted information with keys 'company_names',
                      'metadata' which includes 'publication_timestamp' and 'author'.
       - file_path (str): The path of the file where the data should be written.

       Returns:
       - None: This function does not return any value.

       Raises:
       - IOError: An error occurred accessing the file or writing to it.
       """
    try:
        with open(file_path, 'w') as file:
            file.write("Company Company/Stock Names:\n")
            for name in data['company_names']:
                file.write(f"- {name}\n")
            file.write("\nPublication Time:\n")
            file.write(f"- {data['metadata'].get('publication_timestamp', 'Not Available')}\n")
            file.write("\nAuthor:\n")
            file.write(f"- {data['metadata'].get('author', 'Not Available')}\n")
            file.write("\nTopics:\n")
            file.write(f"- {data['metadata'].get('topics', 'Not Available')}\n")
    except IOError as e:
        print(f"Error writing to file: {e}")

def extract_info(url, config):
    """
        Fetches and extracts information from a given URL.

        Parameters:
            url (str): The URL to fetch.
            config (dict): Configuration dict containing CSS selectors.

        Returns:
            dict: A dictionary containing the extracted content and metadata.
        """

    logger.info("Fetching starts")
    nlp = spacy.load("en_core_web_sm")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()  # Ensure we catch HTTP errors
    except HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        return {"error": f"HTTP error occurred: {http_err}"}
    except Timeout as timeout_err:
        logger.error(f"Timeout error: {timeout_err}")
        return {"error": f"Timeout error: {timeout_err}"}
    except ConnectionError as conn_err:
        logger.error(f"Connection error: {conn_err}")
        return {"error": f"Connection error: {conn_err}"}
    except Exception as err:
        logger.error(f"An error occurred: {err}")
        return {"error": f"An error occurred: {err}"}

    soup = BeautifulSoup(response.text, 'html.parser')
    article_content = soup.select_one(config['content_selector']).text if soup.select_one(config['content_selector']) else 'Content not available'
    metadata = {}
    for key, selector in config['metadata'].items():
        element = soup.select_one(selector)
        metadata[key] = element.text.strip() if element else f'{key} not available'
    doc = nlp(article_content)
    company_names = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    return {
        'content': article_content,
        'metadata': metadata,
        'company_names': set(list(company_names))
    }

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    config = {
        'content_selector': 'div.body__content',  # CSS selector for the main content
        'metadata': {
            'publication_timestamp': 'p.jupiter22-c-author-byline__timestamp',  # CSS selector for timestamp
            'author': 'span.jupiter22-c-author-byline__author-no-link'  # CSS selector for author
        }
    }
    url = 'https://www.nasdaq.com/articles/should-investors-buy-the-artificial-intelligence-technology-etf-instead-of-individual-ai'
    info = extract_info(url, config)
    print(info)
    if 'error' not in info:
        company_stock_names = info['company_names']
        publication_time = info['metadata'].get('publication_timestamp')
        author = info['metadata'].get('author')

        file_path = 'extracted_data.txt' # Data can be saved in a database or another object storage such as S3 or GCS
        write_to_file(info, file_path)
        print(f"Data successfully written to {file_path}")
    else:
        print(info['error'])
