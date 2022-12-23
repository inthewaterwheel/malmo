# Malmo 

Malmo is a tool to help you search through the pages you've seen.

`preproc` scrapes all the webpages you've visited recently, and builds embedding indices for both webpage titles & fulltext.

`query` then takes a query and search for matches in webpages you've visited recently.

# Installation

`pip install -r requirements.txt`

`python3 preproc.py` (takes ~10-20 minutes)

`python3 query.py`

I've only tested out the Chrome History sqlite location on macOS - if you run into issues, you might need to copy over the Chrome History doc.

# Limitations & next steps

This performs so-so, the semantic search is sometimes more useful than Chrome's default history search.

I'm listing down some next steps here, if you have any thoughts about them, or in general, feel free to reach out to me at @inthewaterwheel on Twitter.

## Limitations

- It currently takes quite a while to build the index, and only embeds only the last ~5k entries (~1 month for me).
    -    Building this on the fly as a background program could be cool
- Full-text search doesn't work great
    - Some pages can't be scraped well post-hoc
    - I only use the first 5k characters per page - it'd be much nicer to extract the most salient parts
- Unhelpful duplication in results
- CLI is meh

## Further directions


### Improvements:

- Twitter & extraction from dynamic sites
    - Tweets are extracted fine if you actually click through on a tweet, but aren't well extracted otherwise.
    - Continually extracting content ala Rewind.ai would help

- Extracting only the salient info from a webpage rather than all of it would help, since a lot of a webpage is unrelated garbage that throws results off.

- Some deduplication would help a lot

### Potential Features:

- Clustering
    - The strongest clustering case is to automatically build a Roam/Obsidian knowledge graph from your browsing history
    - Interesting to figure out what you can infer from temporal closeness to help w/ clustering

- LLMs for synthesis
    - Inspired by [Neeva AI](https://twitter.com/RamaswmySridhar/status/1602334539216396288)/[Perplexity.ai](https://www.perplexity.ai/), it would be nice to return a synthesized answer with citations
    - Pick the top `k` search results, feed their text to an LLM, along with the question and a request to provide an answer.

- LLMs as agents
    - Inspired by [Ought](https://primer.ought.org/chapters/action-selection), you could plausibly ask the LLM to: a) pick better queries for the embedding search, b) choose which top m of n results to "expand" from just URL + title to short text

- Alternate embedding approaches
    - Would something [LLM-based](https://beta.openai.com/docs/guides/embeddings) for embedding do better?