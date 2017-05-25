from lxml import html
import time
from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver

path_to_chromedriver = '/Users/annafriedman/Desktop/chromedriver' # change path as needed
driver = webdriver.Chrome(executable_path = path_to_chromedriver)

#I could make this even more general by putting in a keyword argument for the file name rather than hard-coding the file name (and having to change it for each batch iteration)
def save_data(data):
	df = pd.DataFrame().from_dict(data, orient='index')
	# return df.to_csv('test_data/url_batch_9000_to_9450.csv', index=False, encoding="utf-8")
	#above was the original, adding errored rows
	return df.to_csv("test_data/libcount_errored_rows_fixed.csv", index=False, encoding="utf-8")

#changed this from the 9450 df
url_df = pd.read_csv("test_data/errored_rows.csv", usecols=["url"])

#change the column range to pull in batches
oclc_urls = url_df["url"].tolist()

url_page_data = {}
i = 0
for url in oclc_urls:
	driver.get(url)
	url_page_data[i] = {}                 
	try:
		url_request = driver.page_source
		url_soup = bs(url_request, "lxml")
		url_page_data[i]["url"] = url
		url_page_data[i]["short_title"] = url_soup.find("div", id="bibtip_shorttitle").string
		url_page_data[i]["library_count"] = url_soup.find("td", "libsdisplay").get_text()
	except:
		url_page_data[i]["url"] = url
		url_page_data[i]["short_title"] = "Error"
		url_page_data[i]["library_count"] = "Error"
		print("Erroring")
	i += 1
	for x in range(100,len(oclc_urls),100):
		if i == x:
			save_data(url_page_data)
			print("SAVING %s" % x)
			time.sleep(1)
		else:
			time.sleep(1)
save_data(url_page_data)
print("All done!")
driver.close()


