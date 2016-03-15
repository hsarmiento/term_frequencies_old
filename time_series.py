#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from nltk.tokenize import word_tokenize
import json

from nltk.corpus import stopwords
import string
from vincent import *
from vincent.legends import LegendProperties
from vincent.values import ValueRef
from vincent.properties import PropertySet
import pandas
from pre_processing import PreProcessing


db = MySQLdb.connect(host="localhost", # your host, usually localhost
	user="root", # your username
	passwd="legend", # your password
	#db="data_flood"
	db="data_earthquake_09_2015"
	) # name of the data base


if __name__ == '__main__':
	cur = db.cursor() 
	punctuation = list(string.punctuation)
	stop = stopwords.words('spanish') + punctuation + ['rt', 'via']
	# Use all the SQL you like
	
	cur.execute("select text,date_sub(created_at, INTERVAL 3 HOUR) from no_retweet;")
	dates = []

	prepro = PreProcessing()
	for row in cur.fetchall():
		terms_stop = [term for term in prepro.preprocess(row[0]) if len(term) >= 3 and term not in stop]  #ignore terms with length <= 3
		# if 'terremoto' in terms_stop:
		dates.append(row[1])

	# a list of "1" to count the hashtags
	ones = [1]*len(dates)
	# the index of the series
	idx = pandas.DatetimeIndex(dates)
	# the actual series (at series of 1s for the moment)
	date_serie = pandas.Series(ones, index=idx)	 
	# Resampling / bucketing
	per_minute = date_serie.resample('1Min', how='sum').fillna(0)
	time_chart = Line(per_minute)
	time_chart.axis_titles(x='Time', y='Freq')


	time_chart.legend(title='Tweets')
	time_chart.legends[0].properties = LegendProperties(labels=PropertySet(font_size=ValueRef(value=16)),
                                              title=PropertySet(font_size=ValueRef(value=25)))
	# print time_chart.grammar()
	time_chart.to_json('time_chart.json')



	