# traditional_feature_engineering.py

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from confluent_kafka import Consumer
import json

# Kafka consumer setup
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092', #replace this with your server 
    'group.id': 'ml-feature-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['mlops-realtime-topic'])

# Placeholder for real-time feature collection
features = []
labels = []

print("Listening for real-time data...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        data = json.loads(msg.value().decode('utf-8'))
        # Example: Extract features from incoming data
        feature_vector = [
            data.get('cpu_utilization', 0),
            data.get('memory_usage', 0),
            data.get('job_count', 0),
            data.get('hardware_type', 0),  # Assume already encoded
            data.get('hour_of_day', 0)
        ]
        label = data.get('efficiency_metric', 0)
        features.append(feature_vector)
        labels.append(label)

        # For demonstration, train after collecting 100 samples
        if len(features) >= 100:
            X = pd.DataFrame(features, columns=[
                "cpu_utilization", "memory_usage", "job_count", "hardware_type", "hour_of_day"
            ])
            y = pd.Series(labels)
            model = RandomForestRegressor()
            model.fit(X, y)
            print("Trained model on 100 real-time samples.")
            break
finally:
    consumer.close()
