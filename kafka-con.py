from kafka import KafkaConsumer
from neo4j import GraphDatabase, basic_auth
from textblob import TextBlob
import json

uri = "bolt://localhost:50585"
driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "1234567890"))

bootstrap_servers = ['localhost:9092']
consumer = KafkaConsumer('twitter-text', 'twitter-hashtags', 'twitter-usernames', 'twitter-sentiment',
                         bootstrap_servers=bootstrap_servers, auto_offset_reset='earliest', enable_auto_commit=True)

for message in consumer:
    topic = message.topic
    value = message.value.decode('utf-8')
    value = json.loads(value)

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