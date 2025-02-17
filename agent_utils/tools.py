# from serpapi import GoogleSearch
import serpapi
from langchain_community.tools import tool
from dotenv import load_dotenv
import os
import requests
from utils.reddit_utils import extract_comments, reddit, fetch_posts_url
from loguru import logger
from pprint import pprint

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
    SUBREDDIT_LS = ["travelhacks", "travel"]
    all_comments = ""
    # keywords_str = ' '.join(location)
    print(location)
    location_ls = location.split(" ")
    num_posts = 50
    fetched_posts = 0
    comment_exceed = 0
    invalid_urls_posts = 0
    irrelevant_posts = 0

    def custom_filter(record):
        return record["level"].name in ["DEBUG", "ERROR", "SUCCESS"]

    logger.remove()  # Remove the default handler
    logger.add(
        "app.log",
        filter=custom_filter,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )

    for subreddit in SUBREDDIT_LS:
        urls = fetch_posts_url(location, "relevance", "year", subreddit, str(num_posts))
        fetched_posts += len(urls)
        # print('Fetched urls')
        logger.debug("Fetched urls")
        pprint(urls)
        valid_posts = 0

        for url in urls:
            if "reddit" in url:
                submission = reddit.submission(url=url)
                post_title = submission.title
                post_title_lower = post_title.lower()
                text_body = submission.selftext
                text_body_lower = text_body.lower()

                combined_txt = f"Title:{post_title_lower}\n Body:{text_body_lower}"
                # logger.debug(combined_txt)
                # print(post_title)
                # print(submission.num_comments)

                # Only fetching posts which have the keyword in the title
                if any(keyword.lower() in combined_txt for keyword in location_ls):
                    # Limiting posts with comments under 200
                    if submission.num_comments < 200:
                        valid_posts += 1
                        submission.comments.replace_more(limit=None)
                        for top_level_comment in submission.comments:
                            top_level_comment.refresh()
                            top_level_comment.replies.replace_more(limit=None)
                            total_replies = len(top_level_comment.replies.list())
                            upvotes = top_level_comment.score

                            # removing comments with no upvotes and replies
                            if upvotes <= 1 and total_replies < 1:
                                continue

                            all_comments += extract_comments(top_level_comment)
                            all_comments += "-----------------------------\n"
                    else:
                        comment_exceed += 1
                        # logger.error('Post had more than 200 comments')
                        continue
                else:
                    irrelevant_posts += 1
                    # logger.error('No matching keyword',post_title)
                    continue
            else:
                invalid_urls_posts += 1
                # logger.error('Not a valid reddit url')

    logger.debug("Total posts fetched : {}", fetched_posts)

    logger.debug("Total posts with invalid urls : {}", invalid_urls_posts)
    logger.debug("Total posts with comments > 200 : {}", comment_exceed)
    logger.debug("Total posts with no matching keywords : {}", irrelevant_posts)

    logger.success("Fetched {} valid posts", valid_posts)
    logger.success("Info : {}", all_comments)

    return all_comments
