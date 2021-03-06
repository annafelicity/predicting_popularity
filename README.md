## Popularity Predictions in Tattoo-Book Publishing
### Dr. Anna Felicity Friedman

#### Premise of project:

Authors typically care about two things when publishing books: popularity and immortality. (They also care about disseminating information, of course, but that does not lend itself readily to predictive modeling.) Popularity can be measured in various ways: by book sales, by book ratings, by the number of libraries that end up holding a book over time, etc. Immortality can be measured similarly (for example if books keep selling year after year or ratings stay high over time), but for books published more than a few decades ago, the number of libraries that hold a book becomes the key metric that we can access. Book holdings have been tracked in a systematic fashion for well over a century, and these pre-digital records have been widely transformed and input into library-catalog databases.

When we look at what drives book purchasers (or suggesters, in the case of some library acquisitions that are patron-driven), the title jumps out as one of the main criteria upon which someone might make a decision to acquire or not acquire any particular book. Thus I arrived at my problem question: Can title words be used to create a predictive model that generates how many libraries might hold a book?

As a published author, I know that many of us struggle with what to title our books to achieve the greatest reach. I have long wished for some sort of book-title calculator that could give me subject-specific guidance. I did find one “best-seller novel” book-title calculator (http://www.lulu.com/titlescorer/), but for those of us publishing other types of books to niche-market audiences, it would be useful to have a topic-specific generator. (The Lulu Titlescorer also requires a lot of user-input decisions on myriad title characteristics that require significant grammatical knowledge; I was hoping to create a calculator that only needs the title as input.) I decided to use my own area of academic research--tattoo history and culture--as a starting point for a model that, if successful, could be used for other niche subject areas. The calculator will be hosted on two different websites: my personal research website [tattoohistorian.com](http://tattoohistorian.com/) and the [Center for Tattoo History and Culture](https://centerfortattoo.org/), a foundation for which I serve as volunteer director. What I describe below is the beginnings of a project that I plan to continue working on.

#### Data Acquisition:

Book holdings in libraries around the world are primarily housed in [OCLC’s WorldCat database](http://www.worldcat.org/), which features over 2 billion library catalog records for individual books held in over 10,000 international member libraries. This data is accessible to the public via a website search interface and also available to member libraries and partner developers via a series of APIs. I successfully petitioned OCLC to give me trial access to the general search API, which was limited to 100 queries per day. I was hoping to have them up that limit, but they did not grant this. 

OCLC has fairly strict terms of service on what you can do with their data, and they do not want people holding “material” amounts of it nor mining “large amounts”. I explained that my project involved fitting a model to a miniscule number of records (my initial estimate was less than 10,000, which held) or .0005% of their data (an immaterial amount, by any reasonable estimate). So I feel this project falls well within their terms of service.

My starting dataset was based on a broad keyword search for anything and everything that had the word stem tattoo* in it published between 1850 and today. This returned a 9391-row dataset. 

These 9391 dataset rows were far from straightforward. Some of these rows proved to be duplicates in several different ways. OCLC has an entity-matching algorithm that is not accessible via the API, but it is reflected in the webpage for each book which presents the concatenated data across matching catalog records. (See endnote 1 for a more detailed account of this entity-matching issue.)

Faced with very limited queries via the API as well as the entity-matching issue, I implemented my data acquisition for each book in three ways:

1) A script with a series of API requests to get overview data for each unique book record: I could pull 100 of these overview values through each query, so I just snuck in under the daily limit when pulling all the overview records in one script run. The overview records gave me the following information: unique OCLC record number, title, author, summary (not always present), ISBN and LCCN numbers (not always present), and the url for each page on the website version of the catalog. All the rest of the data I needed was only available in individual book queries, and my daily 100-query API limit made getting this data via the API impracticable.

2) The first of two web scrapers: Using the url for each book page, I wrote a web scraper using a combination of the requests and Beautiful Soup libraries that allowed me to additionally pull other data present in the source code for each website page that might be relevant. This way I acquired the year (not always present), the publisher (not always present), the type of book (e.g. “print book”, “ebook”, etc.), a limited genre category only present in some records (e.g. “Fiction”, “Government publication”), the language of publication (not always present), and the age-audience-level for non-adult books (not always present). Unfortunately, the key value that I needed for my popularity predictions--the total count of libraries that hold any given book--was only available via dynamic HTML.

