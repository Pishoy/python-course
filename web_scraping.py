# this script to scrap or get information of imdb websites about films 
# you can choose the year of films that is the films created on it, get (rate,vote)

# reference https://www.dataquest.io/blog/web-scraping-beautifulsoup/

from time import sleep
from random import randint
from time import time
from requests import get
from bs4 import BeautifulSoup
from IPython.core.display import clear_output
from warnings import warn
import ipdb
# Redeclaring the lists to store data in
names = []
years = []
imdb_ratings = []
metascores = []
votes = []

# Preparing the monitoring of the loop
start_time = time()
requests = 0

# set header to get english lang
headers = {"Accept-Language": "en-US, en;q=0.5"}
# to trace functions
#import ipdb;ipdb.set_trace()
# For every year in the interval 2000-2017 , let now one year 2018
for year_url in [str(i) for i in range(2018,2019)]:

    # For every page in the interval 1-4 , let try 3
    for page in [ str(x) for x in range (1,2)]:

        # Make a get request
        response = get('http://www.imdb.com/search/title?release_date=' + year_url +
        '&sort=num_votes,desc&page=' + page, headers = headers)

        # Pause the loop
        sleep(randint(8,15))

        # Monitor the requests
        requests += 1
        elapsed_time = time() - start_time
        print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
        clear_output(wait = True) # to shown one output on your screen of above print , clear old output

        # Throw a warning for non-200 status codes
        if response.status_code != 200:
            warn('Request: {}; Status code: {}'.format(requests, response.status_code))

        # Break the loop if the number of requests is greater than expected
        if requests > 72:
            warn('Number of requests was greater than expected.')
            break

        # Parse the content of the request with BeautifulSoup
        page_html = BeautifulSoup(response.text, 'html.parser')

        # Select all the 50 movie containers from a single page
        mv_containers = page_html.find_all('div', class_ = 'lister-item mode-advanced')

        # For every movie of these 50
        for container in mv_containers:
            # If the movie has a Metascore, then:
            if container.find('div', class_ = 'ratings-metascore') is not None:

                # Scrape the name
                name = container.h3.a.text
                names.append(name)

                # Scrape the year
                year = container.h3.find('span', class_ = 'lister-item-year').text
                years.append(year)

                # Scrape the IMDB rating
                imdb = float(container.strong.text)
                imdb_ratings.append(imdb)

                # Scrape the Metascore
                m_score = container.find('span', class_ = 'metascore').text
                metascores.append(int(m_score))

                # Scrape the number of votes
                vote = container.find('span', attrs = {'name':'nv'})['data-value']
                votes.append(int(vote))
            print ('film name is {} created in year {} and its rating is {} and has a {} metascore and {} votes'.format (name,year,imdb,m_score,vote))


import pandas as pd

test_df = pd.DataFrame({'movie': names,
                       'year': years,
                       'imdb': imdb_ratings,
                       'metascore': metascores,
                       'votes': votes})
print(test_df.info())
test_df
print (test_df[1:])
