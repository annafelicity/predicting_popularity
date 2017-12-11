import sys
import pickle
import pandas as pd
import re
from titlecase import titlecase
from textblob import TextBlob
from textstat.textstat import textstat
from sklearn.preprocessing import LabelBinarizer


title = str(sys.argv)
x = [(title, 0)]
df_x = pd.DataFrame(x, columns=["title", "age_in_2017"])

#turn title into proper title
def make_proper_title(string):
    string = string.replace(" : ", ": ")
    string = string.rstrip(".")
    return titlecase(string)

df_x["proper_title"] = df_x["title"].apply(make_proper_title)

#add sentiment analysis
def text_blob_sentiment_polarity(value):
    blob = TextBlob(value)
    return blob.sentiment.polarity
def text_blob_sentiment_subjectivity(value):
    blob = TextBlob(value)
    return blob.sentiment.subjectivity

df_x["sentiment_polarity"] = df_x["proper_title"].apply(text_blob_sentiment_polarity)
df_x["sentiment_subjectivity"] = df_x["proper_title"].apply(text_blob_sentiment_subjectivity)


#add reading level
def reading_level_comp(string):
    try:
        level = textstat.text_standard(string)
        return level
    except:
        return "Unclear"

df_x["reading_level"] = df_x["proper_title"].apply(reading_level_comp)

lb_rl = pickle.load(open('lb_for_rl.pkl', 'rb'))

#use the lb for the input title
lb_rl_input = lb_rl.transform(df_x["reading_level"])
lb_rl_input

reading_level_dummies = pd.DataFrame(lb_rl_input)

#add number of words column
df_x["number_of_words"] = df_x["proper_title"].apply(lambda x: len(x.split()))

#add title length
df_x["title_length"] = df_x["proper_title"].apply(lambda x: len(x))

#CountVectorize the words in the input string in keeping with the topic modeling model
cv_for_lda = pickle.load(open('cv_for_lda.pkl', 'rb'))
input_words = cv_for_lda.transform(df_x["proper_title"])

#transform the input string using the training set model
lda_8 = pickle.load(open('ttpc_lda.pkl', 'rb'))
transformed_data_8= lda_8.transform(input_words)
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

df_x["top_topic_number_lda8"] = top_topic_number_extractor(transformed_data_8)

topics_list = []
for i in range(0,8):
    if df_x["top_topic_number_lda8"][0] == i:
        topics_list.append(1)
    else:
        topics_list.append(0)

#turn topics dict into df for joining
top_topics_df = pd.DataFrame(topics_list).transpose().copy()

#transform the input into tfidf
tfidf = pickle.load(open('tfidf.pkl', 'rb'))
tfidf_title = tfidf.transform(df_x["proper_title"])

#make it into a df to join onto beginning data:
tfidf_title_df = pd.DataFrame(tfidf_title.todense(), 
                  columns=tfidf.get_feature_names())

#make X to match main final model
X = pd.concat([df_x[["age_in_2017", "sentiment_polarity", "sentiment_subjectivity", "number_of_words", "title_length"]], top_topics_df, tfidf_title_df, reading_level_dummies], axis=1)

#run X through model for prediction
rfr_final = pickle.load(open('ttpc_rfr.pkl', 'rb'))

result = rfr_final.predict(X)

result_int = result.astype(int)

print(result_int)