3) The second of two web scrapers: Again using the url for each book page, I wrote a dynamic HTML web scraper using selenium that pulled the total library count from a header for a list of library locations where one might find the book. In retrospect, I should have simultaneously pulled the subject data for each book (also only available via dynamic HTML or in the individual API queries to each book record), but I can add this in the future.

#### Exploratory Data Analysis:

First, by dropping duplicate rows that had the same URL, I was able to take partial advantage of OCLC’s entity-matching algorithm. However, their entity-matching is not perfect. 157 books hold the same title in the dataset I pulled, some of which definitely refer to the same book and thus need to be merged. These 157 titles account for 424 rows of data or about 8%.  I hope to write my own entity-matching/de-duping function to pull together these total library counts where relevant. This will likely improve my model.

I further narrowed the dataset to just printed books and those either published in English or where the language was not noted (the vast majority of the latter, from a perusal of the data, are in English). I did this because early experiments with natural language processing techniques demonstrated that foreign words were complicating the model, and the goal of the calculator is to predict English-language titles. Then I also dropped about 1000 rows where the library count was absent. (See endnote 2.) The resulting dataset for modeling ended up being 5313 rows.

Looking at the value counts for the total counts of library holdings, it became clear that the data had a very uneven distribution skewed heavily right. It is essentially split in two with about half the data falling into library counts of 25 or less and the rest falling into a much more gentle curve between values of 25 and about 3500. In fact 2597 titles are held by just one library each.  You can see the library-count distribution here:

![library count distribution](/images/total_libcount_distribution.png)

#### Feature Engineering/Feature Extraction:

There are three main elements in this dataset that are likely to be predictive of popularity as measured by total library holdings: the title, the year of publication, and the genre of the book. It may be the case that in a future version of the model, users will need to input information about the genre of the book (from a preselected list that might include things like fiction/non-fiction or juvenile/adult audience.) A fourth factor that could be investigated in the future is the popularity of the author.

First, I standardized all of the titles using the titlecase library to reflect capitalization that is commonly used (the OCLC catalogers do not use a capitalization format that reflects the way book titles are actually printed, and I wanted the model to be most reflective of the titles upon which book purchasers were making their decisions).

**Basic statistics:**

I added “age_in_2017”, “number_of_words”, “title_length” (i.e. the total length of the title string).

**Sentiment analysis:**

I used the TextBlob sentiment analysis processor to add columns for subjectivity and polarity scores.

**Reading Level as Categorical Variables:**

I used the textstat library to determine the reading level for each title. I then created a set of categorical variables based on these assigned reading levels.

**Word Tokenization:**

I used tf-idf for word tokenization to be able to account for more unique words that occur across the corpus of titles. In several model-test comparisons between regular count vectorization and tf-idf vectorization, it also was clear that tf-idf produced superior results in model scoring. I experimented with various versions of this set of features, particularly with respect to stopwords. I landed on the hyperparameters of min_df=5, max_df=.95, lowercase=False, stop_words="english", ngram_range=(1,3). This allowed for initial capitalized words of "The", "A", "An" to have weight in the model, which makes sense from a theoretical standpoint as the word "The" is more definitive and consistently came up in a feature importances analysis as one of the common splits in the chosen tree model.

**Topic Modeling as Categorical Variables:**

