from langchain_community.tools.reddit_search.tool import RedditSearchRun
from langchain_community.utilities.reddit_search import RedditSearchAPIWrapper
from langchain_community.tools.reddit_search.tool import RedditSearchSchema
import praw
from praw.models import MoreComments
import re
import os
from dotenv import load_dotenv
from pprint import pprint


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

def fetch_reddit_content(keywords,subreddits_ls):
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

    all_comments = ''

    def extract_comments(comment, level=0):
        if level == 0:
            header = "Comment:"
        else:
            header = "Reply:"
        
        indent = '    ' * level  # Indentation for nested comments
        if level == 0:
            formatted_comment = f"{indent}{header}\n{indent}{comment.body}\n\n"
        else:
            formatted_comment = f"{indent}{header}{level}\n{indent}{comment.body}\n\n"
        
        # Ensure all replies are loaded
        comment.replies.replace_more(limit=None)
        
        for reply in comment.replies:
            formatted_comment += extract_comments(reply, level + 1)
        
        return formatted_comment


    keywords_str = ' '.join(keywords)
    print(keywords_str)
    for subreddit in subreddits_ls:
        urls = fetch_posts_url(keywords_str,'relevance','year',subreddit,'1')
        print('Fetched urls')
        print(urls)
        for url in urls:
            if 'reddit' in url:
                comments = ''
                submission = reddit.submission(url=url)
                print(submission.num_comments)
                submission.comments.replace_more(limit=None)
                
                for top_level_comment in submission.comments:
                    all_comments += extract_comments(top_level_comment)
                    all_comments += '-----------------------------\n'
                # all_comments += fetch_comments(url) + '\n\n' + '-----------------------------------------------------------------------------------------'
    
    return all_comments


comments  = fetch_reddit_content(['phuket'],['travelhacks'])
# final_info  = '\n'.join(comments)
print(comments)

