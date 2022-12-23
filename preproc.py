import sqlite3
import os
import json
import requests
from bs4 import BeautifulSoup
# use multiple processes to speed up the scraping
from multiprocessing import Pool
import datetime
from sentence_transformers import SentenceTransformer, util
import time
# check OS
import platform

GET_FULL_TEXT = True
MAX_ENTRIES = 5000

def convertTimeStamp(timestamp):
    # Google timestamp, in format of microseconds since Jan 1, 1601
    # Convert to seconds since Jan 1, 1970, then to a string

    # Convert to seconds
    timestamp = timestamp / 1000000
    # Subtract the difference between 1601 and 1970
    timestamp = timestamp - 11644473600

    # Convert to a datetime object
    dt = datetime.datetime.fromtimestamp(timestamp)

    # Convert to a human readable string
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def getCleanText(soup):
    # Collect and concatenate the header tags 
    headers = ""
    for h in soup.find_all(["h1"]):
        headers += h.text + " "

    for h in soup.find_all(["h2"]):
        headers += h.text + " "

    for h in soup.find_all(["h3"]):
        headers += h.text + " "

    # Concatenate all other text
    text = headers + soup.get_text()

    # Return first 5000 characters
    return text[:5000]

def addPageTextToData(data):
    try:
        url = data["url"]
        print("Getting text for", url)
        print("Last accessed at", convertTimeStamp(data["last_visit_time"]))
        # Get the page
        r = requests.get(url, timeout=5)
        # Convert to soup
        soup = BeautifulSoup(r.text, "html.parser")
        # Get the text
        text = getCleanText(soup)
        return dict(data, text=text)
    except:
        return dict(data, text="")

def main():
    print("Extracting history from Chrome")
    # Default database is the chrome history database for macOS
    if platform.system() == "Darwin":
        DB_URL = "~/Library/Application Support/Google/Chrome/Default/History"
    elif platform.system() == "Windows":
        DB_URL = "~/AppData/Local/Google/Chrome/User Data/Default/History"
    else:
        DB_URL = "~/.config/google-chrome/Default"
        
    # Expand user
    DB_URL = os.path.expanduser(DB_URL)

    # Copy the database to the current directory
    os.system(f"cp \"{DB_URL}\" .")

    # Connect to the database
    conn = sqlite3.connect("History")

    # Create a cursor
    c = conn.cursor()

    # Goal: Read all the URLs, titles, and dates from the history database, by most recent
    # SQL query
    res = c.execute("SELECT urls.url, urls.title, urls.last_visit_time FROM urls ORDER BY urls.last_visit_time DESC")

    # Dump into a json
    data = []
    for row in res:
        data.append({
            "url": row[0],
            "title": row[1],
            "last_visit_time": row[2]
        })

    if len(data) > MAX_ENTRIES:
        print("Indexing most recent 5000 entries, out of", len(data), "entries within the last 90 days")
    data = data[:MAX_ENTRIES]

    print("Loading Model")
    model = SentenceTransformer('msmarco-distilbert-base-v4')

    # Embed the titles + urls, in format "URL: <url> \n Title: <title>"
    print("Embedding....")
    t = time.time()
    texts = [f"URL: {d['url']} \n Title: {d['title']}" for d in data]
    embeddings = model.encode(texts, convert_to_tensor=True)
    for i in range(len(texts)):
        data[i]["embedding"] = embeddings[i].tolist()
    # Print with 2 decimal places
    print("Embedding took {:.2f} seconds".format(time.time() - t))

    if GET_FULL_TEXT:
        t = time.time()
        with Pool(8) as p:
            # Get the text for each page
            data =  p.map(addPageTextToData, data)
        print("Getting full text took {:.2f} seconds".format(time.time() - t))

        # Embed the full text
        texts = [d["text"] for d in data]
        embeddings = model.encode(texts, convert_to_tensor=True)

        for i in range(len(texts)):
            data[i]["fulltext_embedding"] = embeddings[i].tolist()
        print("Fulltext embedding took {:.2f} seconds".format(time.time() - t))

    # Write to a file
    with open("history.json", "w") as f:
        f.write(json.dumps(data))

if __name__ == '__main__':
    main()