from flask import Flask, jsonify
import requests
import json
from kafka import KafkaProducer
import os
app = Flask(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")  
API_KEY = os.getenv("API_KEY", "your_default_fallback_key")  
TOPIC = "weather_topic"
CITY = "London"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def fetch_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"
    response = requests.get(url)
    return response.json()

@app.route("/weather", methods=["GET"])
def get_weather():
    """Fetch weather data from OpenWeatherMap."""
    weather_data = fetch_weather()
    return jsonify(weather_data)

@app.route("/publish-weather", methods=["POST"])
def publish_weather():
    """Fetch weather data and publish it to Kafka."""
    try:
        weather_data = fetch_weather()
        print(f"Fetched weather data: {weather_data}")  # Log the fetched data
        producer.send(TOPIC, weather_data)
        producer.flush()  # Ensure the message is actually sent
        print(f"Weather data sent to Kafka topic {TOPIC}")
        return jsonify({"message": "Weather data published to Kafka"})
    except Exception as e:
        print(f"Error in publishing weather data: {e}")  # Log the error message
        return jsonify({"error": str(e)}), 500  # Return the error message in the response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

##