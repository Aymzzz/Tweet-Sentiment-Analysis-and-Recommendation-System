# Tweet-Sentiment-Analysis-and-Recommendation-System

This README file provides an overview of the code and instructions for running the different components of the system.

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

## Additional Notes

- You can modify the `config.py` file to change the Kafka and Neo4j configuration parameters if needed.

- The `data` directory contains sample tweet data in CSV format that can be used to populate the Neo4j database. You can modify this data or provide your own data in the same format.

- The `models` directory contains the pre-trained sentiment analysis model used by TextBlob. You can replace this model file with your own if desired.

- The recommendation system uses collaborative filtering and content-based recommendation techniques as examples. You can modify and extend these techniques or implement other recommendation algorithms as per your requirements.

- The system is provided as a starting point and may require further customization and optimization depending on your specific use case.

- This system is a simplified demonstration and may not include all the features and considerations required for a production-level application. Please use it as a reference and adapt it to meet your specific needs.

## How to run flask 
* virtualenv env
* env\Scripts\activate.bat
* then you can install and run whaterver you need inside the virtual enviorment 