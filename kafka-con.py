from kafka import KafkaConsumer
from neo4j import GraphDatabase, basic_auth
from textblob import TextBlob
import json

uri = "bolt://localhost:50585"
driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "1234567890"))

<<<<<<< HEAD
bootstrap_servers = ['localhost:9092']
consumer = KafkaConsumer('twitter-text', 'twitter-hashtags', 'twitter-usernames', 'twitter-sentiment',
                         bootstrap_servers=bootstrap_servers, auto_offset_reset='earliest', enable_auto_commit=True)

for message in consumer:
    topic = message.topic
    value = message.value.decode('utf-8')
    value = json.loads(value)
=======
def get_recommendations(username):
    with driver.session() as session:
        # Collaborative filtering: find similar users based on tweet history
        similar_users = session.run("""
            MATCH (u1:User)-[:POSTED]->(t:Tweet)<-[:POSTED]-(u2:User)
            WHERE u1.name = $username AND u2.name <> $username
            WITH u2, COUNT(DISTINCT t) AS common_tweets
            ORDER BY common_tweets DESC LIMIT 10
            RETURN u2
        """, username=username)

        # Content-based filtering: find hashtags or users that similar users have interacted with
        recommendations = session.run("""
            MATCH (u:User)-[:POSTED]->(t:Tweet)-[:HAS_TAG]->(h:Hashtag)
            WHERE u IN $similar_users OR u.name = $username
            WITH h, COUNT(DISTINCT t) AS common_tweets
            ORDER BY common_tweets DESC LIMIT 10
            RETURN h.name as recommendation
        """, similar_users=[u['u2']['name'] for u in similar_users], username=username)

        return [rec['recommendation'] for rec in recommendations]

consumer = KafkaConsumer('tweets',
                         bootstrap_servers=['localhost:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True)

producer = KafkaProducer(bootstrap_servers='localhost:9092')

for message in consumer:
    tweet = json.loads(message.value.decode('utf-8'))
    username = tweet['username'] # Use the 'name' field instead of 'id'
    recommendations = get_recommendations(username)
>>>>>>> cc67cd3b847d471043023f27d9c654b2eb3d7b27

    if topic == 'twitter-text':
        text = value['text']
        hashtags = value['hashtags']
        usernames = value['usernames']
        sentiment = value['sentiment']

        with driver.session() as session:
            tx = session.begin_transaction()
            tweet = tx.run("MERGE (t:Tweet {id: $id}) "
                           "ON CREATE SET t.text = $text, t.sentiment = $sentiment "
                           "WITH t RETURN t", id=message.offset, text=text, sentiment=sentiment).single().value()

            for hashtag in hashtags:
                tx.run("MERGE (h:Hashtag {name: $name}) WITH h, $tweet AS t MERGE (t)-[:TAGGED]->(h)",
                       name=hashtag, tweet=tweet)

            for username in usernames:
                tx.run("MERGE (u:User {name: $name}) WITH u, $tweet AS t MERGE (t)-[:MENTIONED]->(u)",
                       name=username, tweet=tweet)

            tx.commit()

    elif topic == 'twitter-hashtags':
        with driver.session() as session:
            tx = session.begin_transaction()
            hashtag = value
            tx.run("MERGE (h:Hashtag {name: $name})", name=hashtag)
            tx.commit()

    elif topic == 'twitter-usernames':
        with driver.session() as session:
            tx = session.begin_transaction()
            username = value
            tx.run("MERGE (u:User {name: $name})", name=username)
            tx.commit()

    elif topic == 'twitter-sentiment':
        sentiment = value['sentiment']
        with driver.session() as session:
            tx = session.begin_transaction()
            tx.run("MATCH (t:Tweet {id: $id}) SET t.sentiment = $sentiment", id=message.offset, sentiment=sentiment)
            tx.commit()

consumer.close()
driver.close()