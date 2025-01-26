import serpapi
from serpapi import GoogleSearch
from langchain_community.tools import tool
from dotenv import load_dotenv
import os
import serpapi
from pprint import pprint   

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
    top_5 = results['properties'][:100]
    return top_5


# def hotels_finder(location,check_in_date,check_out_date,adults= 2,children = 0,rooms = 1,):
#     '''
#     Find hotels using the Google Hotels engine.

#     Returns:
#         dict: Hotel search results.
#     '''

#     params = {
#         'api_key': os.environ.get('SERP_API_KEY'),
#         'engine': 'google_hotels',
#         'hl': 'en',
#         'gl': 'us',
#         'q': location,
#         'check_in_date': check_in_date,
#         'check_out_date': check_out_date,
#         'currency': 'USD',
#         'adults': adults,
#         'children': children,
#         'rooms': rooms
#         # 'sort_by': sort_by,
#         # 'hotel_class': params.hotel_class
#     }

#     # search = serpapi.search(params)
#     # results = search.data
#     search = GoogleSearch(params)
#     results = search.get_dict()
#     # print(results)
#     pprint(results['properties'][:5])
#     # return results['properties'][:5]


# hotels_finder('mumbai resorts','2025-05-21','2025-05-25')