from neo4j import GraphDatabase, basic_auth
from py2neo import Graph, NodeMatcher
from textblob import TextBlob

# Connect to Neo4j graph database
graph = Graph("bolt://localhost:50585", auth=("neo4j", "1234567890"))

# Get node matcher for efficient node querying
matcher = NodeMatcher(graph)

# Function to extract hashtags and usernames from text
def extract_entities(text):
    entities = {'hashtags': [], 'usernames': []}
    for word in text.split():
        if word.startswith('#'):
            entities['hashtags'].append(word[1:])
        elif word.startswith('@'):
            entities['usernames'].append(word[1:])
    return entities

# Function to get sentiment polarity from text
def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

# Function to get similar users based on hashtags and sentiment
def get_similar_users(user_id, hashtags):
    query = '''
        MATCH (u1:User)-[:POSTED]->(:Tweet)-[:TAGGED]->(h:Hashtag)
        WHERE ID(u1) = $user_id AND h.name IN $hashtags
        WITH DISTINCT u1
        MATCH (u1)-[:POSTED]->(t:Tweet)<-[:POSTED]-(u2:User)
        WITH DISTINCT u1, u2, COUNT(DISTINCT t) AS common_tweets
        WHERE SIZE([(u1)-[:POSTED]->(t)<-[:POSTED]-(u) WHERE ID(u) = ID(u2) | NULL]) = 0
        WITH DISTINCT u2, common_tweets
        ORDER BY common_tweets DESC
        LIMIT 10
        RETURN COLLECT(ID(u2)) AS user_ids
    '''
    result = graph.run(query, user_id=user_id, hashtags=hashtags).data()
    if result:
        return result[0]['user_ids']
    else:
        return []

# Function to get similar tweets based on sentiment and content
def get_similar_tweets(user_id):
    query = '''
        MATCH (u:User)-[:POSTED]->(t1:Tweet)
        WHERE ID(u) = $user_id
        WITH t1
        MATCH (t1)-[:TAGGED]->(h:Hashtag)<-[:TAGGED]-(t2:Tweet)
        WHERE ID(t1) <> ID(t2)
        WITH t2, COUNT(DISTINCT h) AS common_hashtags
        ORDER BY common_hashtags DESC
        LIMIT 10
        RETURN COLLECT(ID(t2)) AS tweet_ids
    '''
    result = graph.run(query, user_id=user_id).data()
    if result:
        return result[0]['tweet_ids']
    else:
        return []

# Function to get recommended tweets and users for a given user
def get_recommendations(user_id):
        
    # Get user's posted tweets and sentiment
    user = matcher.match('User', id=user_id).first()
    if user is None:
        return [], []
    
    # Get user's posted tweets and sentiment
    posted_tweets = user.get_related_nodes('POSTED', 'Tweet')
    sentiment = sum([get_sentiment(tweet['text']) for tweet in posted_tweets]) / len(posted_tweets)

    # Get hashtags and usernames from user's tweets
    hashtags = []
    usernames = []
    for tweet in posted_tweets:
        entities = extract_entities(tweet['text'])
        hashtags.extend(entities['hashtags'])
        usernames.extend(entities['usernames'])

    # Get similar users based on hashtags and sentiment
    similar_users = get_similar_users(user_id, hashtags)
    tweets_to_recommend = []

    # Aggregate similar users' tweets and exclude user's posted tweets
    for similar_user_id in similar_users:
        similar_user = matcher.match('User', id=similar_user_id).first()
        similar_user_tweets = similar_user.get_related_nodes('POSTED', 'Tweet')
        for tweet in similar_user_tweets:
            if tweet not in posted_tweets:
                tweets_to_recommend.append(tweet)

    # Get similar tweets based on sentiment and content
    similar_tweets = get_similar_tweets(user_id)

    # Aggregate similar tweets and exclude user's posted tweets
    for tweet_id in similar_tweets:
        tweet = matcher.match('Tweet', id=tweet_id).first()
        if tweet not in posted_tweets:
            tweets_to_recommend.append(tweet)

    # Get recommended hashtags and users from recommended tweets
    recommended_hashtags = []
    recommended_users = []
    for tweet in tweets_to_recommend:
        entities = extract_entities(tweet['text'])
        recommended_hashtags.extend(entities['hashtags'])
        recommended_users.extend(entities['usernames'])

    # Remove duplicates and return top 10 recommended hashtags and users
    recommended_hashtags = list(set(recommended_hashtags))
    recommended_users = list(set(recommended_users))
    return recommended_hashtags[:10], recommended_users[:10]

# Example usage
user = matcher.match('User', username='hillary006').first()
hashtags, users = get_recommendations(user)
print(f"Recommended hashtags for user {user['username']}: {hashtags}")
print(f"Recommended users for user {user['username']}: {users}")