from langchain_community.tools.reddit_search.tool import RedditSearchRun
from langchain_community.utilities.reddit_search import RedditSearchAPIWrapper
from langchain_community.tools.reddit_search.tool import RedditSearchSchema
import praw
from praw.models import MoreComments
import re
import os
from dotenv import load_dotenv


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

def fetch_reddit_content(keywords):
    """
    Fetches the comments for the given subreddits

    Args:
        subreddits_ls (List): List containing the subreddits
    """
    def fetch_posts_url(query,sort,time_filter,subreddit,limit):
        search_params = RedditSearchSchema(
            query=query, sort=sort, time_filter=time_filter, subreddit=subreddit, limit=limit
        )


        result = search.run(tool_input=search_params.model_dump())
        print(result)
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, result)
        return urls 

    # https://praw.readthedocs.io/en/stable/tutorials/comments.html
    # # print(reddit.user.me())

    comments =  {}

    def fetch_comments(url):
        submission = reddit.submission(url=url)
        submission.comments.replace_more(limit=None)

        # Fetching top level comments and their replies
        for top_level_comment in submission.comments:
            for second_level_comment in top_level_comment.replies:
                # print(second_level_comment.body)
                comments[top_level_comment.body] = second_level_comment.body
            
    
    keywords_str = ' '.join(keywords)
    print(keywords_str)
    # for subreddit in subreddits_ls:
    urls = fetch_posts_url(keywords_str,'hot','year','travel','1')
    print('Fetched urls')
    print(urls)
    for url in urls:
        if 'reddit' in url:
            fetch_comments(url)
    
    return comments


comments  = fetch_reddit_content(['thailand tourism snorkelling'])
# final_info  = '\n'.join(comments)
print(comments)
