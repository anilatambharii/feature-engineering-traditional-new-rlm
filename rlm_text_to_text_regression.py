# rlm_text_to_text_regression.py

from confluent_kafka import Consumer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import json
import torch

# Kafka consumer setup
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'ml-rlm-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['mlops-realtime-topic'])

# Load pretrained Regression Language Model (replace with actual model name)
tokenizer = AutoTokenizer.from_pretrained("google/regress-lm")
model = AutoModelForSeq2SeqLM.from_pretrained("google/regress-lm")

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
        # Convert incoming data to structured text (YAML/JSON-like)
        system_state = f"""
cell: {data.get('cell', 'unknown')}
timestamp: {data.get('timestamp', 'unknown')}
hardware:
  - type: {data.get('hardware_type', 'unknown')}
    cores: {data.get('cores', 0)}
    memory_gb: {data.get('memory_gb', 0)}
jobs:
  - id: {data.get('job_id', 'unknown')}
    cpu_request: {data.get('cpu_request', 0)}
    memory_gb: {data.get('job_memory_gb', 0)}
    priority: {data.get('priority', 'normal')}
scheduler_params:
  bin_packing_algo: {data.get('bin_packing_algo', 'v1')}
  max_jobs: {data.get('max_jobs', 0)}
"""

        inputs = tokenizer(system_state, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=10)
        predicted_efficiency = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Predicted Efficiency: {predicted_efficiency}")
finally:
    consumer.close()
