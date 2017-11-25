from matplotlib import pyplot as plt
from matplotlib_venn import venn2
import json
from matplotlib.backends.backend_pdf import PdfPages
from pylab import *

a = open('english_articles_analysis_results_refined_ne.json','r').read()
data = json.loads(a)


keywords_in_keyphrases = []
named_entities_in_keywords = []
named_entities_in_keyphrases = []

for article in data:
    keywords = []
    keyphrases = []
    named_entities = []
    for words in article['keywords']:
        keywords.append(words[0])
    for words in article['keyphrases']:
        for k in words[0].split():
            keyphrases.append(k)
    for words in article['names_entities']:
        named_entities.append(words.lower())

    keywords_set = set(keywords)
    keyphrases_set = set(keyphrases)
    named_entities_set = set(named_entities)

    print "Article:"+article['url']
    
    keywords_in_keyphrases.append(len(keywords_set.intersection(keyphrases_set))*10)
    named_entities_in_keywords.append(len(keywords_set.intersection(named_entities_set))*10)
    named_entities_in_keyphrases.append(len(keyphrases_set.intersection(named_entities_set))*10)

count_scores_keywords_in_keyphrases = []
count_scores_named_entities_in_keywords = []
count_scores_named_entities_in_keyphrases = []
percentages = range(0,110,10)
for value in percentages:
    count_scores_keywords_in_keyphrases.append(keywords_in_keyphrases.count(value))
    count_scores_named_entities_in_keywords.append(named_entities_in_keywords.count(value))
    count_scores_named_entities_in_keyphrases.append(named_entities_in_keyphrases.count(value))


# make a square figure and axes
figure(1, figsize=(6,6))
ax = axes([0.1, 0.1, 0.8, 0.8])

# The slices will be ordered and plotted counter-clockwise.
labels = 'None', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'

pie(count_scores_keywords_in_keyphrases, labels=labels, autopct='%1.1f%%', startangle=90)

title('% of Keywords in Keyphrases - Analysis on 100 English news articles', bbox={'facecolor':'0.8', 'pad':5})

show()

# make a square figure and axes
figure(1, figsize=(6,6))
ax = axes([0.1, 0.1, 0.8, 0.8])

# The slices will be ordered and plotted counter-clockwise.
labels = 'None', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'

pie(count_scores_named_entities_in_keywords, labels=labels, autopct='%1.1f%%', startangle=90)

title('% of Named entities in Keywords - Analysis on 100 English news articles', bbox={'facecolor':'0.8', 'pad':5})

show()

# make a square figure and axes
figure(1, figsize=(6,6))
ax = axes([0.1, 0.1, 0.8, 0.8])

# The slices will be ordered and plotted counter-clockwise.
labels = 'None', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'

pie(count_scores_named_entities_in_keyphrases, labels=labels, autopct='%1.1f%%', startangle=90)

title('% of Named entities in Keyphrases - Analysis on 100 English news articles', bbox={'facecolor':'0.8', 'pad':5})

show()


    
    
