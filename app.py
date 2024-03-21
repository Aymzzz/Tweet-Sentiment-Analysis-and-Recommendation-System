from flask import Flask, render_template, request, jsonify
from kafka import KafkaProducer, KafkaConsumer
import json

app = Flask(__name__)

# Kafka producer setup
bootstrap_servers = ['localhost:9092']
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

# Kafka consumer setup
consumer = KafkaConsumer('recommendations',
                         bootstrap_servers=bootstrap_servers,
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id='my-group')

# Function to send tweet data to Kafka
def send_tweet_to_kafka(tweet_data):
    producer.send('tweets', json.dumps(tweet_data).encode('utf-8'))

# Function to get recommendations from Kafka consumer
def get_recommendations():
    recommendations = []
    for message in consumer:
        rec = message.value.decode('utf-8')
        recommendations.append(rec)
    return recommendations

# Route for posting tweets
@app.route('/post_tweet', methods=['POST'])
def post_tweet():
    tweet_data = request.json
    send_tweet_to_kafka(tweet_data)
    return jsonify({'message': 'Tweet submitted successfully'})

# Route for displaying recommendations
@app.route('/recommendations', methods=['GET'])
def display_recommendations():
    recommendations = get_recommendations()
    return jsonify({'recommendations': recommendations})

# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
