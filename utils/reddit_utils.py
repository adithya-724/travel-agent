import requests
from dotenv import load_dotenv
import os
from pydantic import BaseModel, field_validator, ValidationError
from pprint import pprint
import praw
from langchain_community.tools.reddit_search.tool import RedditSearchRun
from langchain_community.utilities.reddit_search import RedditSearchAPIWrapper
from langchain_community.tools.reddit_search.tool import RedditSearchSchema
import re

# load env vars
load_dotenv()

reddit = praw.Reddit(
    client_id= os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    password=os.getenv('reddit_app_pass'),
    user_agent="Comment Extraction (by u/USERNAME)",
    username="azio777",
)


search = RedditSearchRun(
    api_wrapper=RedditSearchAPIWrapper(
        reddit_client_id=os.getenv('client_id'),
        reddit_client_secret=os.getenv('client_secret'),
        reddit_user_agent=os.getenv('user_agent'),
    )
)

class RedditPost(BaseModel):
    title: str
    url: str

    @field_validator('url')
    def validate_reddit_url(cls, value):
        if "reddit" not in value:
            raise ValueError("URL must contain the substring 'reddit'")
        return value

def fetch_posts_url(query,sort,time_filter,subreddit,limit):
    search_params = RedditSearchSchema(
        query=query, sort=sort, time_filter=time_filter, subreddit=subreddit, limit=limit
    )


    result = search.run(tool_input=search_params.model_dump())
    print(result)
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, result)
    return urls 


def fetch_posts(query):
    url = os.getenv('reddit_url')

    querystring = {"query":query,"sort":"RELEVANCE","time":"year","nsfw":"0"}

    headers = {
        "x-rapidapi-key": os.getenv('rapid_api_key'),
        "x-rapidapi-host": os.getenv('rapid_api_host')
    }

    response = requests.get(url, headers=headers, params=querystring)
    # print(response)
    response_json = response.json()['data']


    def process_reddit_posts(json_data_list):
        valid_posts = []
        errors = []

        for data in json_data_list:
            try:
                post = RedditPost(title=data["title"], url=data["url"])
                valid_posts.append(post)
            except ValidationError as e:
                errors.append({"data": data, "error": str(e)})

        return valid_posts, errors
    
    valid_posts, errors = process_reddit_posts(response_json)

    # pprint(valid_posts)
    # pprint(errors)

    return valid_posts


def fetch_comments(url):
    submission = reddit.submission(url=url)
    submission.comments.replace_more(limit=None)
    comments = {}
    # Fetching top level comments and their replies
    for top_level_comment in submission.comments:
        for second_level_comment in top_level_comment.replies:
            # print(second_level_comment.body)
            comments[top_level_comment.body] = second_level_comment.body


    return comments

def get_comments(query):
    url = "https://reddit-scraper2.p.rapidapi.com/search_comments"

    querystring = {"query":query,"sort":"RELEVANCE","nsfw":"0"}

    headers = {
        "x-rapidapi-key": "d032a9d7f1mshb483cfb3094b15dp1942a4jsnae90643d6479",
        "x-rapidapi-host": "reddit-scraper2.p.rapidapi.com"
    }
    all_comments = ''
    
    for i in range(10):
        response = requests.get(url, headers=headers, params=querystring)
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
    # print(response.json())


pprint(get_comments('thailand tourism snorkelling'))
