# 📄 Weather Monitoring Application
## 📝 Overview

This project is a weather monitoring web application. It provides an interface for tracking weather data, likely through a web-based front-end powered by Python.The Weather Monitoring Application helps users track real-time weather conditions (such as temperature, minimum & maximum temperature, humidity and wind speed) for locations like Bangalore, Chennai, Delhi, Hyderabad, Kolkata and Delhi. This can be used to display current data or forecast information via APIs and visualize trends using graphs.

## 📂 Project Structure
```bash
weather_monitoring_extracted/
    Appli-2/
        app.py
        sql.txt
        templates/
            index.html
   ```
### weather_monitoring

│ ├── app.py 🚪 # Main application script (Python)

│ ├── sql.txt 📜 # SQL commands or database setup

│ └── templates/

│ └── index.html 🖥️ # Web interface template



## ⚙️ Prerequisites

Make sure you have the following installed on your machine:

- Python 3.x
- Flask (`pip install flask`)
- SQLite (if `sql.txt` sets up a local database)

## 🧠 Installation

1. Clone the repository or download the project.
   ```bash
   git clone https://github.com/your-username/weather-monitoring.git
   cd weather-monitoring/Appli-2
    ```
 2. Install the required Python packages.
     ```bash
     pip install -r requirements.txt
     ```
    Note: If requirements.txt is not provided, you may need at least Flask:
      ```bash
    pip install flask
      ```
  3. Set up the database using sql.txt:
     
     Open the file and execute the SQL commands in your SQLite interface or using sqlite3:    
        ```bash
       sqlite3 weather.db < sql.txt
        ```
  4. Set up the API_KEY.
   
        ##### Sign Up for the Weather API Service
    
        -> Visit the OpenWeatherMap website: https://openweathermap.org.
       
        -> Click on Sign Up or Sign In if you already have an account.
     
        -> Verify your email to activate the account.

        ##### Get the API Key
    
        -> After logging in, go to API keys under your account section.
   
        -> You’ll see a default key named default or My API Key. You can use this or generate a new one by clicking + Generate.
   
        -> Copy the API key for use in your project.   

        -> And replace with the API_KEY in the configuration app.py file.

        
  ## ✨  Usage
  1. Run the application:
      ```bash
      python app.py
      ```
   2. Open your browser and visit:
         ```bash
          http://127.0.0.1:5000
         ```

      ![Alt Text](URL_TO_IMAGE)
      ![Weather monitoring SS](https://github.com/user-attachments/assets/7589e81c-1a2f-4d6e-86dd-19de3172e0a2)

    

         
 ## 📄 File Overview
   -> app.py: The main script that runs the Flask web server.
   
   -> sql.txt: Contains SQL commands, possibly for setting up a database.
   
   -> templates/index.html: HTML file that serves as the front-end for the web interface.


## 👥 Contributing
Feel free to fork the project and submit pull requests. For major changes, please open an issue first to discuss what you would like to change. 

