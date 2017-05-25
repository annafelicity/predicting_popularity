#note this pulls everything besides the library count which can only be pulled using selenium due to that being rendered in dynamic html
#I also had the selenium scraper pull the short title field so I'd have a sense of which books were which so that is duplicate here

from lxml import html
import requests
import time
import json
from bs4 import BeautifulSoup as bs
import pandas as pd

def save_data(data):
	df = pd.DataFrame().from_dict(data, orient='index')
#note: change to final file name/folder in final version
	return df.to_csv('test_data/scraper_trial_from_7140.csv', index=False, encoding="utf-8")

url_df = pd.read_csv("test_data/oclc_trial_bks_9450.csv", usecols=["url"])

#remove the [0:5] for full webscraper
oclc_urls = url_df["url"].tolist()[7140:]

url_page_data = {}
i = 0
x = 0
for sublist in oclc_urls:
	sublist = oclc_urls[x:x+10]
	for url in sublist:
		url_page_data[i] = {}
		try:
			url_request = requests.get(url)
			url_soup = bs(url_request.text, "html5lib")
			url_page_data[i]["url"] = url
			bibdata = url_soup.find("div", id="bibdata")
			url_page_data[i]["title"] = bibdata.find("h1", "title").string
			url_page_data[i]["publisher"] = bibdata.find(id="bib-publisher-cell").string
			url_page_data[i]["book_type"] = bibdata.find("span", "itemType").string
			genre_chunk = bibdata.find("span", id="editionFormatType")
			url_page_data[i]["genre_chunk"] = genre_chunk.get_text()
			url_page_data[i]["isbns_space_delim"] = url_soup.find("div", id="bibtip_isxn").string
		except:
			url_page_data[i]["url"] = url
			print("Erroring")
		i += 1
		time.sleep(1)
	save_data(url_page_data)
	print("SAVING")
	x += 10
print("All done!")


