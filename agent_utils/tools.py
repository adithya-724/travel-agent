# from serpapi import GoogleSearch
import serpapi
from langchain_community.tools import tool
from dotenv import load_dotenv
import os
import requests
from utils.reddit_utils import extract_comments, reddit, fetch_posts_url

# from pydantic import BaseModel, Field
load_dotenv()


@tool("HotelFinder")
def hotels_finder(
    location,
    check_in_date,
    check_out_date,
    adults=2,
    children=0,
    rooms=1,
    property_types=21,
    amenties=None,
    max_price=None,
):
    """
    Searches for hotels in a specified location and date range using SerpApi's Google Hotels engine.

    Args:
        location (str): The destination city or region to search for hotels.
        check_in_date (str): The desired check-in date in 'YYYY-MM-DD' format.
        check_out_date (str): The desired check-out date in 'YYYY-MM-DD' format.
        adults (int, optional): The number of adult guests. Defaults to 2.
        children (int, optional): The number of child guests. Defaults to 0.
        rooms (int, optional): The number of hotel rooms required. Defaults to 1.
        max_price (int,optional) : The maximum price to limit the hotel search for.
        property_types (str, optional): A comma-separated string of property type codes to filter the search results.
            Defaults to '21'.
            Examples:
                - Single property type:
                    '14'
                - Multiple property types:
                    '14,12,13'

            Note: Replace '14', '12', '13' with the appropriate property type codes.

        amenities (str, optional): A comma-separated string of amenity codes to filter the search results.
            Defaults to None.

            Examples:
                - Single amenity:
                    '35'
                - Multiple amenities:
                    '35,9,19'

            Note: Replace '35', '9', '19' with the appropriate amenity codes as per SerpApi's documentation.

    Returns:
        list: A list of dictionaries containing details of the top 10 hotel properties found.
    """

    params = {
        "api_key": os.environ.get("SERP_API_KEY"),
        "engine": "google_hotels",
        "hl": "en",
        "gl": "us",
        "q": location,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "currency": "INR",
        "adults": adults,
        "children": children,
        "rooms": rooms,
        "property_types": property_types,
        "amenties": amenties,
        "sort_by": 8,
        "max_price": max_price,
        # 'hotel_class': params.hotel_class
    }

    search = serpapi.search(params)
    results = search.data
    top_50 = results["properties"][:50]
    return top_50


@tool("RedditCommentFinder")
def get_reddit_comments(keywords: str):
    """
    Find relevant reddit comments based on user's query. This tool accepts a python string as a input.

    Input:
    query (str) : Query to be searched

    Returns:
        string: Reddit comments
    """
    url = os.getenv("reddit_url_comments")

    querystring = {"query": keywords, "sort": "RELEVANCE", "nsfw": "0"}

    headers = {
        "x-rapidapi-key": os.getenv("rapid_api_key"),
        "x-rapidapi-host": os.getenv("rapid_api_host"),
    }
    all_comments = ""

    for i in range(2):
        response = requests.get(url, headers=headers, params=querystring)
        # print(response.json())
        response_json = response.json()["data"]

        for item in response_json:
            all_comments += item["text"] + "\n"
        next_page_cursor = response.json()["pageInfo"]

        if next_page_cursor["hasNextPage"]:
            querystring["cursor"] = next_page_cursor["endCursor"]
            continue
        else:
            break

    return all_comments


@tool("reddit_comment_scraper")
def fetch_reddit_content(location):
    """
    Fetches the comments for the given keyword

    Args:
        location (str): Location for which the reddit information has to be scraped
    """
    SUBREDDIT_LS = ["travelhacks"]
    all_comments = ""
    # keywords_str = ' '.join(location)
    print(location)

    for subreddit in SUBREDDIT_LS:
        urls = fetch_posts_url(location, "relevance", "year", subreddit, "5")
        print("Fetched urls")
        print(urls)
        for url in urls:
            if "reddit" in url:
                submission = reddit.submission(url=url)
                print(submission.num_comments)
                if submission.num_comments < 200:
                    submission.comments.replace_more(limit=None)

                    for top_level_comment in submission.comments:
                        all_comments += extract_comments(top_level_comment)
                        all_comments += "-----------------------------\n"
                else:
                    continue

    return all_comments
