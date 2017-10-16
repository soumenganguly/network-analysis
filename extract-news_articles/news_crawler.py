import newspaper as np
from newspaper import news_pool
from datetime import datetime
import hashlib
import MySQLdb


starttime = datetime.now()


db = MySQLdb.connect(host="localhost", user="root", passwd="madrugada", db="news_crawls", charset='utf8')
cur = db.cursor()

french_news_outlet_list = open("french_outlets_temp.txt","r").read()
french_outlets = french_news_outlet_list.split('\n')
french_outlets.pop(-1)

# Provide individual news outlets from the shell script
build_objects = []

for outlet in french_outlets:
	build_objects.append(np.build('http://'+outlet, memoize_articles=False))


news_pool.set(build_objects, threads_per_source=2)
news_pool.join()


for outlet in build_objects:
    for article in outlet.articles:
        #Check for duplicates
        hash_code = hashlib.md5(article.url.encode())
        hash_digest = hash_code.hexdigest()
        cur.execute('select hashcode from french_news_outlets;')
        hash_set = cur.fetchall()
        if (hash_digest,) in hash_set:
            continue
        else:
            article.parse()
            hashcode_value = hash_digest
            url_value = article.url.encode('utf-8')
            text_value = article.text.encode('utf-8')
            title_value = article.title.encode('utf-8')
            #image_url_value = article.image
            newspaper_name_value = url_value.split('.')[1].encode('utf-8')
            publish_date_value = article.publish_date
            publish_time_value = datetime.now().time()
            #print hashcode_value, url_value, text_value, title_value, newspaper_name_value, publish_date_value, publish_time_value
            cur.execute('insert into french_news_outlets(hashcode, url, text, title, newspaper_name, publish_date, publish_time) values(%s, %s, %s, %s, %s, %s, %s)',(hashcode_value, url_value, text_value, title_value, newspaper_name_value, publish_date_value, publish_time_value))
            db.commit()
db.close()

print datetime.now() - starttime


