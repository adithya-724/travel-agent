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
    location_ls = location.split(' ')
    num_posts = 50
    fetched_posts = 0
    comment_exceed = 0
    invalid_urls_posts = 0
    irrelevant_posts = 0

    def custom_filter(record):
        return record["level"].name in ["DEBUG", "ERROR", "SUCCESS"]

    logger.remove()  # Remove the default handler
    logger.add("app.log", filter=custom_filter, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")


    for subreddit in SUBREDDIT_LS:
        
        urls = fetch_posts_url(location,'relevance','year',subreddit,str(num_posts))
        fetched_posts += len(urls)
        # print('Fetched urls')
        logger.debug('Fetched urls')
        pprint(urls)
        valid_posts = 0

        for url in urls:
            if 'reddit' in url:
                submission = reddit.submission(url=url)
                post_title = submission.title
                post_title_lower = post_title.lower()
                text_body = submission.selftext
                text_body_lower = text_body.lower()

                combined_txt = f'Title:{post_title_lower}\n Body:{text_body_lower}'
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
                            all_comments += extract_comments(top_level_comment)
                            all_comments += '-----------------------------\n'
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


    logger.debug('Total posts fetched : {}',fetched_posts)

    logger.debug('Total posts with invalid urls : {}',invalid_urls_posts)
    logger.debug('Total posts with comments > 200 : {}',comment_exceed)
    logger.debug('Total posts with no matching keywords : {}',irrelevant_posts)
    
    logger.success('Fetched {} valid posts',valid_posts)
    logger.success('Info : {}',all_comments)

    return all_comments


fetch_reddit_content('thailand phuket bangkok krabi')