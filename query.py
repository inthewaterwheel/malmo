import json
from sentence_transformers import SentenceTransformer, util
import torch
import time
import datetime
from termcolor import colored

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

t = time.time()
# Read history.json
with open("history.json", "r") as f:
    data = json.load(f)
print(colored("Loaded data in {:.2f} seconds".format(time.time() - t), "grey"))

t = time.time()
model = SentenceTransformer('msmarco-distilbert-base-v4')
print(colored("Loaded model in {:.2f} seconds".format(time.time() - t), "grey"))


t = time.time()
#Extract embeddings from json
embeds = [d["embedding"] for d in data]
# Convert to tensor
embeds = torch.tensor(embeds)

full_text_embeds = [d["fulltext_embedding"] for d in data]
full_text_embeds = torch.tensor(full_text_embeds)
print(colored("Corpus embeddings loaded in {:.2f} seconds".format(time.time() - t), "grey"))


while True:
    # Query the model
    query = input(">")

    # Encode the query
    t = time.time()
    query_embedding = model.encode(query, convert_to_tensor=True)
    print(colored("Query embedding took {:.2f} seconds".format(time.time() - t), "grey"))

    # Compute cosine-similarits
    t = time.time()
    cos_scores = util.pytorch_cos_sim(query_embedding, embeds)[0]
    cos_scores_full_text = util.pytorch_cos_sim(query_embedding, full_text_embeds)[0]

    # Sort the results
    top_results = torch.topk(cos_scores, k=5)
    top_results_full_text = torch.topk(cos_scores_full_text, k=5)
    print(colored("Search took {:.2f} seconds".format(time.time() - t), "grey"))

    print("Results (title):")
    for score, idx in zip(top_results[0], top_results[1]):
        print(data[idx]["title"], "(Score: %.4f)" % (score))
        print(convertTimeStamp(data[idx]["last_visit_time"]))
        print(data[idx]["url"])

        print("-------------------------")

    print("Results (full-text):")
    for score, idx in zip(top_results_full_text[0], top_results_full_text[1]):
        print(data[idx]["title"], "(Score: %.4f)" % (score))
        print(convertTimeStamp(data[idx]["last_visit_time"]))
        print(data[idx]["url"])

        print("-------------------------")