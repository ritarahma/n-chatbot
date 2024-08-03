import http.client
from flask_restful import Resource
from flask import current_app as app, request
import json

class ChatResources(Resource):

	def post(self, **kwargs): 
		conn = http.client.HTTPSConnection("service-chat.qontak.com")

		payload = "{\n  \"to_name\": \"Rita Rahmawati\",\n  \"to_number\": \"628987912883\",\n  \"message_template_id\": \"3fe599f6-2fb7-4596-8993-4491c421319a\",\n  \"channel_integration_id\": \"b0bdbb6a-1608-4d1a-8bc1-a0eac8b792f6\",\n  \"language\": {\n    \"code\": \"en\"\n  },\n  \"parameters\": {\n    \"header\": {\n      \"format\": \"DOCUMENT\",\n      \"params\": [\n        {\n          \"key\": \"url\",\n          \"value\": \"https://qontak-hub-development.s3.amazonaws.com/uploads/direct/files/01417dc5-9cd1-40b7-8900-d8b9fd6f250e/sample.pdf\"\n        },\n        {\n          \"key\": \"filename\",\n          \"value\": \"sample.pdf\"\n        }\n      ]\n    },\n    \"body\": [\n      {\n        \"key\": \"1\",\n        \"value_text\": \"Lorem Ipsum\",\n        \"value\": \"customer_name\"\n      }\n    ],\n    \"buttons\": [\n      {\n        \"index\": \"0\",\n        \"type\": \"url\",\n        \"value\": \"paymentUniqNumber\"\n      }\n    ]\n  }\n}"

		headers = {
		    'Content-Type': "application/json",
		    'Authorization': "Bearer Authorization: Bearer eMw6R7CM6B6jHUdVMVqvpULdqDOYDRfosjyG6DA6zBw"
		}

		conn.request("POST", "/api/open/v1/broadcasts/whatsapp/direct", payload, headers)

		res = conn.getresponse()
		data = res.read()

		result = json.loads(data.decode("utf-8"))

		return result
