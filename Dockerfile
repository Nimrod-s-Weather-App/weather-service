FROM python:3.10

# Set the working directory to /app inside the container
WORKDIR /app

# Copy the requirements.txt from the app folder to the container
COPY app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY app/ .

# Start the Flask app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5001", "weather_service:app"]
