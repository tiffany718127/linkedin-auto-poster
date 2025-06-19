import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import requests
load_dotenv() #load tokens from .env
LINKEDIN_TOKEN=os.getenv("LINKEDIN_ACCESS_TOKEN") # get linkedin API token from env
ORG_URN= os.getenv("LINKEDIN_ORGANIZATION_URN") # get company page URN

def get_blog(url):
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True) #launch chromium browser
        page=browser.new_page() #open new page
        page.goto(url) # direct to the blog website
        page.wait_for_load_state('networkidle') # wait till finishing loading
        title=page.title()
        paragraphs = page.query_selector_all("p")
        # Join all paragraphs into one string
        body = "\n\n".join([p.inner_text() for p in paragraphs])
        browser.close()
        return title, body, url

def post_linkedin(blog_text):
    url= "https://api.linkedin.com/v2/ugcPosts" # linkedin api endpoint for creating posts
    headers={
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    } # headers for request to post, including token, content type

    post_body={
        "author": ORG_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": blog_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    request_to_post=requests.post(url, headers=headers, json=post_body)

    # print request status
    print("LinkedIn response status:", request_to_post.status_code)
    print("LinkedIn response body:", request_to_post.text)

def main():
    blog_url="https://www.hydrox.ai/blogs/hydrox-ai-graduates-from-the-google-cloud-ai-accelerator"
    title, body, url =get_blog(blog_url)
    # linkedin posts has limit of 3000 characters
    max_length = 3000
    post_text = f"{title}\n\n{body}"
    if len(post_text) > max_length:
        post_text = post_text[:max_length] + "..."+ " \nFull article: "+url

    # print to check what will be posted
    print("Posting to LinkedIn:\n", post_text)

    # post it to LinkedIn using the API
    post_linkedin(post_text)

if __name__ == "__main__":
    main()