import json
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import requests
from twilio.request_validator import RequestValidator
from nflask import twilio_validator
import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from keras.models import load_model
import random
from nlpid import lemmatizer as lemma
from nflask.utils import lemma_clean, precision_m, recall_m, f1_m
from flask import current_app as app, request
from nflask.auth import generate_token, generate_session, save_session, clear_session, get_session_list
from datetime import datetime


class chatInterfaceResources(Resource):

    parser = RequestParser()
    parser.add_argument(
        'question', type=str, location='json',
        help="data required", required=True)

    # lemmatizer = WordNetLemmatizer()
    lemmatizer = lemma.Lemmatizer()
    train_set = json.loads(open('train_set_rsa_id.json').read())
    model = load_model('chatbot_model_id.hs', compile=False)


    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemma_clean(self.lemmatizer.lemmatize(word.lower())) for word in sentence_words]
        return sentence_words

    def bag_of_words(self, sentence, show_details=True):
        words = pickle.load(open('words_id.pkl', 'rb'))
        
        sentence_words = self.clean_up_sentence(sentence)

        bag = [0]*len(words)
        for s in sentence_words:
            for i, word in enumerate(words):
                if word == s:
                    bag[i] = 1
                    if show_details==True:
                        print('found in bag: %s' % word)
        # print(np.array(bag))
        return(np.array(bag))

    def predict_class(self, sentence):
        classes = pickle.load(open('classes_id.pkl', 'rb'))

        p = self.bag_of_words(sentence, show_details=True)
        res = self.model.predict(np.array([p]))[0]
        # print(res)
        ERROR_THRESHOLD = 0.5
        results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]

        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({'keyword': classes[r[0]], 'probability': str(r[1])})
        return return_list

    def getKeyword(self, keywords, keywords_json):
        if len(keywords) != 0:
            print('ga kosong')
            tag = keywords[0]['keyword']
            list_of_keywords = keywords_json['keywords']
            for i in list_of_keywords:
                # print(i)
                if(i['tag']== tag):
                    result = random.choice(i['responses'])
                    break
                else:
                    result = 'maaf saya tidak mengerti'
        else:
            print('kosong')
            result = 'maaf saya tidak mengerti'

        return result

    def get(self, **kwargs):
        return 'your question will answer by chatbot'


    def post(self, **kwargs): 
        account_sid = app.config['TWILIO_SANDBOX_ACCOUNT_SID']
        auth_token = app.config['TWILIO_SANDBOX_AUTH_TOKEN']
        client = Client(account_sid, auth_token)

        es = app.elastic
        es_index = app.elastic.indices

        # Fetch the message
        twilio_req = request.form

        msg = twilio_req.get('Body').lower() # Reading the message from the whatsapp
        waUser = twilio_req.get('From')
        sender = twilio_req.get('To')

        #check session
        current_session = get_session_list(phoneNo=waUser)
        # print(current_session)
        category = 'test'
        is_question = False 
        is_correct = False

        if len(current_session) == 0:

            #create session
            token = generate_token(twilio_req)
            session = generate_session(twilio_req, token)

            #save session to redis
            save_session(session)

        else:
            token = str(current_session).split(':')[1]


        if es_index.exists(index='twilio_chat_data'):
            pass
        else:
            es_index.create(index='twilio_chat_data')

        data = {
            'session_id': token,
            'phone_number': waUser.split(':')[1],
            'full_name': twilio_req.get('ProfileName'),
            'msg_log': [
            {
                'msg': msg,
                'category': category,
                'msg_type': 'incoming',
                'is_question': is_question,
                'is_correct': is_correct, 
                'created_date': datetime.now()
            },
            ]
        }

        data_update = {
          "script": {
            "source": "ctx._source.msg_log.add(params.msg_add)",
            "params": {
            'msg_add':{
                'msg': msg,
                'category': category,
                'msg_type': 'incoming',
                'is_question': is_question,
                'is_correct': is_correct, 
                'created_date': datetime.now()
                }
            }
          }
        }

        query_body = {
          "query": {
              "match": {
                  "_id": waUser.split(':')[1]
              }
          }
        }

        res = es.search(index="twilio_chat_data", body=query_body)
        if res['hits']['total']['value'] == 1:
            print("updating index...")
            es.update(index='twilio_chat_data',id=waUser.split(':')[1], body=data_update)
        else:
            print("creating index...")
            es.index(index='twilio_chat_data', doc_type='_doc', id=waUser.split(':')[1], body=data)


        # get prediction from AI model

        if msg != '':
            print(msg)
            ints = self.predict_class(msg)
            res = self.getKeyword(ints, self.train_set)
        else:
            res = 'maaf saya tidak mengerti'

        resp = MessagingResponse()
        reply=resp.message()

        # Create reply
        category = 'test'

        rep_msg = res
        reply=client.messages.create(
          to=waUser,
          body=rep_msg,
          from_=sender
        )
        category = 'test'
        reply_update = {
          "script": {
            "source": "ctx._source.msg_log.add(params.msg_add)",
            "params": {
            'msg_add':{
                'msg': rep_msg,
                'category': category,
                'msg_type': 'outcoming',
                'is_question': is_question,
                'is_correct': is_correct, 
                'created_date': datetime.now()
                }
            }
        }
        }

        es.update(index='twilio_chat_data',id=waUser.split(':')[1], body=reply_update)

        return True