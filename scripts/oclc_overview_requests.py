import requests
import time
import json
from bs4 import BeautifulSoup as bs
import pandas as pd

#notes: 
#1) I created a folder called "full_data" that is in the .gitignore file so that it will not get uploaded to github. I need to save data here.
#2) I still need to put in a few periodic saves of the data and something to tell me what start it errored out on if it errors out

# this is the keyword tattoo query that works : "http://www.worldcat.org/webservices/catalog/search/worldcat/opensearch?q=srw.kw+all+%22tattoo*%22+and+srw.yr+%3E%3D+%221850%22+and+srw.dt+any+%22bks%22&count=100&wskey={oclc_key}"

#.gitignore file with oclc_api_key.json
#one row json is {"oclc_key": "add api key text here"}

with open('oclc_api_key.json') as f:
	oclc_key = json.load(f)



#these are all the fields I need to pull when parsing xml	
# author
# title
# summary #note: there isn't a summary for every book
# oclc_record_id
# oclc_link #this is in the "id" tag section
# isbn #this one will be a multiple values which I'd like to put in as a list, also not all have ISBNs

#need to replace the second value in the range tuple with the end number of the length of the kw tattoo search (9403, plus a little bit for padding in case new things added)

#changed to srw.su tattoo* to pull subject kw tattoo. This list is 2803 long last I checked. But sadly the API key expired, so I'll need to either get it renewed or scrape each of the records I have (narrow first by printed book and some other relevant things).

entries = {}

for start in range(1,2900,100): #that last 100 is a step value jumping the range by 100s
	main_query = "http://www.worldcat.org/webservices/catalog/search/worldcat/opensearch?q=srw.su+all+%22tattoo*%22+and+srw.yr+%3E%3D+%221850%22+and+srw.dt+any+%22bks%22&count=100" 
	params = {"start": start, "wskey": oclc_key["oclc_key"]}
	each_hundred_entries = requests.get(main_query, params=params)
	soup = bs(each_hundred_entries.text, "xml")
	entry_tags = soup.find_all("entry")
	for i, entry in enumerate(entry_tags):
		row = i + start -1
		entries[row] = {}
		entries[row]["oclc_recordid"] = entry.select("recordIdentifier")[0].string
		entries[row]["title"] = entry.find_all("title")[0].string
		#note, this was written to account for multiple "name" tags in the author section; it may be the case that this never happens so code could be simplified
		author_tag = entry.find_all("author")
		author_names = []
		for line in author_tag:
			name_tags = line.find_all("name")
			for name in name_tags:
				author_names.append(name.string)
		entries[row]["author_names"] = author_names
		try: 
			entries[row]["summary"] = entry.find_all("summary")[0].string
		except:
			entries[row]["summary"] = "No summary"	
		entries[row]["url"] = entry.find_all("id")[0].string
		#note: this pulls just ISBNs, not LCCNs
		isbns = []
		try:
			isbn_tags = entry.select("identifier")
			for isbn in isbn_tags:
				if "ISBN" in isbn.string:
					isbns.append(isbn.string)
				else:
					pass
		except:
			isbns.append("No ISBN")
		entries[row]["isbns"] = isbns
	time.sleep(1)

entries_df = pd.DataFrame().from_dict(entries, orient='index')

#note! change folder to final_data folder!

entries_df.to_csv('test_data/oclc_trial_bks_su_tattoo.csv', index=False, encoding="utf-8")

print("Woohoo, you have data!")
