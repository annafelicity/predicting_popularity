#import all the things for the submodels

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from textstat.textstat import textstat
from sklearn.preprocessing import LabelBinarizer
import pickle

#read in the data
titles = pd.read_csv("/Users/annafriedman/GA/GACapstoneProject/full_data/final_ttpc_data_3831rows.csv")

#print(len(titles))

#the LDA topic-modeling submodel (it first requires another submodel to count-vectorize the title words)
cv_for_lda = CountVectorizer(min_df=5, max_df=.75, ngram_range=(1,3), stop_words="english")

words = cv_for_lda.fit_transform(titles["proper_title"])

lda_8 = LatentDirichletAllocation(n_topics=8, max_iter=15,
                                topic_word_prior=2,
                                learning_offset=50., random_state=3)

lda_8.fit(words)

# save the lda_8 model as a pickle file
filename = 'ttpc_lda.pkl'
pickle.dump(lda_8, open(filename, 'wb'))

#save the cv_for_lda model as a pickle file (because it is needed on its own in the input pipeline)
filename_2 = 'cv_for_lda.pkl'
pickle.dump(cv_for_lda, open(filename_2, 'wb'))

#the tfidf model
tfidf = TfidfVectorizer(min_df=5, max_df=.95, lowercase=False, stop_words="english", ngram_range=(1,3))
tfidf_title = tfidf.fit_transform(titles["proper_title"])

#save it as a pickle file
#not sure if I need to save tfidf_title too (might need for the input pipeline?)
filename_3 = 'tfidf.pkl'
pickle.dump(tfidf, open(filename_3, 'wb'))

#pickle for reading level and the dummies df for it
def reading_level_comp(string):
    try:
        level = textstat.text_standard(string)
        return level
    except:
        return "Unclear"
        
titles["reading_level"] = titles["proper_title"].apply(reading_level_comp)
lb_rl = LabelBinarizer()
lb_rl.fit_transform(titles["reading_level"])

filename_4 = 'lb_for_rl.pkl'
pickle.dump(lb_rl, open(filename_4, 'wb'))