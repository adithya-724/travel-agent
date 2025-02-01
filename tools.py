import serpapi
from serpapi import GoogleSearch
from langchain_community.tools import tool
from dotenv import load_dotenv
import os
import serpapi
from pprint import pprint   
import requests

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
    url = "https://reddit-scraper2.p.rapidapi.com/search_comments"

    querystring = {"query":keywords,"sort":"RELEVANCE","nsfw":"0"}
    print(querystring)

    headers = {
        "x-rapidapi-key": "d032a9d7f1mshb483cfb3094b15dp1942a4jsnae90643d6479",
        "x-rapidapi-host": "reddit-scraper2.p.rapidapi.com"
    }
    all_comments = ''
    
    for i in range(2):
        response = requests.get(url, headers=headers, params=querystring)
        response_json = response.json()['data']
        print(response_json)
        for item in response_json:
            all_comments += item['text'] + '\n'
        next_page_cursor = response.json()['pageInfo']

        if next_page_cursor['hasNextPage'] == True:
            querystring['cursor'] = next_page_cursor['endCursor']
            continue
        else:
            break
        

    return all_comments