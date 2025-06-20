import os
from dotenv import load_dotenv
from browser_use import BrowserUse
from openai import OpenAI


load_dotenv() #load tokens from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#initialize openai
client=OpenAI()


def get_blog(url):
        browser = BrowserUse(browser="chromium", headless=False)
        page = browser.goto(url)
        page.wait_for_load_state('networkidle') # wait till finishing loading
        title=page.title()
        paragraphs = page.query_selector_all("p")
        # Join all paragraphs into one string
        body = "\n\n".join([p.inner_text() for p in paragraphs])
        browser.close()
        return title, body

def generate_linkedin(article):
    #use openAI to generate linkedin post
    prompt=f""" Read this article and translate and rewrite it into a LinkedIn-style post.
    Here is the article:
    {article}
    """
    response=client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"user", "content":prompt}
        ]
    )
    return response.choices[0].message.content

def post_generated_article(post):
    browser=BrowserUse(browser="chromium", headless=False)
    page=browser.goto("https://www.linkedin.com/login")
    page.goto("https://www.linkedin.com/feed/") # go to linkedin feed
    page.get_by_role("button", name="Start a post").click() # find the start a post button
    page.wait_for_selector("div[role='textbox']") #wait for textbox to show up
    page.locator("div[role='textbox']").fill(post) # fill with the generated post
    page.locator("button.share-actions__primary-action").click() # click post button
    browser.close()


def main():
    blog_url="https://www.hydrox.ai/blogs/hydrox-ai-graduates-from-the-google-cloud-ai-accelerator"
    title, body =get_blog(blog_url)
    article=f"{title}\n\n{body}"
    post=generate_linkedin(article)
    # print to check what will be posted
    print("Posting to LinkedIn:\n", post)

    post_generated_article(post)

if __name__ == "__main__":
    main()