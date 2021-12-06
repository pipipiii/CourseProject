# Topic mining with LDA
# https://www.kaggle.com/panks03/clustering-with-topic-modeling-using-lda
import logging
import os
import nltk

from collections import defaultdict
from gensim import corpora
# from gensim.models import ldamulticore
from gensim.models import ldamodel
from gensim.test.utils import common_corpus, common_dictionary
from numpy import random
from textblob import TextBlob

def _init_nltk():
    logging.info("YTSGET: Initializing NLTK")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    download_dir = os.path.join(root, 'nltk_data')
    os.chdir(download_dir)
    nltk.data.path.append(download_dir)
    logging.info("YTSGET: Initializing NLTK - done")


def _preprocess(doc):
    '''Preprocess: tokenize, remove punctuations, remove stopwords.'''
    # tokenize without punctuations
    logging.info("YTSGET: Preprocessing documents")
    tokenizer = nltk.RegexpTokenizer(r"\w+")
    words = tokenizer.tokenize(doc)
    # to lower case
    words = [word.lower() for word in words] 
    # remove stopwords (English only)
    words = [word for word in words 
            if word not in nltk.corpus.stopwords.words('english')]
    # for analyzing topics, leave only nouns
    pos_tags = nltk.pos_tag(words)
    words = [word for (word, tag) in pos_tags 
            if (tag in ("NN", "NNS"))]
    return words

def _build_topic_to_comments_dict(all_comments_topics, comments):
    '''Build a dictionary of topic to list of corresponding comments'''
    topic_comments = defaultdict(list)
    for i, single_comment_topics in enumerate(all_comments_topics):
        for topic_and_score in single_comment_topics:
            if topic_and_score[1] >= 0.6:
                topic_comments[topic_and_score[0]].append(comments[i])
                continue
    return topic_comments

def _build_topic_and_sentiment_dict(topics, topic_to_comments, sentiment_func):
  '''Given the topics and topic to comments, build the result topic to sentiment dict.'''
  topic_sentiment = defaultdict()
  for topic in topics:
    topic_sentiment[str(topic[0])] = {
        "topic": [
            (topic_and_score[0], str(topic_and_score[1])) 
            for topic_and_score in topic[1]
        ], 
        "sentiment": str(sentiment_func(topic_to_comments[topic[0]]))
    }
  return topic_sentiment

def _analyze_topics_and_sentiment(comments, sentiment_func, num_topics=2):
    # Preprocessing
    pre_processed_comments = [_preprocess(comment) for comment in comments]

    # Build dictionary from corpus
    logging.info("YTSGET: Building dictionary")
    doc_dict = corpora.Dictionary(pre_processed_comments)

    # High filter threshold for words that appear very often - comments are usually discussing
    # the same topic as the video.
    doc_dict.filter_extremes(no_below=10, no_above=0.9)
    logging.info("YTSGET: Tokenizing")
    corpus = [doc_dict.doc2bow(doc) for doc in pre_processed_comments]

    # Train LDA model for the current videos' comments
    logging.info("YTSGET: Building LDA model")
    # lda_model = ldamulticore.LdaMulticore(
    #     corpus, 
    #     id2word=doc_dict, 
    #     num_topics=num_topics,
    #     batch=True,
    #     minimum_probability=0.05,
    #     iterations=350,
    #     passes=100)
    lda_model = ldamodel.LdaModel(
        corpus, 
        id2word=doc_dict, 
        num_topics=num_topics,
        minimum_probability=0.05,
        iterations=350,
        passes=100)
    # Get topic for each comment
    logging.info("YTSGET: Getting topics")
    all_comments_topics = lda_model.get_document_topics(corpus)

    # Build a dict from topics to their corresponding comments
    topic_to_comments = _build_topic_to_comments_dict(all_comments_topics, comments)
    topic_and_sentiment = _build_topic_and_sentiment_dict(
        lda_model.show_topics(formatted=False), topic_to_comments, sentiment_func)
    return topic_and_sentiment

# Helper function to calculate overall sentiment.
# Overall video comments sentiment score is average of all comments
def _get_overall_sentiment(comments, senti_func):
    # This polarity score is between -1 to 1
    senti_scores = [senti_func(comment) for comment in comments]
    return sum(senti_scores) / len(senti_scores)
    
# Sentiment using TextBlob
def get_textblob_sentiment(comments):
    logging.info("YTSGET: Getting textblob sentiment")
    return _get_overall_sentiment(
        comments, 
        lambda comment: TextBlob(comment).sentiment.polarity)

def analyze_sentiment(comments):
    logging.info("YTSGET: Analyzing comments...")
    _init_nltk()
    random.seed(54321) # Ensure results are consistent
    return {
        "overallSentiment": str(get_textblob_sentiment(comments)), 
        "topicSentiments": _analyze_topics_and_sentiment(comments, get_textblob_sentiment)
    }