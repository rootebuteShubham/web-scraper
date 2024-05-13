# web-scraper
Steps to execute the web scraper code
pip install -U requests
pip install -U BeautifulSoup
pip install -U spacy
python -m spacy download en_core_web_sm
If using pycharm or any other editor, you can execute the main function directly. If using command line, you can execute the nasdaq_web_scraper.py file.
The output file will be created with the name extracted_date.txt that will contain
  1. Stock/Company Names
  2. Publication Time
  3. Author
  4. Topics, if available
