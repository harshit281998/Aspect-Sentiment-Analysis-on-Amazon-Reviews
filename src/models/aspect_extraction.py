# Python script for extracting aspects based on dependancy rules
#! /usr/bin/env python


import requests
import os
import csv
import numpy as np
import pandas as pd
import urllib.request
import gzip
import sys
import spacy
import json
#import enchant
from nltk.sentiment.vader import SentimentIntensityAnalyzer


BASE_PATH = os.getcwd()
PARENT = os.path.dirname(BASE_PATH)


#USE THIS FOR IMPORTING ANY FUNCTIONS FROM src
sys.path.insert(0,BASE_PATH)
from src.dataprep import clean_data

stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]


def fetch_reviews(filepath):
    raw_data = pd.read_table(filepath,nrows = 300,error_bad_lines=False)
    return raw_data



def apply_extraction(row,nlp):
    review_body = row['review_body']
    review_id = row['review_id']

    doc=nlp(review_body)
    #sid = SentimentIntensityAnalyzer()

    ## FIRST RULE OF DEPENDANCY PARSE -
    ## M - Sentiment modifier || A - Aspect
    ## RULE = M is child of A with a relationshio of amod
    rule1_pairs = []
    for token in doc:
        if token.dep_ == "amod" and not token.is_stop:
            #check_spelling(token.text)
            rule1_pairs.append((token.head.text, token.text,sid.polarity_scores(token.text)['compound']))
            #return row['height'] * row['width']


    ## SECOND RULE OF DEPENDANCY PARSE -
    ## M - Sentiment modifier || A - Aspect
    #Direct Object - A is a child of something with relationship of nsubj, while
    # M is a child of the same something with relationship of dobj
    #Assumption - A verb will have only one NSUBJ and DOBJ

    rule2_pairs = []
    for token in doc:
        children = token.children
        A = "999999"
        M = "999999"
        for child in children :
            if(child.dep_ == "nsubj" and not child.is_stop):
                A = child.text
                # check_spelling(child.text)

            if(child.dep_ == "dobj" and not child.is_stop):
                M = child.text
                #check_spelling(child.text)

        if(A != "999999" and M != "999999"):
            rule2_pairs.append((A, M,sid.polarity_scores(M)['compound']))


    ## THIRD RULE OF DEPENDANCY PARSE -
    ## M - Sentiment modifier || A - Aspect
    #Adjectival Complement - A is a child of something with relationship of nsubj, while
    # M is a child of the same something with relationship of acomp
    #Assumption - A verb will have only one NSUBJ and DOBJ

    rule3_pairs = []

    for token in doc:

        children = token.children
        A = "999999"
        M = "999999"
        for child in children :
            if(child.dep_ == "nsubj" and not child.is_stop):
                A = child.text
                # check_spelling(child.text)

            if(child.dep_ == "acomp" and not child.is_stop):
                M = child.text
                #check_spelling(child.text)

        if(A != "999999" and M != "999999"):
            rule3_pairs.append((A, M, sid.polarity_scores(M)['compound']))

    ## FOURTH RULE OF DEPENDANCY PARSE -
    ## M - Sentiment modifier || A - Aspect

    #Adverbial modifier to a passive verb - A is a child of something with relationship of nsubjpass, while
    # M is a child of the same something with relationship of advmod

    #Assumption - A verb will have only one NSUBJ and DOBJ

    rule4_pairs = []
    for token in doc:


        children = token.children
        A = "999999"
        M = "999999"
        for child in children :
            if(child.dep_ == "nsubjpass" and not child.is_stop):
                A = child.text
                # check_spelling(child.text)

            if(child.dep_ == "advmod" and not child.is_stop):
                M = child.text
                #check_spelling(child.text)

        if(A != "999999" and M != "999999"):
            rule4_pairs.append((A, M,sid.polarity_scores(M)['compound'])) # )


    ## FIFTH RULE OF DEPENDANCY PARSE -
    ## M - Sentiment modifier || A - Aspect

    #Complement of a copular verb - A is a child of M with relationship of nsubj, while
    # M has a child with relationship of cop

    #Assumption - A verb will have only one NSUBJ and DOBJ

    rule5_pairs = []
    for token in doc:
        children = token.children
        A = "999999"
        buf_var = "999999"
        for child in children :
            if(child.dep_ == "nsubj" and not child.is_stop):
                A = child.text
                # check_spelling(child.text)

            if(child.dep_ == "cop" and not child.is_stop):
                buf_var = child.text
                #check_spelling(child.text)

        if(A != "999999" and buf_var != "999999"):
            rule5_pairs.append((A, token.text,sid.polarity_scores(token.text)['compound']))

    aspects = []
    aspects = rule1_pairs + rule2_pairs + rule3_pairs +rule4_pairs +rule5_pairs
    dic = {"review_id" : review_id , "aspect_pairs" : aspects}
    return dic


def init_spacy():
    nlp=spacy.load("en_core_web_lg")
    for w in stopwords:
        nlp.vocab[w].is_stop = True
    return nlp


def spell_check_init():
    spell_dict = enchant.Dict("en_US")
    return spell_dict

def check_spelling(word):
    spell_dict = spell_check_init()
    if not spell_dict.check(word):
        list_of_words = spell_dict.suggest(word)
        #print(list_of_words)
        with open('spelling.txt', 'a') as f:
            f.write("%s :" % word)

            for item in list_of_words:

                f.write("%s ," % item)

            f.write("\n")


def extract_aspects(df):

    reviews = df[['review_id', 'review_body']]
    nlp=init_spacy()


    aspect_list = reviews.apply(lambda row: apply_extraction(row,nlp), axis=1) #going through all the rows in the dataframe

    return aspect_list


def aspect_extraction():
    filepath = BASE_PATH + "/data/raw/amazon_reviews_us_Electronics_v1_00.tsv"

    reviews =  fetch_reviews(filepath)
    reviews = clean_data.clean_data(reviews)
    aspect_list = extract_aspects(reviews)

    #print(aspect_list)

    return aspect_list



if __name__ == '__main__' :
    a = aspect_extraction()

    # USE THIS IF YOU WANT TO SEE THE ASPECTS IN A FILE
    # with open('your_file.txt', 'w') as f:
        # for item in a:
            # f.write("%s\n" % item)