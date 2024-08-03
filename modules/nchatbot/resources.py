from flask import current_app as app, request
import json
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
import random
import json
import pickle
import numpy as np
import tensorflow as tf
import nltk
from nltk.stem import WordNetLemmatizer
from nflask import bulking
from datetime import datetime
from nlpid import lemmatizer as lemma
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
from datetime import datetime
from keras import backend as K
from nflask.utils import precision_m, recall_m, f1_m, lemma_clean
import shutil

class ModelResources(Resource):

    parser = RequestParser()
    parser.add_argument(
        'file', type=str, location='json',
        help="file required", required=True)

    RAW_CLEAN ='train_clean.xlsx'
    TEST_RAW = 'test_raw.xlsx'

    def test_set(self):
        lemmatizer = lemma.Lemmatizer()
        test_set =json.loads(open('test_set_rsa_id.json').read())

        words = []
        words_clean = []
        classes = []
        documents = []
        ignoreLetters = ['?','!','.',',']
        _stopwords_ = stopwords.words('indonesian')

        for keyword in test_set['keywords']:
            for pattern in keyword['patterns']:
                wordList = nltk.word_tokenize(pattern)
                words.extend(wordList)
                documents.append((wordList, keyword['tag']))
                if keyword['tag'] not in classes:
                    classes.append(keyword['tag'])

        words = [lemmatizer.lemmatize(word) for word in words if word not in ignoreLetters and word not in _stopwords_ and word.isalpha()]
        words = [lemma_clean(word) for word in words]
        words = sorted(set(words))

        # print(words)
        classes = sorted(set(classes))

        pickle.dump(words, open('words_test_id.pkl', 'wb'))
        pickle.dump(classes, open('classes_test_id.pkl', 'wb'))

        testing = []
        outputEmpty = [0] * len(classes)

        # print(documents)

        for document in documents:
            # print(document)
            bag = []
            wordPatterns = document[0]
            wordPatterns = [lemma_clean(lemmatizer.lemmatize(word.lower())) for word in wordPatterns]
            for word in words:
                bag.append(1) if word in wordPatterns else bag.append(0)

            # print(bag)

            outputRow = list(outputEmpty)
            outputRow[classes.index(document[1])] = 1
            testing.append(bag + outputRow)

        random.shuffle(testing)
        testing = np.array(testing)

        testX = testing[:, :len(words)]
        testY = testing[:, len(words):]

        return testX, testY



    def get(self, **kwargs): 
        # lemmatizer = WordNetLemmatizer()
        lemmatizer = lemma.Lemmatizer()
        train_set = json.loads(open('train_set_rsa_id.json').read())
    
        words = []
        words_clean = []
        classes = []
        documents = []
        ignoreLetters = ['?','!','.',',']
        _stopwords_ = stopwords.words('indonesian')

        for keyword in train_set['keywords']:
            for pattern in keyword['patterns']:
                wordList = nltk.word_tokenize(pattern)
                words.extend(wordList)
                documents.append((wordList, keyword['tag']))
                if keyword['tag'] not in classes:
                    classes.append(keyword['tag'])
        # print(len(words), words)
        words = [lemmatizer.lemmatize(word) for word in words if word not in ignoreLetters and word not in _stopwords_ and word.isalpha()]
        words = [lemma_clean(word) for word in words]
        words = sorted(set(words))

        # print(words)
        classes = sorted(set(classes))

        pickle.dump(words, open('words_id.pkl', 'wb'))
        pickle.dump(classes, open('classes_id.pkl', 'wb'))

        training = []
        outputEmpty = [0] * len(classes)

        # print(documents)

        for document in documents:
            # print(document)
            bag = []
            wordPatterns = document[0]
            wordPatterns = [lemma_clean(lemmatizer.lemmatize(word.lower())) for word in wordPatterns]
            for word in words:
                bag.append(1) if word in wordPatterns else bag.append(0)

            # print(bag)

            outputRow = list(outputEmpty)
            outputRow[classes.index(document[1])] = 1
            training.append(bag + outputRow)

        # print(training)

        random.shuffle(training)
        training = np.array(training)

        trainX = training[:, :len(words)]
        trainY = training[:, len(words):]

        testX, testY = self.test_set()

        #training models
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Dense(128, input_shape=(len(trainX[0]),), activation = 'relu'))
        model.add(tf.keras.layers.Dropout(0.5))
        model.add(tf.keras.layers.Dense(64, activation = 'relu'))
        model.add(tf.keras.layers.Dropout(0.5))
        model.add(tf.keras.layers.Dense(len(trainY[0]), activation = 'softmax'))

        sgd = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy', precision_m, recall_m, f1_m])

        print('deleting previous model')
        shutil.rmtree('chatbot_model_id.hs')

        model.fit(trainX, trainY, epochs=100, batch_size=5, verbose=1)
        model.save('chatbot_model_id.hs', save_format='tf')

        print('closeset evaluate')
        close_results = model.evaluate(trainX, trainY, batch_size=5,verbose=0)
        for name, value in zip(model.metrics_names, close_results):
          print(name, ': ', value)
        
        # print('openset evaluate')
        # open_results = model.evaluate(testX, testY, batch_size=5,verbose=0)
        # for name, value in zip(model.metrics_names, open_results):
        #   print(name, ': ', value)

        return ('done training :), model updated timestamp:'+ str(datetime.now()))

    def post(self, **kwargs):
        # data train preparation xls --> json

        df = pd.read_excel(self.RAW_CLEAN)
        df_test = pd.read_excel(self.TEST_RAW)
        # print(df)

        df2 = df.groupby('tag', as_index=False).agg({'patterns':lambda x: list(x), 'responses':lambda y: list(y)}).to_dict('records')
        df_test2 = df.groupby('tag', as_index=False).agg({'patterns':lambda x: list(x), 'responses':lambda y: list(y)}).to_dict('records')

        result_train = {
            'total data train':len(df),
            'keywords': df2
        }
        result_test = {
            'total data test':len(df_test),
            'keywords':df_test2
        }

        with open('train_set_rsa_id.json', 'w') as f:
            json.dump(result_train, f)
        
        with open('test_set_rsa_id.json', 'w') as f:
            json.dump(result_test, f)

        return result_train
        # return True

