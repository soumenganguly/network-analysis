from __future__ import division

import time
import hashlib

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from nltk.corpus.reader import WordListCorpusReader

import sys
import string
import operator
from math import log
import pickle
import random

from newspaper import Article

from collections import Counter
import requests
from lxml import html
#import json
#import MySQLdb

from sklearn.datasets import load_files
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB


# Intialize the database
'''
db = MySQLdb.connect(host='localhost',
                     user='webrowse',
                     passwd='Webrowse@123',
                     db='article')
cur = db.cursor()
'''

dataset = load_files('/home/soumen/projects/scikit-learn/doc/tutorial/text_analytics/data/languages/paragraphs')  # Read an article

file_id_argv = open(sys.argv[1])
file_id = file_id_argv.read()
file_list = file_id.split('\n')
file_list.pop(-1)

italian_stopwords = WordListCorpusReader('.', ['stop-words-it-en.txt'])


def language_detection(text):
    """Description here"""
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(dataset.data)
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

    X_test_counts = count_vect.transform(text)
    X_test_tfidf = tfidf_transformer.transform(X_test_counts)

    clf = MultinomialNB().fit(X_train_tfidf, dataset.target)

    predicted = clf.predict(X_test_tfidf)
    return dataset.target_names[predicted[0]]


def tokenize(text, language):
    """Description goes here"""
    tokens = []
    filtered = []
    lower = text.lower()
    lower_str = lower.encode('utf-8')
    no_punctuation = lower_str.translate(None, string.punctuation)
    tokens = word_tokenize(no_punctuation)
    if language == 'fr':
        filtered = [w for w in tokens if w not in stopwords.words('french')]
    elif language == 'de':
        filtered = [w for w in tokens if w not in stopwords.words('german')]
    elif language == 'it':
        filtered = [w for w in tokens if w not in italian_stopwords.words()]
    elif language == 'es':
        filtered = [w for w in tokens if w not in stopwords.words('spanish')]
    elif language == 'pt':
        filtered = [w for w in tokens if w not in stopwords.words('portuguese')]
    else:
        filtered = [w for w in tokens if w not in stopwords.words('english')]
    return filtered


def calculate_tf(word_list):
    """Description goes here"""
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
    # print the frequency of bigram tokens
    bigram_items = bcf.ngram_fd.viewitems()
    bi_dict = {}
    for i in bigram_items:
        bi_dict[i[0]] = i[1]
    sorted_bigram = sorted(bi_dict.items(), key=operator.itemgetter(1))
    sorted_bigram.reverse()
    # for j in sorted_bigram[0:10]:
    #    print j
    return sorted_bigram


def calculate_trigrams(tokens):
    tcf = TrigramCollocationFinder.from_words(tokens)
    trigram_tokens = tcf.nbest(TrigramAssocMeasures.likelihood_ratio, 10)
    return trigram_tokens


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


if __name__ == "__main__":
    time_start = time.time()
    count = 0
    for links in file_list:
        print links
        try:
            filtered = []
            #link = links.split('\t')[1]
            a = Article(links)
            a.download()
            a.parse()
            title = a.title
            text = a.text
            count += 1
            print "[%d]Reading link-->"%(count), links
        except:
            continue
        link_text = title + text
        lang = language_detection([link_text])
        tokens = tokenize(link_text, lang)
        top_n = calculate_tf(tokens)  # Calculate the top unigrams.
        top_n_bigrams = calculate_bigrams(tokens)  # Calculate top
        top_n_trigrams = calculate_trigrams(tokens)  # Calculate top trigrams.
        top_10_words = calculate_top_n_words(top_n, top_n_bigrams)
        for i in top_10_words:
            print i[0]
        for j in top_n:
            print j[0]
        #top_10_words_db = json.dumps(top_10_words)
        #link_db = json.dumps(link)
        #user_id_db = hashlib.md5(links.split('\t')[0]).hexdigest()
        #title_db = tokenize(title, lang)
    time_end = time.time() - time_start
    print time_end
