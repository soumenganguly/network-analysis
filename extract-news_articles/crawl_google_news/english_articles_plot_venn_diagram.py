'''
This script plots the venn diagrams, which shows the intersection between 3 entities gathered for each article - Keywords, Keyphrases and Named entities. 
'''

from matplotlib import pyplot as plt
from matplotlib_venn import venn2
import json

a = open('english_articles_analysis_results_refined_ne.json','r').read()
data = json.loads(a)

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
    plt.figure()
    c=venn2([keywords_set,keyphrases_set], set_labels=['Keywords','Keyphrases'])
    plt.show()
    
    plt.figure()
    d=venn2([keywords_set,named_entities_set], set_labels=['Keywords','Named Entities'])
    plt.show()
    
    plt.figure()
    e=venn2([keyphrases_set,named_entities_set], set_labels=['Keyphrases','Named Entities'])
    plt.show()
