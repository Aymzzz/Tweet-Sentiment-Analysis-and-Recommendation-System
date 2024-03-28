from neo4j import GraphDatabase, basic_auth

uri = "bolt://localhost:64048"
driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "1234567890"))

def get_users_tweets_dict():
    with driver.session() as session:
        result = session.run("MATCH (u:User)-[:POSTED]->(t:Tweet) RETURN u.name, collect(t.text) as tweets, collect(t.sentiment) as sentiments")
    users_tweets = {}
    for record in result:
        user_id = record['u.name']
        tweets = [tweet for tweet in record['tweets']]
        sentiments = [sentiment for sentiment in record['sentiments']]
        users_tweets[user_id] = (tweets, sentiments)
    return users_tweets

def get_hashtags_tweets_dict():
    with driver.session() as session:
        result = session.run("MATCH (h:Hashtag)<-[:TAGGED]-(t:Tweet) RETURN h.name, collect(t.text) as tweets, collect(t.sentiment) as sentiments")
    hashtags_tweets = {}
    for record in result:
        hashtag = record['h.name']
        tweets = [tweet for tweet in record['tweets']]
        sentiments = [sentiment for sentiment in record['sentiments']]
        hashtags_tweets[hashtag] = (tweets, sentiments)
    return hashtags_tweets