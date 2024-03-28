# Tweet-Sentiment-Analysis-and-Recommendation-System

This project aims to develop a scalable graph-based recommendation system for Twitter-like users. The system provides recommendations in the form of hashtags to browse and users to follow. A front-end web application allows users to post tweets, which are then processed by an underlying graph database. Simultaneously, the tweets are streamed for near real-time sentiment analysis using natural language processing (NLP). The sentiment analysis results are used to refine the recommendations provided to the users.

## Project Overview
The main focus of this project is to build a scalable pipeline rather than developing a sophisticated web application. The web application serves as a user interface for posting tweets, while the recommendations and sentiment analysis form the core components of the system. The recommendations are generated based on the hashtags and users present in the user tweets, and the sentiment analysis results are used to enhance the recommendations.

## System Components

The system consists of several Python scripts and commands to set up and run the components. Here is a brief description of each component:

1. `neo4j-data.py`: This script inserts tweets and their associated nodes and relationships into a Neo4j graph database.

2. `kafka-pro.py`: This script retrieves tweets from the Neo4j database, performs sentiment analysis using TextBlob, and publishes the tweet data and sentiment analysis results to Kafka topics.

3. `kafka-con.py`: This script consumes the sentiment analysis results from the Kafka topic and updates the sentiment values for the corresponding tweets in the Neo4j database.

4. `neo4j_utils.py`: This module contains utility functions for retrieving users' tweets and hashtags' tweets from the Neo4j database.

5. `Recommendation-system.py`: This script demonstrates two types of recommendations: collaborative filtering-based recommendation and content-based recommendation.

## Prerequisites

Before running the system, please ensure you have the following prerequisites installed:

1. Kafka: Install and set up Kafka on your local machine. You can download Kafka from the official website: [https://kafka.apache.org/downloads](https://kafka.apache.org/downloads).

2. Neo4j: Install and set up Neo4j on your local machine. You can download Neo4j from the official website: [https://neo4j.com/download](https://neo4j.com/download).

3. Python: Install Python 3.x on your machine. You can download Python from the official website: [https://www.python.org/downloads](https://www.python.org/downloads).

4. Python packages: Install the required Python packages by running the following command:
   ```
   pip install neo4j kafka-python textblob pandas tqdm
   ```

## Setup and Configuration

1. Start ZooKeeper and Kafka servers:
   - Open a command prompt or terminal.
   - Navigate to the Kafka installation directory.
   - Run the following command to start ZooKeeper:
     ```
     bin\windows\zookeeper-server-start.bat config\zookeeper.properties
     ```
   - Run the following command to start the Kafka server:
     ```
     bin\windows\kafka-server-start.bat config\server.properties
     ```

2. Create Kafka topics:
   - Open a command prompt or terminal.
   - Navigate to the Kafka installation directory.
   - Run the following commands to create the necessary Kafka topics:
     ```
     bin\windows\kafka-topics.bat --create --topic twitter-text --bootstrap-server localhost:9092
     bin\windows\kafka-topics.bat --create --topic twitter-hashtags --bootstrap-server localhost:9092
     bin\windows\kafka-topics.bat --create --topic twitter-usernames --bootstrap-server localhost:9092
     bin\windows\kafka-topics.bat --create --topic twitter-sentiment --bootstrap-server localhost:9092
     ```

3. Start the Neo4j graph database:
   - Open a command prompt or terminal.
   - Navigate to the Neo4j installation directory.
   - Run the following command to start the Neo4j database:
     ```
     neo4j start
     ```

4. Update Neo4j credentials:
   - Open the `neo4j-data.py`, `kafka-pro.py`, `kafka-con.py`, and `Recommendation-system.py` files in a text editor.
   - Locate the following line in each file:
     ```python
     uri = "bolt://localhost:64048"
     driver = GraphDatabase.driver(uri, auth=("neo4j", "1234567890"))
     ```
   - If your Neo4j database is using different credentials, update the `auth` parameter with the appropriate username and password.

## Running the System

1. Insert tweets into the Neo4j database:
   - Open a command prompt or terminal.
   - Navigate to the directory where `neo4j-data.py` is located.
   - Run the following command to insert tweets into the Neo4j database:
     ```
     python neo4j-data.py
     ```

2. Publish tweet data and sentiment analysis results to Kafka topics:
   - Open a command prompt or terminal.
   - Navigate to the directory where `kafka-pro.py` is located.
   - Run the following command to publish tweet data and sentiment analysis results to Kafka topics:
     ```
     python kafka-pro.py
     ```

3. Consume sentiment analysis results from Kafka topic and update Neo4j database:
   - Open a command prompt or terminal.
   - Navigate to the directory where `kafka-con.py` is located.
   - Run the following command to consume sentiment analysis results from the Kafka topic and update the Neo4j database:
     ```
     python kafka-con.py
     ```

4. Run the recommendation system:
   - Open a command prompt or terminal.
  ## Running the Recommendation System

To run the recommendation system, follow these steps:

1. Open a command prompt or terminal.

2. Navigate to the directory where `Recommendation-system.py` is located.

3. Run the following command to start the recommendation system:
   ```
   python Recommendation-system.py
   ```

4. The recommendation system will prompt you to choose the type of recommendation you want to try: collaborative filtering-based recommendation or content-based recommendation. Enter `1` or `2` accordingly.

5. If you choose collaborative filtering-based recommendation, the system will ask for a user ID. Enter the ID of the user for whom you want to get recommendations.

6. The system will display the recommended tweets for the user based on collaborative filtering.

7. If you choose content-based recommendation, the system will ask for a hashtag. Enter a hashtag for which you want to get recommendations.

8. The system will display the recommended tweets for the hashtag based on content-based recommendation.

9. You can continue to try different recommendations by following the prompts.

Note: Make sure the Neo4j database is running and has the necessary data inserted before running the recommendation system.

## How to run flask 
* virtualenv env
* env\Scripts\activate.bat
* then you can install and run whaterver you need inside the virtual enviorment 