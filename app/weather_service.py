from flask import Flask, jsonify
import requests
import json
from kafka import KafkaProducer
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # This will log all messages at DEBUG level and higher
logger = logging.getLogger(__name__)

app = Flask(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
API_KEY = os.getenv("API_KEY", "your_default_fallback_key")
TOPIC = "weather_topic"
CITY = "London"

# Set up Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def fetch_weather():
    """Fetch weather data from OpenWeatherMap API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"
    try:
        logger.debug(f"Making API request to {url}")  # Log the API request
        response = requests.get(url)
        response.raise_for_status()  # Will raise an error if the status code is not 200
        weather_data = response.json()
        logger.debug(f"Received weather data: {weather_data}")  # Log the fetched data
        return weather_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data: {e}")  # Log the error if any
        return None

@app.route("/weather", methods=["GET"])
def get_weather():
    """Fetch and return weather data."""
    weather_data = fetch_weather()
    if weather_data:
        return jsonify(weather_data)
    return jsonify({"error": "Failed to fetch weather data"}), 500

@app.route("/publish-weather", methods=["POST"])
def publish_weather():
    """Fetch weather data and send it to Kafka."""
    try:
        weather_data = fetch_weather()
        if weather_data:
            logger.debug(f"Publishing weather data to Kafka: {weather_data}")  # Log the data being sent
            producer.send(TOPIC, weather_data)
            producer.flush()  # Ensure the message is sent before returning
            logger.info(f"Weather data successfully sent to Kafka topic {TOPIC}")  # Log success
            return jsonify({"message": "Weather data published to Kafka"})
        else:
            logger.error("No weather data to send to Kafka.")  # Log the failure to fetch data
            return jsonify({"error": "Failed to fetch weather data"}), 500
    except Exception as e:
        logger.error(f"Error while publishing weather data: {e}")  # Log the error in case of failure
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting weather-service on port 5001")  # Log when the service starts
    app.run(host="0.0.0.0", port=5001, debug=True)
