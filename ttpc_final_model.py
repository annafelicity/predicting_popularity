import pandas as pd
import re
import pickle
from textblob import TextBlob
from textstat.textstat import textstat
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelBinarizer

df = pd.read_csv("/Users/annafriedman/GA/GACapstoneProject/full_data/final_ttpc_data_3831rows.csv", usecols=[ "extracted_libcount", "age_in_2017", "proper_title"])

#add sentiment analysis
def text_blob_sentiment_polarity(value):
    blob = TextBlob(value)
    return blob.sentiment.polarity
def text_blob_sentiment_subjectivity(value):
    blob = TextBlob(value)
    return blob.sentiment.subjectivity

df["sentiment_polarity"] = df["proper_title"].apply(text_blob_sentiment_polarity)
df["sentiment_subjectivity"] = df["proper_title"].apply(text_blob_sentiment_subjectivity)

#add reading level
def reading_level_comp(string):
    try:
        level = textstat.text_standard(string)
        return level
    except:
        return "Unclear"

df["reading_level"] = df["proper_title"].apply(reading_level_comp)

lb_rl = pickle.load(open('lb_for_rl.pkl', 'rb'))
#just transform???
reading_level_lb = lb_rl.fit_transform(df["reading_level"]) 

reading_level_dummies = pd.DataFrame(reading_level_lb)

#add number of words column
df["number_of_words"] = df["proper_title"].apply(lambda x: len(x.split()))

#add title length
df["title_length"] = df["proper_title"].apply(lambda x: len(x))

#pull in pickled lda model
lda_8 = pickle.load(open('ttpc_lda.pkl', 'rb'))
cv_for_lda = pickle.load(open('cv_for_lda.pkl', 'rb'))
#just transform???
words = cv_for_lda.fit_transform(df["proper_title"])

#version with pickles
transformed_data_8= lda_8.transform(words)
transformed_data_8 = pd.DataFrame(transformed_data_8, columns=['Topic %s' % x for x in range(8)])

def top_topic_number_extractor(dataframe):
    top_topic_list = []
    for i in dataframe.index:
        ordered_row = dataframe.iloc[i,:].sort_values(ascending=False)
        top_topic_name = ordered_row.index[0]
        count_pattern = re.compile("\d+")
        top_topic_number = count_pattern.search(top_topic_name).group()
        top_topic_list.append(int(top_topic_number))
    return top_topic_list

df["top_topic_number_lda8"] = top_topic_number_extractor(transformed_data_8)

#make dummy variable columns for top topic number
lb = LabelBinarizer()
topic_lb = lb.fit_transform(df["top_topic_number_lda8"])

#make df with categoricalized top topics
top_topics_df = pd.DataFrame(topic_lb)

#pull in pickled tfidf
tfidf = pickle.load(open('tfidf.pkl', 'rb'))
tfidf_title = tfidf.fit_transform(df["proper_title"])

#make it into a df to join onto beginning data:
tfidf_title_df = pd.DataFrame(tfidf_title.todense(), 
                  columns=tfidf.get_feature_names())

#create y and X for modeling
y = df["extracted_libcount"]
X = pd.concat([df[["age_in_2017", "sentiment_polarity", "sentiment_subjectivity", "number_of_words", "title_length"]], top_topics_df, tfidf_title_df, reading_level_dummies], axis=1)

#fit the model
rfr_final = RandomForestRegressor(max_depth=15, max_features=0.3, min_samples_leaf=7, n_estimators=100)
rfr_final.fit(X, y)

#pickle the model
filename = 'ttpc_rfr.pkl'
pickle.dump(rfr_final, open(filename, 'wb'))
