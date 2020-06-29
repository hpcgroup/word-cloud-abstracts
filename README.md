# word-cloud-abstracts

Takes a list of links to IEEE, ACM DL, and Springer pages, scrapes them for titles and abstracts, and creates a wordcloud.

The data is cached in an intermediate JSON file so as not to unnecessarily scrape the websites too much.

__Usage:__

```sh
# reads `links.txt` and creates a wordcloud from the abstracts
python main.py --word-cloud

# reads `links.txt` and abstracts already in `papers_db.json`
# and creates a wordcloud
python main.py -f links.txt --database papers_db.json --word-cloud
```
