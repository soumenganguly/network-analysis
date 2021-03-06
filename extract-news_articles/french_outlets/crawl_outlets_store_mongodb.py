import newspaper as np
from newspaper import news_pool
from pymongo import MongoClient
import sys
from datetime import datetime

client = MongoClient()

db = client['news_crawls']

outlet_list_file = open(sys.argv[1],'r').read()
outlet_list = outlet_list_file.split('\n')
outlet_list.pop(-1)

build_objects = []

for outlet in outlet_list:
    build_objects.append(np.build('http://'+outlet, memoize_articles=False))

news_pool.set(build_objects, threads_per_source=2)
news_pool.join()


for outlet in build_objects:
    for article in outlet.articles:
        count = db.french_outlets.find({"url":article.url})
        if count.count() != 0:
            continue
        else:
            article.parse()
            print article.url
            db.french_outlets.insert_one({"title":article.title, "text":article.text, "url":article.url, "publish_date":article.publish_date, "newspaper_name":article.source_url.split('.')[1], "timestamp":datetime.utcnow()()})


