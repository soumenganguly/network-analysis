#Automatic keyword/keyphrase extraction using TextRank algorithm

#Article curation and Tokenization
from nltk.tokenize import sent_tokenize, PunktWordTokenizer
from nltk.corpus import stopwords
from string import punctuation
from newspaper import Article
import networkx as nx
from itertools import takewhile, tee, izip
import operator
import sys
import nltk

url = sys.argv[1]
article = Article(url)

article.download()
article.parse()

title = article.title
text = article.text

tokenizer = PunktWordTokenizer()
sentences = sent_tokenize(text)
words = []
refined_words = []
for sentence in sentences:
    word = tokenizer.tokenize(sentence)
    for i in word:
        words.append(i.lower())
        
#Removal of stopwords and punctuations
for word in words:
    if word not in stopwords.words('english') and word not in punctuation:
        refined_words.append(word)

#Stemming and lemmatization

#Tagging and extracting important keyword for graph computation(TextRank)
def textrank(wordlist):
    tagged_words = nltk.pos_tag(wordlist)
    good_tags = ['JJ','JJS','JJR','NN','NNS','NNP','NNPS']
    candidate_words = []
    for tagged_word in tagged_words:
        if tagged_word[1] in good_tags:
            candidate_words.append(tagged_word[0])

    #Create a graph
    G = nx.Graph()
    G.add_nodes_from(set(candidate_words)) #Add keywords as nodes

    #Add edges 
    def pairwise(iterator):
        a, b = tee(iterator)
        next(b, None)
        return izip(a,b)

    for w1, w2 in pairwise(candidate_words):
        if w2:
            G.add_edge(w1,w2)
    rank = nx.pagerank(G)

    word_ranks_tuple = sorted(rank.iteritems(), key=operator.itemgetter(1), reverse=True)[:50]
    word_ranks = {word_rank[0]:word_rank[1] for word_rank in word_ranks_tuple}
    keyword = set(word_ranks.keys())

    keyphrases = {}
    j = 0
    for i, word in enumerate(wordlist):
        if i < j:
            continue
        if word in keyword:
            kp_word = list(takewhile(lambda x: x in keyword, wordlist[i:i+10]))
            avg_pagerank = sum(word_ranks[w] for w in kp_word) / float(len(kp_word))
            keyphrases[' '.join(kp_word)] = avg_pagerank
            j = i + len(kp_word)
    return sorted(keyphrases.iteritems(), key=operator.itemgetter(1), reverse=True)