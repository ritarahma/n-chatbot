import http.client
from flask_restful import Resource
from flask import current_app as app, request
import json

class AuthenticationResources(Resource):
	def get(self, **kwargs):

		conn = http.client.HTTPSConnection("service-chat.qontak.com")
		payload = "{\n  \"username\": \"ritarahma1706@gmail.com\",\n  \"password\": \"90Thicanerv!\",\n  \"grant_type\": \"password\",\n  \"client_id\": \"RRrn6uIxalR_QaHFlcKOqbjHMG63elEdPTair9B9YdY\",\n  \"client_secret\": \"Sa8IGIh_HpVK1ZLAF0iFf7jU760osaUNV659pBIZR00\"\n}"
		headers = { 'Content-Type': "application/json" }

		conn.request("POST", "/oauth/token", payload.encode("utf-8"), headers)

		res = conn.getresponse()
		data = res.read()

		session = json.loads(data.decode("utf-8"))

		# print(session["token_type"])

		#save session
		app.redis.set(
        "{}:{}".format(
            session["token_type"],
            session["access_token"]
        ),
        json.dumps(session),
        ex=14400
    	)

		return session

	def put(self, **kwargs):
		conn = http.client.HTTPSConnection("service-chat.qontak.com")
		payload = "-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"receive_message_from_agent\"\r\n\r\nfalse\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"receive_message_from_customer\"\r\n\r\ntrue\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"status_message\"\r\n\r\nfalse\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"url\"\r\n\r\n110916958676428\r\n-----011000010111000001101001--\r\n"

		headers = {
		    'Content-Type': "multipart/form-data; boundary=---011000010111000001101001",
		    'Authorization': "eMw6R7CM6B6jHUdVMVqvpULdqDOYDRfosjyG6DA6zBw"
		}

		conn.request("PUT", "/api/open/v1/message_interactions", payload, headers)

		res = conn.getresponse()
		data = res.read()

		result = json.loads(data.decode("utf-8"))

		return result

	def post(self, **kwargs): 
		return True
