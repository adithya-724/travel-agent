import requests
from dotenv import load_dotenv
import os
from pydantic import BaseModel, field_validator, ValidationError
from pprint import pprint

# load env vars
load_dotenv()


class RedditPost(BaseModel):
    title: str
    url: str

    @field_validator('url')
    def validate_reddit_url(cls, value):
        if "reddit" not in value:
            raise ValueError("URL must contain the substring 'reddit'")
        return value

def fetch_posts(query):
    url = os.getenv('reddit_url')

    querystring = {"query":query,"sort":"RELEVANCE","time":"all","nsfw":"0"}

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

    pprint(valid_posts)
    pprint(errors)
    # print(type(response_json))
    # final_result = RedditPost(title = response_json['subreddit']['title'],url = response_json['subreddit']['url'])
    # print(final_result)



fetch_posts('thailand tourism & snorkelling')