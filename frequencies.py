#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from nltk.tokenize import word_tokenize
import operator 
import json
from collections import Counter
import re
from nltk.corpus import stopwords
import string
from nltk import bigrams
from nltk import trigrams
from nltk.util import ngrams
from collections import defaultdict
import vincent

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
 
regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]
    
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)
 
def tokenize(s):
    return tokens_re.findall(s)
 
def preprocess(s, lowercase=True):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens

db = MySQLdb.connect(host="localhost", # your host, usually localhost
	user="root", # your username
	passwd="legend", # your password
	#db="data_flood"
	db="data_earthquake_09_2015"
	) # name of the data base


if __name__ == '__main__':
	cur = db.cursor() 
	count_all = Counter()
	punctuation = list(string.punctuation)
	stop = stopwords.words('spanish') + punctuation + ['rt', 'via']
	# Use all the SQL you like
	
	cur.execute("select text from no_retweet;")
	#cur.execute("SELECT text FROM tweet where text like '%diego de almagro%' or text like '%chañaral%' or text like '%copiapo%';")

	# print all the first cell of all the rows

	com = defaultdict(lambda: defaultdict(int))


	for row in cur.fetchall():
		terms_stop = [term for term in preprocess(row[0]) if len(term) >= 3 and term not in stop]
		for i in range(len(terms_stop)-1):
			for j in range(i+1, len(terms_stop)):
				w1,w2 = sorted([terms_stop[i],terms_stop[j]])
				if w1 != w2:
					com[w1][w2] +=1

	com_max = []
	# For each term, look for the most common co-occurrent terms
	for t1 in com:
	    t1_max_terms = max(com[t1].items(), key=operator.itemgetter(1))[:5]
	    for t2 in t1_max_terms:
	        com_max.append(((t1, t2), com[t1][t2]))
	# Get the most frequent co-occurrences
	terms_max = sorted(com_max, key=operator.itemgetter(1), reverse=True)
	# print(terms_max[:5])
	# 	# terms_all = [term for term in preprocess(row[0])]
	# 	#terms_trigram = trigrams(terms_stop)
		# terms_bigram = bigrams(terms_stop)
		# count_all.update(terms_bigram)
	# 	# count_all.update(terms_stop)
	# 	# count_all.update(terms_trigram)

	terms_max = terms_max[:10]
	labels, freq = zip(*terms_max)
	data = {'data': freq, 'x': labels}
	bar = vincent.Bar(data, iter_idx='x')
	bar.to_json('term_freq.json', html_out=True, html_path='chart.html')


	