from kafka import KafkaConsumer, KafkaProducer
from neo4j import GraphDatabase, basic_auth
import json
from textblob import TextBlob

driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", ""))

def get_recommendations(user_id):
    with driver.session() as session:
        # Collaborative filtering: find similar users based on tweet history
        similar_users = session.run("""
            MATCH (u1:User)-[:POSTED]->(t:Tweet)<-[:POSTED]-(u2:User)
            WHERE u1.id = $user_id AND u2.id <> $user_id
            WITH u2, COUNT(DISTINCT t) AS common_tweets
            ORDER BY common_tweets DESC LIMIT 10
            RETURN u2
        """, user_id=user_id)

        # Content-based filtering: find hashtags or users that similar users have interacted with
        recommendations = session.run("""
            MATCH (u:User)-[:POSTED]->(t:Tweet)-[:HAS_TAG]->(h:Hashtag)
            WHERE u IN $similar_users OR u.id = $user_id
            WITH h, COUNT(DISTINCT t) AS common_tweets
            ORDER BY common_tweets DESC LIMIT 10
            RETURN h.name as recommendation
        """, similar_users=[u['u2']['id'] for u in similar_users], user_id=user_id)

        return [rec['recommendation'] for rec in recommendations]

consumer = KafkaConsumer('tweets',
                         bootstrap_servers=['localhost:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True)

producer = KafkaProducer(bootstrap_servers='localhost:9092')

for message in consumer:
    tweet = json.loads(message.value.decode('utf-8'))
    user_id = tweet['user_id']
    recommendations = get_recommendations(user_id)

    #send recommendations to the user
    for rec in recommendations:
        producer.send('recommendations', rec.encode('utf-8'))

    #update sentiment data in Neo4j
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Tweet {id: $id})
            SET t.sentiment = $sentiment
        """, id=tweet['id'], sentiment=tweet['sentiment'])

    #send hashtags and usernames to separate Kafka topics
    if 'hashtags' in tweet:
        for hashtag in tweet['hashtags']:
            producer.send('hashtags', hashtag.encode('utf-8'))
    if 'usernames' in tweet:
        for username in tweet['usernames']:
            producer.send('usernames', username.encode('utf-8'))
