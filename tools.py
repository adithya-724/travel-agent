import serpapi
from serpapi import GoogleSearch
from langchain_community.tools import tool
from dotenv import load_dotenv
import os
import serpapi
from pprint import pprint   
import requests
from utils.reddit_utils import *

# from pydantic import BaseModel, Field
load_dotenv()

@tool('HotelFinder')
def hotels_finder(location,check_in_date,check_out_date,adults= 2,children = 0,rooms = 1,):
    '''
    Find hotels using the Google Hotels engine.

    Returns:
        dict: Hotel search results.
    '''

    params = {
        'api_key': os.environ.get('SERP_API_KEY'),
        'engine': 'google_hotels',
        'hl': 'en',
        'gl': 'us',
        'q': location,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'currency': 'INR',
        'adults': adults,
        'children': children,
        'rooms': rooms
        # 'sort_by': sort_by,
        # 'hotel_class': params.hotel_class
    }


    search = GoogleSearch(params)
    results = search.get_dict()
    top_5 = results['properties'][:10]
    return top_5

@tool('RedditCommentFinder')
def get_reddit_comments(keywords : str):
    '''
    Find relevant reddit comments based on user's query. This tool accepts a python string as a input.

    Input:
    query (str) : Query to be searched

    Returns:
        string: Reddit comments
    '''
    url = os.getenv('reddit_url_comments')

    querystring = {"query":keywords,"sort":"RELEVANCE","nsfw":"0"}

    headers = {
        "x-rapidapi-key": os.getenv('rapid_api_key'),
        "x-rapidapi-host": os.getenv('rapid_api_host')
    }
    all_comments = ''

    for i in range(2):
        response = requests.get(url, headers=headers, params=querystring)
        # print(response.json())
        response_json = response.json()['data']

        for item in response_json:
            all_comments += item['text'] + '\n'
        next_page_cursor = response.json()['pageInfo']

        if next_page_cursor['hasNextPage'] == True:
            querystring['cursor'] = next_page_cursor['endCursor']
            continue
        else:
            break
        

    return all_comments



@tool('reddit_comment_scraper')
def fetch_reddit_content(location):
    """
    Fetches the comments for the given keyword

    Args:
        location (str): Location for which the reddit information has to be scraped
    """
    SUBREDDIT_LS = ['travelhacks']
    all_comments = ''
    # keywords_str = ' '.join(location)
    print(location)
    

    for subreddit in SUBREDDIT_LS:
        urls = fetch_posts_url(location,'relevance','year',subreddit,'5')
        print('Fetched urls')
        print(urls)
        for url in urls:
            if 'reddit' in url:
                comments = ''
                submission = reddit.submission(url=url)
                print(submission.num_comments)
                if submission.num_comments < 200:
                    submission.comments.replace_more(limit=None)
                    
                    for top_level_comment in submission.comments:
                        all_comments += extract_comments(top_level_comment)
                        all_comments += '-----------------------------\n'
                else:
                    continue
    
    return all_comments

