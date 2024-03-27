from flask import Flask, render_template, request
from kafka import KafkaProducer, KafkaConsumer
import json

app = Flask(__name__)

bootstrap_servers = ['localhost:9092']
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

consumer = KafkaConsumer('recommendations',
                         bootstrap_servers=bootstrap_servers,
                         auto_offset_reset='earliest',
                         enable_auto_commit=True)

def send_tweet_to_kafka(tweet):
    message = {
        "text": tweet
    }
    producer.send('tweets', value=json.dumps(message).encode('utf-8'))

def get_recommendations():
    recommendations = []
    for message in consumer:
        recommendation = message.value.decode('utf-8')
        recommendations.append(recommendation)
        if len(recommendations) >= 10:
            break
    return recommendations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_tweet', methods=['POST'])
def submit_tweet():
    tweet = request.form['tweet']
    send_tweet_to_kafka(tweet)
    recommendations = get_recommendations()
    return render_template('recommendations.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
