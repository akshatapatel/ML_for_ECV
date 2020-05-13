import re
from http.client import InvalidURL
from typing import Dict
from urllib.error import HTTPError, URLError

import pandas as pd
from langdetect.lang_detect_exception import LangDetectException
from newsplease import NewsPlease

INVALID_URL_PATTERNS = [
    "necsi-edu.slack.com",
    "zoom.us",
    "docs.google.com"
]


def main():

    msg_df = pd.read_csv("ecv_analytics_scanning_data.csv")
    web_texts = []

    for row_idx, row in msg_df.iterrows():

        text = row["text"]
        if pd.isna(text):
            continue

        links = find_links(text)

        # clean the text by replacing the links by placeholders
        cleaned_text = text
        for link in links:
            cleaned_text = cleaned_text.replace(link, "[LINK]")
        row["text"] = cleaned_text
        msg_df.iloc[row_idx] = row

        # retrieve web texts
        for url in links.values():
            if any(p in url for p in INVALID_URL_PATTERNS):
                continue

            print(f"Scraping URL {url}")
            try:
                article = NewsPlease.from_url(url)
                article_data = {
                    "client_msg_id": row["client_msg_id"],
                    "user": row["user"],
                    "url": url,
                    "title": article.title,
                    "maintext": article.maintext,
                    "authors": article.authors,
                    "date_publish": article.date_publish
                }
                web_texts.append(article_data)
            except HTTPError:
                print("HTTPError, skipping...")
            except InvalidURL:
                print("Invalid URL, skipping...")
            except URLError as e:
                print(f"URL error, skipping: {e}")
            except Exception:
                print("Unknown exception, skipping...")

    # save cleaned df
    msg_df.to_csv("ecv_analytics_scanning_data.csv.cleaned")

    # save webtexts
    web_texts_df = pd.DataFrame(web_texts)
    web_texts_df.to_csv("web_text_data.csv")


def find_links(text: str) -> Dict[str, str]:

    # map urls
    links = {}

    bracketed_expressions = re.findall(r"<(.*)>", text)
    for exp in bracketed_expressions:

        # clean any extra information
        exp_cleaned = exp.split("|")[0]

        # check if it's a URL
        if exp_cleaned.startswith("http://") or exp_cleaned.startswith("https://"):
            links["<" + exp + ">"] = exp_cleaned

    return links


if __name__ == '__main__':
    main()
