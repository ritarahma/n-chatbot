import json
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import requests
from twilio.request_validator import RequestValidator
from nflask import twilio_validator
from nflask.auth import generate_token, generate_session, save_session, clear_session, get_session_list
from flask import current_app as app
from datetime import datetime


class templateResources(Resource):

    parser = RequestParser()
    parser.add_argument(
        'data', type=str, location='json',
        help="data required", required=True)

    def schedule_handler(self, waUser, sender, category):
        wlcmMsg = 'Anda memilih menu Tanya Jadwal, ada yg bisa saya bantu?'
        reply=client.messages.create(
              to=waUser,    
              body=wlcmMsg,
              from_=sender
            )


        return True

    def registration_handler(self, opt):
        return True

    def registration_handler(self, opt):
        return True

    def topic_handler(self, msg, waUser, sender):
        # 1. tanya_jadwal
        # 2. pendaftaran
        # 3. informasi_layanan

        if msg == '1':
            category=1
            result = self.schedule_handler(waUser, sender, category)
        elif msg == '2':
            result = self.registration_handler()
        elif msg == '3':
            result = self.info_handler()
        else:
            result='maaf, silahkan pilih salah satu menu berikut: 1. Tanya Jadwal, 2. Pendaftaran, 3. Informasi Layanan'

        return result

    def get(self, **kwargs): 

        return ('this must be a chatbot template')

    # @twilio_validator.validate_twilio_request
    def post(self, **kwargs): 
        account_sid = app.config['TWILIO_ACCOUNT_SID']
        auth_token = app.config['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)

        # ES var
        es = app.elastic
        es_index = app.elastic.indices

        # template msg
        wlcmMsg = 'Terima kasih telah menghubungi RSA, silahkan pilih menu berikut untuk memulai: 1. Tanya Jadwal, 2. Pendaftaran, 3. Informasi Layanan'
        
        # """Respond to incoming calls with a simple text message."""
        # Fetch the message
        twilio_req = request.form

        msg = twilio_req.get('Body').lower() # Reading the message from the whatsapp
        waUser = twilio_req.get('From')
        sender = twilio_req.get('To')

        #check session
        current_session = get_session_list(phoneNo=waUser)
        # print(current_session)
        category = 'test_template'
        is_question = False 
        is_correct = False

        if len(current_session) == 0:

            #create session
            token = generate_token(twilio_req)
            session = generate_session(twilio_req, token)

            #save session to redis
            save_session(session)

        
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

            resp = MessagingResponse()
            reply=resp.message()

            rep_msg = wlcmMsg
            reply=client.messages.create(
              to=waUser,
              body=rep_msg,
              from_=sender
            )

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

        else:
            token = str(current_session).split(':')[1]
            msg = self.topic_handler(msg, waUser, sender)

            rep_msg = msg
            reply=client.messages.create(
              to=waUser,
              body=rep_msg,
              from_=sender
            )

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

        
        # return str(reply.sid)
        return True