from kafka import KafkaConsumer
from neo4j import GraphDatabase, basic_auth
import json
from textblob import TextBlob

uri = "bolt://localhost:50585"
driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "1234567890"))

bootstrap_servers = ['localhost:9092']
consumer = KafkaConsumer('twitter-text', bootstrap_servers=bootstrap_servers)

def perform_sentiment_analysis(text):
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    return sentiment_score
try: 
    for message in consumer:
        value = message.value.decode('utf-8')
        tweet = json.loads(value)
        text = tweet['text']
        hashtags = tweet['hashtags']
        usernames = tweet['usernames']

        # Perform sentiment analysis on the tweet content
        sentiment_score = perform_sentiment_analysis(text)

        with driver.session() as session:
            # Insert tweet into Neo4j
            session.run(
                "MERGE (t:Tweet {text: $text}) SET t.sentiment = $sentiment",
                text=text, sentiment=sentiment_score
            )

            if hashtags is not None:
                for hashtag in hashtags:
                    # Create or update hashtag nodes in Neo4j
                    session.run("MERGE (h:Hashtag {name: $name})", name=hashtag)
                    # Create TAGGED relationships between tweet and hashtag
                    session.run(
                        "MATCH (t:Tweet {text: $text}), (h:Hashtag {name: $name}) MERGE (t)-[:TAGGED {name: 'TAGGED'}]->(h)",
                        text=text, name=hashtag
                    )

            if usernames is not None:
                for username in usernames:
                    # Create or update user nodes in Neo4j
                    session.run("MERGE (u:User {name: $name})", name=username)
                    # Create MENTIONED relationships between tweet and user
                    session.run(
                        "MATCH (t:Tweet {text: $text}), (u:User {name: $name}) MERGE (t)-[:MENTIONED {name: 'MENTIONED'}]->(u)",
                        text=text, name=username
                    )

        print(f"Processed tweet: {text}")
        
except Exception as e:
    print(f"Error occurred: {str(e)}")

driver.close()