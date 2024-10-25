from flask import Flask, render_template, jsonify
from threading import Thread
import requests
import time
from datetime import datetime
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Configuration
API_KEY = '70ad56e90ce260d971fa52997d48a136'
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

DB_CONFIG = {
    'host': 'localhost',
    'database': 'weather_db',
    'user': 'root',
    'password': 'root',
    'sql_mode': 'NO_ENGINE_SUBSTITUTION'
}

# Template filters
@app.template_filter('format_datetime')
def format_datetime(value):
    """Convert timestamps to formatted datetime strings"""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    return str(value)

@app.template_filter('format_temp')
def format_temp(value):
    """Format temperature values to 2 decimal places"""
    return f"{value:.2f}"

# Database functions
def create_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''))")
        connection.commit()
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def create_tables(connection):
    cursor = connection.cursor()
    
    # Weather data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        city VARCHAR(50),
        main VARCHAR(50),
        temp FLOAT,
        feels_like FLOAT,
        humidity INT,
        wind_speed FLOAT,
        dt BIGINT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_city_dt (city, dt)
    ) ENGINE=InnoDB
    ''')
    
    # Daily summary table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_summary (
        id INT AUTO_INCREMENT PRIMARY KEY,
        city VARCHAR(50),
        date DATE,
        avg_temp FLOAT,
        max_temp FLOAT,
        min_temp FLOAT,
        dominant_condition VARCHAR(50),
        UNIQUE KEY unique_city_date (city, date)
    ) ENGINE=InnoDB
    ''')
    
    connection.commit()

# Weather data functions
def get_weather_data(city, max_retries=3):
    """Fetch weather data from OpenWeatherMap API with retry logic"""
    for attempt in range(max_retries):
        try:
            params = {
                'q': city,
                'appid': API_KEY,
                'units': 'metric'
            }
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed for {city} (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2)

def insert_weather_data(connection, data):
    """Insert or update weather data with error handling"""
    query = '''
    INSERT INTO weather_data 
        (city, main, temp, feels_like, humidity, wind_speed, dt)
    VALUES 
        (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        main = VALUES(main),
        temp = VALUES(temp),
        feels_like = VALUES(feels_like),
        humidity = VALUES(humidity),
        wind_speed = VALUES(wind_speed)
    '''
    cursor = connection.cursor()
    try:
        cursor.execute(query, (
            data['city'],
            data['main'],
            data['temp'],
            data['feels_like'],
            data['humidity'],
            data['wind_speed'],
            data['dt']
        ))
        connection.commit()
    except Error as e:
        print(f"Database error for {data['city']}: {e}")
        connection.rollback()

def calculate_daily_summary(connection):
    """Calculate and store daily weather summaries"""
    cursor = connection.cursor()
    query = '''
    INSERT INTO daily_summary 
        (city, date, avg_temp, max_temp, min_temp, dominant_condition)
    SELECT 
        city,
        DATE(FROM_UNIXTIME(dt)) as date,
        ROUND(AVG(temp), 2) as avg_temp,
        MAX(temp) as max_temp,
        MIN(temp) as min_temp,
        (
            SELECT w2.main
            FROM weather_data w2
            WHERE w2.city = w1.city 
            AND DATE(FROM_UNIXTIME(w2.dt)) = DATE(FROM_UNIXTIME(w1.dt))
            GROUP BY w2.main
            ORDER BY COUNT(*) DESC
            LIMIT 1
        ) as dominant_condition
    FROM weather_data w1
    WHERE DATE(FROM_UNIXTIME(dt)) = CURDATE()
    GROUP BY city, DATE(FROM_UNIXTIME(dt))
    ON DUPLICATE KEY UPDATE
        avg_temp = VALUES(avg_temp),
        max_temp = VALUES(max_temp),
        min_temp = VALUES(min_temp),
        dominant_condition = VALUES(dominant_condition)
    '''
    try:
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(f"Error calculating daily summary: {e}")
        connection.rollback()

# Data retrieval functions
def get_latest_weather_data(connection):
    """Get the most recent weather data for each city"""
    cursor = connection.cursor(dictionary=True)
    query = '''
    WITH RankedData AS (
        SELECT 
            *,
            ROW_NUMBER() OVER (PARTITION BY city ORDER BY dt DESC) as rn
        FROM weather_data
    )
    SELECT 
        id, city, main, temp, feels_like, humidity, wind_speed, dt, created_at
    FROM RankedData
    WHERE rn = 1
    ORDER BY city
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return results

def get_daily_summary(connection):
    """Get today's weather summary for each city"""
    cursor = connection.cursor(dictionary=True)
    query = '''
    SELECT *
    FROM daily_summary
    WHERE date = CURDATE()
    ORDER BY city
    '''
    cursor.execute(query)
    return cursor.fetchall()

# Background update process
def update_weather_data():
    """Background process to update weather data"""
    while True:
        try:
            connection = create_db_connection()
            if connection:
                for city in CITIES:
                    
                    weather_data = get_weather_data(city)
                    if weather_data and weather_data.get('cod') == 200:
                        data = {
                            'city': city,
                            'main': weather_data['weather'][0]['main'],
                            'temp': weather_data['main']['temp'],
                            'feels_like': weather_data['main']['feels_like'],
                            'humidity': weather_data['main']['humidity'],
                            'wind_speed': weather_data['wind']['speed'],
                            'dt': weather_data['dt']
                        }
                        insert_weather_data(connection, data)
                            
                calculate_daily_summary(connection)
                connection.close()
                
        except Exception as e:
            print(f"Update process error: {e}")
        finally:
            time.sleep(300)  # Update every 5 minutes

# Routes
@app.route('/')
def index():
    """Main page route"""
    try:
        connection = create_db_connection()
        if not connection:
            return "Database connection error", 500

        latest_data = get_latest_weather_data(connection)
        daily_summary = get_daily_summary(connection)
        
        # Generate alerts for high temperatures
        alerts = []
        for data in latest_data:
            if data['temp'] > 35:
                alerts.append(f"ALERT: Temperature in {data['city']} exceeds 35°C!")
        
        connection.close()
        return render_template('index.html', 
                             weather_data=latest_data,
                             daily_summary=daily_summary,
                             alerts=alerts)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/api/weather')
def api_weather():
    """API endpoint for weather data"""
    try:
        connection = create_db_connection()
        if not connection:
            return jsonify({"error": "Database connection error"}), 500

        latest_data = get_latest_weather_data(connection)
        daily_summary = get_daily_summary(connection)
        connection.close()
        
        return jsonify({
            'current_weather': latest_data,
            'daily_summary': daily_summary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Initialize database and start background update process
    connection = create_db_connection()
    if connection:
        create_tables(connection)
        connection.close()
        
        update_thread = Thread(target=update_weather_data)
        update_thread.daemon = True
        update_thread.start()
        
        app.run(debug=True)
    else:
        print("Failed to initialize database")