from flask import Flask, request, jsonify
from kafka import KafkaProducer
from neo4j import GraphDatabase, basic_auth
import json
from textblob import TextBlob
from recommendation_system import collaborative_filtering_recommendation, content_based_filtering_recommendation
from neo4j_utils import get_hashtags_tweets_dict

app = Flask(__name__)

uri = "bolt://localhost:64048"

driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "1234567890"))

bootstrap_servers = ['localhost:9092']

producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

@app.route('/new_tweet', methods=['POST'])
def new_tweet():
    # Parse the new tweet data from the request
    data = request.json
    tweet_text = data.get('text')
    usernames = data.get('usernames')
    hashtags = data.get('hashtags')
    mentions = data.get('mentions')

    # Check if the 'text' and 'usernames' parameters are null or missing
    if tweet_text is None:
        return jsonify({'error': 'Text parameter is missing or null'}), 400
    if usernames is None:
        return jsonify({'error': 'Usernames parameter is missing or null'}), 400

    # Insert the new tweet data into the graph database
    with driver.session() as session:
        session.run("""\
            MERGE (t:Tweet {text: $text})
            WITH t
            UNWIND $usernames AS username
            MERGE (u:User {name: username})
            MERGE (u)-[:POSTED]->(t)
            SET t.usernames = COALESCE(t.usernames, []) + username
            SET t.hashtags = COALESCE(t.hashtags, []) + $hashtags
            SET t.mentions = COALESCE(t.mentions, []) + $mentions
        """, text=tweet_text, usernames=usernames, hashtags=hashtags, mentions=mentions)
        result = session.run("MATCH (t:Tweet {text: $text}) RETURN t", text=tweet_text)
        tweet = result.single()[0]
        print(f"Updated tweet: {tweet}")

    # Stream the new tweet data to the Kafka producer
    message = {
        "text": tweet_text,
        "hashtags": hashtags,
        "usernames": usernames,
        "mentions": mentions,
        "sentiment": None
    }

    value_bytes = json.dumps(message, ensure_ascii=False).encode('utf-8')
    producer.send('twitter-text', value=value_bytes)
    if hashtags is not None:
        for hashtag in hashtags:
            producer.send('twitter-hashtags', value=hashtag.encode('utf-8'))
    if mentions is not None:
        for mention in mentions:
            producer.send('twitter-usernames', value=mention.encode('utf-8'))

    # Perform sentiment analysis on the new tweet data
    blob = TextBlob(tweet_text)
    sentiment = blob.sentiment.polarity

    # Stream the sentiment data to the Kafka producer and update the sentiment data in the graph database
    producer.send('twitter-sentiment', value=json.dumps({"sentiment": sentiment}).encode('utf-8'))
    with driver.session() as session:
        session.run("""
            MATCH (t:Tweet {text: $text})
            SET t.sentiment = $sentiment
        """, text=tweet_text, sentiment=sentiment)
    
    print("========================================================================",usernames[0])    

    # Get the recommended hashtags and users based on the new tweet data
    hashtags_tweets_dict = get_hashtags_tweets_dict()
    if hashtags is not None and len(hashtags) > 0:
        similar_tweets = content_based_filtering_recommendation(hashtags[0], hashtags_tweets_dict)
    else:
        similar_tweets = []
    
    recommended_users = collaborative_filtering_recommendation(usernames[0])

    # Return the recommended hashtags, users, and sentiment as a response
    response = {
        "similar_tweets": similar_tweets,
        "recommended_users": recommended_users,
        "sentiment": sentiment
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)