class PrepResources(Resource):
    WORD_FILE ='word.json'
    DICT_FILE ='dictionary.json'
    HOST = 'http://localhost:9200'
    KEYSPACE_WORD = WORD_FILE.split('.')[0]
    KEYSPACE_DICT = DICT_FILE.split('.')[0]
    ID = ['id']
    ID_HASH = ['lemma']
    IS_HASH_ID = False
    MINIMUM_BATCH = 0

    def get(self, **kwargs):
        # cleansing cache
        # os.remove("words_id.pkl")
        # os.remove("classes_id.pkl")
        # os.remove("chatbot_model_id.hs")
        # lem = lemma.Lemmatizer()

        # sentence = 'Tahukah Anda berapa perkiraan biaya yang perlu disiapkan agar si buah hati dapat mengenyam Pendidikan ?'

        # # with open('sentence.txt', 'r') as sent_file:
        # #     sentence = sent_file.readline()

        # print('Before:\n', sentence, '\n')

        # _stopwords_ = stopwords.words('indonesian')

        # preprocessed_sent = []

        # for token in word_tokenize(sentence.lower()):
        #     if token not in _stopwords_ and token.isalpha():
        #         preprocessed_sent.append(token)

        # lemmatized_sent = []

        # for token in preprocessed_sent:
        #     lemmatized = lem.lemmatize(token)
        #     # print(lemmatized)

        #     if(type(lemmatized) == tuple):
        #         lemmatized_sent.append(lemmatized[0])
        #     else:
        #         print(lemmatized)
        #         lemmatized_sent.append(lemmatized)

        # print('After:\n', " ".join(lemmatized_sent))

        return 'get'

    def post(self, **kwargs):
        with open(self.WORD_FILE) as wf:
            data_wf = json.load(wf)
        print("got",len(data_wf),"record(s) for word on",datetime.now())
        
        with open(self.DICT_FILE) as df:
            data_dict = json.load(df)
        print("got",len(data_dict),"record(s) for dict on",datetime.now())
        
        # print(self.KEYSPACE_WORD, self.KEYSPACE_DICT)
        bulking.send_bulk(self.HOST,self.KEYSPACE_WORD,data_wf,len(data_wf),self.ID,is_hash=False)
        bulking.send_bulk(self.HOST,self.KEYSPACE_DICT,data_dict,len(data_dict),self.ID_HASH,is_hash=True)
        
        return 'word & dictionary updated!'