from langchain_community.tools.reddit_search.tool import RedditSearchRun
from langchain_community.utilities.reddit_search import RedditSearchAPIWrapper
from langchain_community.tools.reddit_search.tool import RedditSearchSchema
import praw
from praw.models import MoreComments
import re
import os
from dotenv import load_dotenv
from pprint import pprint
from utils.reddit_utils import *


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

def fetch_reddit_content(location):
    """
    Fetches the comments for the given keyword

    Args:
        location (str): Location for which the reddit information has to be scraped
    """
    SUBREDDIT_LS = ['travelhacks','travel']
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


fetch_reddit_content('thailand phuket bangkok krabi')