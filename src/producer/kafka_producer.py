from kafka import KafkaProducer
import json

# Khởi tạo producer Kafka
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic_name = 'loan_data'

def send_to_kafka(data: dict):
    producer.send(topic_name, value=data)
    producer.flush()
