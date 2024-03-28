from neo4j_utils import get_users_tweets_dict, get_hashtags_tweets_dict
from neo4j import GraphDatabase, basic_auth
import logging

# Import the users and hashtags tweets dictionaries
users_tweets = get_users_tweets_dict()
hashtags_tweets = get_hashtags_tweets_dict()

# Initialize the driver
uri = "bolt://localhost:64048"
driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "1234567890"))

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG
)

def collaborative_filtering_recommendation(user_id):
    with driver.session() as session:
        result = session.run("MATCH (u:User {name: $user_id})-[:POSTED]->(t:Tweet)-[:TAGGED]->(h:Hashtag)<-[:TAGGED]-(t2:Tweet)-[:POSTED]->(u2:User) WHERE u <> u2 WITH u2, count(DISTINCT h) as common_hashtags ORDER BY common_hashtags DESC RETURN u2.name, common_hashtags LIMIT 10", user_id=user_id)
    return [(user, similarity) for user, similarity in result.records()]

def content_based_filtering_recommendation(hashtag):
    with driver.session() as session:
        result = session.run("MATCH (h:Hashtag {name: $hashtag})<-[:TAGGED]-(t:Tweet) WHERE EXISTS(t.sentiment) RETURN t.text, t.sentiment ORDER BY t.sentiment DESC LIMIT 10", hashtag=hashtag)
    return [(tweet, sentiment) for tweet, sentiment in result.records()]
