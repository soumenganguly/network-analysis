'''
This script extracts, from a text file with url\'s of Articles, top-10 keywords and keyphrases along with all the Named entities present in an article. 
It was written for the purpose of analyzing which extraction technique(keywords or keyphrases) performs better and imparts more insights into an articles\' contents.
The analysis is based on English language articles and the results can be inferred to articles in different languages for which there is no state-of-the-art extraction framework available.

'''


from pymongo import MongoClient
import pickle
from nltk.tokenize import word_tokenize, sent_tokenize
from string import punctuation
import sys
import newspaper as np
import signal
import operator
import json
from collections import Counter
from nltk.tag.stanford import NERTagger

from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from nltk.corpus.reader import WordListCorpusReader

st = NERTagger('/home/soumen/Downloads/stanford-ner-2017-06-09/classifiers/english.all.3class.distsim.crf.ser.gz','/home/soumen/Downloads/stanford-ner-2017-06-09/stanford-ner.jar', encoding='utf8')

tags = ['ORGANIZATION', 'PERSON', 'LOCATION', 'MISC']

#client = MongoClient()

#db = client['english_articles_analysis']



class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

signal.signal(signal.SIGALRM, timeout_handler)

# Input file with URLS
input_file = open(sys.argv[1], 'rb')
input_file_read = input_file.read()
input_file_data = input_file_read.split('\n')
input_file_data.pop(-1)

output_file = open("english_articles_analysis_results_refined_ne.json","wb")



# File which contains URLS which were not scraped
error_url_files = open('error_url_files.txt','wb')

# Tokenization
def tokenize(t):
    sentences = sent_tokenize(t)
    words = []
    refined_words = []
    for sentence in sentences:
        word = word_tokenize(sentence)
        for i in word:
            words.append(i.lower())
        
    #Removal of stopwords and punctuations
    #stopwords = open('stop-words-it-en.txt','r').read().split('\r\n')
    for word in words:
        if word not in stopwords.words('english') and word not in punctuation:
            refined_words.append(word)
    return refined_words


''' 
Extract the top-10 KEYWORDS(Uni-grams) from an article.

'''
    
def extract_top_10_keywords_in_an_article(title, text):
	top_10_dict = {}
    	title_words = tokenize(title)
    	all_words = tokenize(title+' '+text)
    	for word in all_words:
        	if word in title_words:
            		score = 1
        	else:
            		score = 0.5
        	if word in top_10_dict:
            		top_10_dict[word] = top_10_dict[word] + score
        	else:
            		top_10_dict[word] = score
	temp = sorted(top_10_dict.items(), key=operator.itemgetter(1), reverse=True)
	return temp


'''
Extract the top-10 KEYPHRASES from an article.

'''

def calculate_tf(word_list):
    tf_score = {}
    top_n_words = []
    count = Counter(word_list)
    for word in word_list:
        tf_score[word] = count[word]
    sorted_tf = sorted(tf_score.items(), key=operator.itemgetter(1))
    sorted_tf.reverse()
    for word in sorted_tf[0:10]:
        top_n_words.append(word)
        # print word[0], word[1]
    return top_n_words


def calculate_bigrams(tokens):
    bcf = BigramCollocationFinder.from_words(tokens)
    bigram_tokens = bcf.nbest(BigramAssocMeasures.raw_freq, 10)
    bigram_items = bcf.ngram_fd.viewitems()
    bi_dict = {}
    for i in bigram_items:
        bi_dict[i[0]] = i[1]
    sorted_bigram = sorted(bi_dict.items(), key=operator.itemgetter(1))
    sorted_bigram.reverse()
    return sorted_bigram

def calculate_top_n_words(unigram_tokens, bigram_tokens):
    bigram_items = {}
    for j in bigram_tokens[0:10]:
        bigram_items[j[0][0] + ' ' + j[0][1]] = j[1]

    for i in unigram_tokens:
        count = 0
        for j in bigram_items.keys():
            if i[0] in j:
                break
            else:
                count += 1
        if count >= len(bigram_items):
            bigram_items[i[0]] = i[1]
    sorted_list = sorted(bigram_items.items(), key=operator.itemgetter(1))
    sorted_list.reverse()
    return sorted_list[0:10]

'''
Extract all the NAMED ENTITIES from an article.
'''

def extract_named_entities(text):
    named_entities = []
    sents = sent_tokenize(text)
    for sentences in sents:
        for entity in st.tag(sentences.split()):
            if entity[1] in tags and entity[0] not in named_entities:
                named_entities.append(entity[0])
            else:
                pass
    return named_entities


if __name__ == "__main__":
    count = 0
    article_dict = []
    for url in input_file_data:
	# Download and parse the article
	article = np.Article(url)
	article.download()
	article.parse()
        print "Reading url: %s"%(article.url)


	title = article.title
	text = article.text
	
        list_of_top_10_words = []
	list_of_top_10_keyphrases = []
	list_of_named_entities = []

	tokens = tokenize(title+' '+text)

	try:
	    # Collect top-10 keywords
	    print "Extracting top-10 keywords.."
            sorted_dict_of_top_10_terms = extract_top_10_keywords_in_an_article(title, text)
	    for item in sorted_dict_of_top_10_terms[:10]:
		list_of_top_10_words.append(item)
	    
	    # Collect named entities
	    print "Extracting Named entities.."
	    list_of_named_entities = extract_named_entities(text+' '+title)

	    # Collect top-10 keyphrases
	    print "Extracting top-10 keyphrases.."
	    top_n_words = calculate_tf(tokens)
	    top_n_bigrams = calculate_bigrams(tokens)
	    top_n_keyphrases = calculate_top_n_words(top_n_words, top_n_bigrams)
	
	    print "Storing in the Database.."
	    #db.articles.insert_one({"url":article.url,"keywords":list_of_top_10_words,"keyphrases":top_n_keyphrases,"named entities":list_of_named_entities})
            article_dict.append({"url":article.url,"keywords":list_of_top_10_words,"keyphrases":top_n_keyphrases,"names_entities":list_of_named_entities})
		
	except TimeoutException:
	    error_url_files.write(url+'\n')
    	count+=1
   	print "%d of %d"%(count,len(input_file_data))
    json.dump(article_dict, output_file)
    input_file.close()
    output_file.close()
    error_url_files.close()

