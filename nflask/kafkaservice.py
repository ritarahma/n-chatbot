import json
from kafka import KafkaProducer
from config import KAFKA_BOOTSTRAP

producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def send_msg(topic,data):
    producer.send(topic,data)
