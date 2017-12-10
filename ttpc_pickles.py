#topic modeling model

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pickle

#read in the data
titles = pd.read_csv("/Users/annafriedman/GA/GACapstoneProject/full_data/final_ttpc_data_3831rows.csv")

#print(len(titles))

cv_for_lda = CountVectorizer(min_df=5, max_df=.75, ngram_range=(1,3), stop_words="english")

words = cv_for_lda.fit_transform(titles["proper_title"])

lda_8 = LatentDirichletAllocation(n_topics=8, max_iter=15,
                                topic_word_prior=2,
                                learning_offset=50., random_state=3)

lda_8.fit(words)

# save the lda_8 model to disk
filename = 'ttpc_lda.pkl'
pickle.dump(lda_8, open(filename, 'wb'))

#save the cv_for_lda model to disk
filename_2 = 'cv_for_lda.pkl'
pickle.dump(cv_for_lda, open(filename_2, 'wb'))