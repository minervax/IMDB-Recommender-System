import re
import requests
import sys
from bs4 import BeautifulSoup
import time
import operator
import json
import nltk
from nltk.collocations import *
from nltk import word_tokenize
from nltk import pos_tag
from nltk import wordpunct_tokenize
from nltk.book import *
from nltk.stem import *
import pickle
import json
from collections import Counter
from nltk.corpus import wordnet as wn



## Similar words extraction

conceptSim = requests.get('http://swoogle.umbc.edu/SimService/GetSimilarity?operation=top_sim&word='+sys.argv[1]+'&pos=NN&N=100&sim_type=concept&corpus=webbase&query=Get+Top-N+Most+Similar+Words'+sys.argv[1])
relationSim = requests.get('http://swoogle.umbc.edu/SimService/GetSimilarity?operation=top_sim&word='+sys.argv[1]+'&pos=NN&N=100&sim_type=relation&corpus=webbase&query=Get+Top-N+Most+Similar+Words'+sys.argv[1])
related_words={}

conceptSoup = BeautifulSoup(conceptSim.text)
conceptTextArea = conceptSoup.findAll("textarea")
conceptText = conceptTextArea[0].contents[0]

relationSoup = BeautifulSoup(relationSim.text)
relationTextArea = relationSoup.findAll("textarea")
relationText = relationTextArea[0].contents[0]

totalText = relationText + conceptText

print totalText

show_repeats = {}


lines = totalText.split(",")
for line in lines:
	line = line.strip()
	parts = line.split("_")
	if(len(parts) >= 2):
		item_name = parts[0]
		score = float(re.search('(\d+\.\d+)',parts[1]).group())
		
		if item_name.strip() in related_words.keys():
			pass
		else:
			related_words[item_name.strip()] = score

for key in related_words.keys():
	if(related_words[key] > 0.3):
		print key+" : "+str(related_words[key])


## Extracting from IMDB 

i=0

while i<len(related_words.keys()):
	if(related_words[related_words.keys()[i]] <= 0.3):
		i = i+1
		continue

	try:
		imdb_data = requests.get('http://www.imdb.com/search/keyword?keywords='+related_words.keys()[i]+'&sort=moviemeter,asc&mode=advanced&page=1&title_type=tvSeries&ref_=kw_ref_typ')
		html_content = imdb_data.text

		soup = BeautifulSoup(html_content)
		spans = soup.findAll("span", { "class" : "lister-item-index" })

		if(len(spans)>0):
			print "Scraped IMDB For "+related_words.keys()[i]+"...\n"
			for span in spans:
				show_name = span.parent.findNext("a").contents[0]
				if(show_name in show_repeats):
					show_repeats[show_name] = show_repeats[show_name]+1
				else:
					show_repeats[show_name] = 1

				print show_name

			print "--------------\n"
		i = i+1
	except Exception as e:
		time.sleep(2)
		print "Error fetching page"
		print e

# sorting tvlist by repeats and writing over 3 copies to a file

f = open('retained'+sys.argv[1]+'tvlist.txt', 'w+')

sorted_repeats = sorted(show_repeats.items(), key=operator.itemgetter(1))
sorted_repeats.reverse()
print "\nRepeat Data"
for item in sorted_repeats:
	if item[1] > 2:
		print item[0]+" : "+str(item[1])
		f.write(item[0]+",")

f.close()
