from neo4j import GraphDatabase, basic_auth

uri = "bolt://localhost:64048"
driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "1234567890"))

def get_users_tweets_dict():
    with driver.session() as session:
        result = session.run("MATCH (u:User)-[:POSTED]->(t:Tweet) RETURN u.name, collect(DISTINCT t.text) as tweets ORDER BY u.name")
        users_tweets = {}
        for record in result:
            user = record['u.name']
            tweets = record['tweets']
            users_tweets[user] = tweets
        # Consume the result
        result.consume()
        return users_tweets

def get_hashtags_tweets_dict():
    with driver.session() as session:
        result = session.run("MATCH (h:Hashtag)<-[:TAGGED]-(t:Tweet) RETURN h.name, collect(DISTINCT t.text) as tweets ORDER BY h.name")
        hashtags_tweets = {}
        for record in result:
            hashtag = record['h.name']
            tweets = record['tweets']
            hashtags_tweets[hashtag] = tweets
        # Consume the result
        result.consume()
        return hashtags_tweets