I used Latent Dirichlet Allocation (LDA) to assign topics to each title based on their similarity to other titles in the data set. I experimented with a variety of hyperparameters (both in the CountVectorizer function that tokenized the title words and word-groups and in the LDA model itself). Here using the traditional natural-language-processing technique of lower-casing all the words worked better, as did removing English stopwords (I'd actually like to experiment with additional added stopwords as well). For hyperparameters on the LDA model, a learning offset of 50. (quite a bit above the default of 10.) worked best, as did a topic_word_prior setting of 2. Since it’s a small dataset, I increased the max iterations to 15 and that seemed to improve the groupings even more.

Determining whether the topic modeling is representative of distinct topics in the dataset is, of course, subjective. As I know this dataset very well, in combination with the aforementioned hyperparameters it seemed to me that the number of topics coalesced into something workable at 8 topics. This is where I started to see clear categories for fiction, poetry, history, the military, and subgenres of tattoo subjects like Japanese and Maori tattooing that definitely form their own sub-corpuses within the dataset. I would like to spend much more time reading about hyperparameter selection in LDA models, particularly the document and topic priors (and specifically [this academic paper](https://mimno.infosci.cornell.edu/papers/NIPS2009_0929.pdf) to tweak this part of the model further.

**Non-title-derived variables:**

I tried out adding in “is_fiction” and “is_non_adult” categorical features. The former was determined by assigning 1 to books with a genre of fiction or poetry. The latter determined by assigning a 1 to any books with a non-adult audience indicated in the record.

Ultimately I was able to determine that these variables did not affect the prediction outcomes enough to merit keeping them in the model (they improved the scores by a tiny bit). To deploy a model with these features, I would either need the user to input genre/audience criteria or I would need to see if it was possible to predict these features using fiction/non-fiction and adult/non-adult classification sub-models.

#### Data Problems:

Given the extreme skew of the data, I decided to limit the model to library count values of 2 to 1500. Having so many library counts of 1 was having an undue influence on my data, so I decided to have the model focus on library counts of 2 or greater. On the other end of the value spectrum, outliers were also affecting my predictions. I made the decision to make a library count of 1500 the top value for my model based on the data visualization and where the values started to really thin out as well as taking into consideration that 1500 is more than 4 standard deviations from the mean (the standard deviation on the full dataset was 312 and the mean was 147). By narrowing the data to a range of library counts between 2 and 1500 the standard deviation changed to 253 with a mean of 167. 

In the future I would like to experiment more with other subsets of the data to see if I can further improve the model, for example library counts of 10 to 1500.

#### The Model:

Using Scikit-learn, I tried a wide range of different regression model types, and two scored reasonably well in early tests to consider for further model testing: RandomForest Regressor and GradientBoosting Regressor. The model types that were eliminated in early testing were AdaBoost, ExtraTrees, MLB, SVR, and basic Ridge and Lasso Regressors (Ridge performed almost well enough for further testing).

To perform cross validation, I set up a train/test split on each of various combinations of features (4 different combinations) with one third going to the test set. With no hyperparameters adjusted from the default, the model was severely overfit on the training set and scored terribly on the test set (with an r-squared score slightly in the negative). By adjusting hyperparameters such as n_estimators and min_samples_leaf, I was able to bring down the overfitting and get the test set consistently scoring better. As mentioned above, although the feature set with "is_fiction" and "is_non_adult" performed slightly better than just the title alone, for deployment's sake, it made sense to go with the version with just features based off the title.
 
Using GridSearchCV, I was able to iterate over various hyperparameters and found that the best estimator parameters were max_depth: 20, max_features: 0.3, min_samples_leaf: 5, and n_estimators: 100. Running the training and test sets with these parameters, I was able to achieve nearly matching r-squared and explained variance scores of 6.3 and 6.4%. The mean absolute error on the test set was 165 (which was reasonable considering the range of library counts in the training set ran from 2 to 1500).
 
When I re-ran the entire data set using these grid-searched hyperparameters, the results improved even more. Predicted vs. actual values on the entire data set had r-squared and explained variance rise to 26% and the mean absolute error decline to 146. Compare this to the Lulu Title Scorer cited above which, with its many user inputs and much cleaner data set, only achieved 40% of explained variance.

Looking at a scatter plot of the predicted versus actual values on the entire data set, you can see that the higher values are being underpredicted and the lower values are being overpredicted. I discuss later in this report several thoughts on solving this problem.

![predicted vs actual values](/images/actual_vs_predicted_libcount.png)

And a detail of the lower values, since they are so densely packed in the above image:

![detail predicted vs actual](/images/actual_vs_predicted_libcount_detail.png)

#### Deployment:

In order to deploy this model, I will need to set up a pipeline for the user-input titles to be transformed into the same features as the existing model. This brings up the issue of controlling for the year, as the dataset reflects a wide historical span (1850-today). A book that has only been out for one year (or zero years) may not be in as many libraries as one that has been out for several, although the current model seems to vary with respect to this. I have been experimenting with having the model predict outcomes for library holdings after 1, 5, and 10 years to see if there is a difference.

You can see here some outcomes of experiments with hypothetical user-input titles:

![sample predictions](/images/sample_predictions.png)

#### Future goals:

Given that the model consistently overpredicts low library counts and underpredicts high library counts in the test set, it may be worth creating a model that is actually a set of models--a classifer that works on the incoming title inputs and determines if the title might be low, medium, or high value, with a different regression model run for each classification. The classifications could be something along the line of just 1 (or something like 1 to 10), one for the middle range (say, 2 to 1500), and one for the high outliers (over 1500).

I want to do more feature-engineering experiments. One thing that seems to have a lot of significance with titles is the sentiment. I’d like to try out some of the other sentiment analysis libraries like VaderSentiment and see if they perform better (or differently). I also would like to write a function for a feature that takes into account the position of words in each title string. This could take at least two forms: an iteration over all words in the training set or an iteration over just the top words. For example, does it matter if "Tattoo" is the first word, the second word, the last word?

I’d also like to think about a model that makes predictions for popularity based on several different sets of years since publication. I have a hypothesis that library holdings for any given book form a curve over time with peak library holdings probably at about 10 or 20 years of book age, and then due to books getting lost or damaged or deaccessioned because they were not popular with patrons their numbers drop off. It would be interesting to see if this drop off varies by genre of book (or topic of book using the topic modeling feature). Are best-sellers less prone to immortality in libraries (perhaps due to loss/damage over time) versus nerdy academic books well preserved in special collections?

Other future research might determine whether better outcomes in predictions can emerge from having the user input additional criteria such as the genre of the book (fiction, biography, poetry, history, etc.). I would also like to try re-running the model using only books pulled from a subject keyword search on tattoo* rather than a general keyword search to reduce the noise in the data.

I’d also like to try this as a classification model problem. Instead of predicting continuous values, I could predict whether a book would fall into one of several set ranges for popularity, e.g. 1 to 9, 10 to 99, 100 to 999, 1000 and over.

Also I’d like to add on other metrics such as the Amazon.com sales rank and overall rating and GoodReads rating.

#### Conclusion:

A popularity prediction calculator has value as one of several tools in an author’s toolbox to help craft and narrow choices of book title. This current model predicts the total number of libraries that will hold a book 26% better than randomly guessing; in other words, my predictive model using the title alone explains 26% of the variance. This can be helpful when narrowing down title choice among several different options.


#### Endnotes:

1) The reason for duplicates in the dataset has to do with the way books are catalogued in OCLC. Most libraries use what’s called copy cataloging, where they use a standard record already in the WorldCat database. Some libraries, however, use their own original cataloging and these records then up mixed in with the rest (these records are identifiable since they often consist of only one or a few library counts). Also books get published in different editions and sometimes these end up standing alone as separate entities in WorldCat. For my purposes, since I am concerned with the impact of the title only, I can sum up the total counts for each duplicate record.

2) Many of the rows without a library count appear to be for book records that were imported into WorldCat from Library of Congress catalog records but which were not actually acquired into any collections; one other possible avenue to explore with respect to this subset of the data and the predictive model is to keep them in the dataset and set their library-count value to zero.

#### For further reading:

Here are some references that were helpful to me:

https://tedunderwood.com/2012/04/07/topic-modeling-made-just-simple-enough/

http://blog.christianperone.com/2011/09/machine-learning-text-feature-extraction-tf-idf-part-i/

http://stackoverflow.com/questions/20463281/how-do-i-solve-overfitting-in-random-forest-of-python-sklearn

