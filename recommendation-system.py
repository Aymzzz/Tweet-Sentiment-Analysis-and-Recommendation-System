import threading
from kafka import KafkaConsumer, KafkaProducer
from neo4j import GraphDatabase, basic_auth
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob

# Graph Database Configuration
uri = "bolt://localhost:50585"
driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "1234567890"))

# Kafka Configuration
bootstrap_servers = ['localhost:9092']
consumer = KafkaConsumer('twitter-text', bootstrap_servers=bootstrap_servers)
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

# Content-Based Filtering Configuration
vectorizer = TfidfVectorizer()

# Collaborative Filtering Configuration
SIMILAR_USERS_LIMIT = 5

def insert_tweet_to_neo4j(session, text, hashtags, usernames, sentiment):
    # Insert tweet into Neo4j
    session.run(
        "CREATE (t:Tweet {text: $text, hashtags: $hashtags, usernames: $usernames, sentiment: $sentiment})",
        text=text, hashtags=hashtags, usernames=usernames, sentiment=sentiment
    )

    if hashtags is not None:
        for hashtag in hashtags:
            # Create or update hashtag nodes in Neo4j
            session.run("MERGE (h:Hashtag {name: $name})", name=hashtag)
            # Create TAGGED relationships between tweet and hashtag
            session.run(
                "MATCH (t:Tweet {text: $text}), (h:Hashtag {name: $name}) CREATE (t)-[:TAGGED]->(h)",
                text=text, name=hashtag
            )

    if usernames is not None:
        for username in usernames:
            # Create or update user nodes in Neo4j
            session.run("MERGE (u:User {name: $name})", name=username)
            # Create MENTIONED relationships between tweet and user
            session.run(
                "MATCH (t:Tweet {text: $text}), (u:User {name: $name}) CREATE (t)-[:MENTIONED]->(u)",
                text=text, name=username
            )

def update_tweet_sentiment(session, text, sentiment):
    session.run("MATCH (t:Tweet {text: $text}) SET t.sentiment = $sentiment", text=text, sentiment=sentiment)

def get_user_interests(session, username):
    result = session.run(
        "MATCH (u:User {name: $username})-[:MENTIONED]->(t:Tweet) RETURN t.hashtags",
        username=username
    )
    hashtags = []
    for record in result:
        tweet_hashtags = record["t.hashtags"]
        if tweet_hashtags is not None:
            hashtags.extend(tweet_hashtags)
    return hashtags

def get_similar_users(session, username):
    result = session.run(
        "MATCH (u1:User {name: $username})-[:MENTIONED]->(t:Tweet)<-[:MENTIONED]-(u2:User) "
        "WHERE u1 <> u2 "
        "RETURN DISTINCT u2.name AS similar_user "
        "LIMIT $limit",
        username=username,
        limit=SIMILAR_USERS_LIMIT
    )
    similar_users = [record["similar_user"] for record in result]
    return similar_users

def get_recommendations(username):
    with driver.session() as session:
        user_interests = get_user_interests(session, username)
        similar_users = get_similar_users(session, username)

        # Content-Based Filtering
        vectorizer.fit(user_interests)
        user_interests_vector = vectorizer.transform([user_interests])
        tweet_hashtags_vectors = session.run(
            "MATCH (h:Hashtag)<-[:TAGGED]-(t:Tweet) RETURN h.name AS hashtag, t.hashtags AS hashtags"
        )
        content_based_scores = {}
        for record in tweet_hashtags_vectors:
            hashtag = record["hashtag"]
            hashtags = record["hashtags"]
            if hashtags is not None:
                hashtags_vector = vectorizer.transform([hashtags])
                similarity_scores = cosine_similarity(user_interests_vector, hashtags_vector)
                content_based_scores[hashtag] = similarity_scores[0][0]

        # Collaborative Filtering
        collaborative_scores = {}
        for similar_user in similar_users:
            user_tweets = session.run(
                "MATCH (u:User {name: $username})-[:MENTIONED]->(t:Tweet) RETURN t.hashtags AS hashtags",
                username=similar_user
            )
            for record in user_tweets:
                hashtags = record["hashtags"]
                if hashtags is not None:
                    for hashtag in hashtags:
                        if hashtag not in collaborative_scores:
                            collaborative_scores[hashtag] = 0
                        collaborative_scores[hashtag] += 1

        # Combine Content-Based and Collaborative Filtering Scores
        combined_scores = {}
        for hashtag in set(list(content_based_scores.keys()) + list(collaborative_scores.keys())):
            content_based_score = content_based_scores.get(hashtag, 0)
            collaborative_score = collaborative_scores.get(hashtag, 0)
            combined_score = content_based_score + collaborative_score
            combined_scores[hashtag] = combined_score

        # Sort the recommendations by combined score in descending order
        recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        return recommendations

def process_tweet(message):
    value = message.value.decode('utf-8')
    tweet = json.loads(value)
    text = tweet['text']
    hashtags = tweet['hashtags']
    usernames = tweet['usernames']
    sentiment = tweet['sentiment']

    with driver.session() as session:
        insert_tweet_to_neo4j(session, text, hashtags, usernames, sentiment)
        update_tweet_sentiment(session, text, sentiment)

    print(f"Processed tweet: {text}")

def run_consumer():
    for message in consumer:
        process_tweet(message)

def run_producer():
    with driver.session() as session:
        result = session.run("MATCH (t:Tweet) RETURN t.text, t.hashtags, t.usernames")
        count = 0
        for record in result:
            text = record["t.text"]
            hashtags = record["t.hashtags"]
            usernames = record["t.usernames"]
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity
            message = {
                "text": text,
                "hashtags": hashtags,
                "usernames": usernames,
                "sentiment": sentiment
            }
            value_bytes = json.dumps(message, ensure_ascii=False).encode('utf-8')
            producer.send('twitter-text', value=value_bytes)
            if hashtags is not None:
                for hashtag in hashtags:
                    producer.send('twitter-hashtags', value=hashtag.encode('utf-8'))
            if usernames is not None:
                for username in usernames:
                    producer.send('twitter-usernames', value=username.encode('utf-8'))

            # Publish sentiment data to the 'twitter-sentiment' topic
            producer.send('twitter-sentiment', value=json.dumps({"sentiment": sentiment}).encode('utf-8'))

            update_tweet_sentiment(session, text, sentiment)

            count += 1
            print(f"Sent message {count}: {message}")

    producer.flush()
    producer.close()

if __name__ == '__main__':
    # Start consumer and producer in separate threads or processes
    consumer_thread = threading.Thread(target=run_consumer)
    producer_thread = threading.Thread(target=run_producer)

    consumer_thread.start()
    producer_thread.start()

    consumer_thread.join()
    producer_thread.join()

    driver.close()