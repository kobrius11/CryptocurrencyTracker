# end_of_the_line
# Crypto Tracker

Crypto Tracker is a web application that allows users to stay updated with real-time cryptocurrency prices and charts. It enables users to track their cryptocurrency portfolio and monitor their investments with ease.

## Features

- Real-time cryptocurrency prices and charts
- Portfolio tracking functionality
- User-friendly interface
- Ccxt apis implementation https://github.com/ccxt/ccxt


## Installation

To run Crypto Tracker locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/crypto-tracker.git

2. Create venv in CryptocurrencyTracker/

   ```bash
   python3 -m venv venv
   source venv/bin/activate 

3. Install requirements.txt

   ```bash
   pip install -r requirements.txt

4. Create local_settings.py in crypto_tracker/crypto_tracker:

  ### DJANGO SECRET KEY
  SECRET_KEY = you can get it from django.core.management.utils.get_random_secret_key(), or https://miniwebtool.com/django-secret-key-generator/

  ### DATABASE SETTINGS
  -POSTGRES_HOST = 'postgres'
  -POSTGRES_DB = 'tracker_database'
  -POSTGRES_USER = 'user'
  -POSTGRES_PASSWORD = 'pass'
  -POSTGRES_PORT = 5432

  ### ENCRYPTION SETTINGS
  -KEY_INSTANCE = 32 byte key, generated from Fernet.generate_key(), you may find it in ecryption_config.py

5. Create docker images, and launch servers:

   ### You need to have wsl linux distro, if you are running on windows!
   ### Docker only works in linux enviroment !
   
   Run docker app, and run these commands in CryptocurrencyTracker/

   ```bash
   docker-compose build
   docker-compose up

You may now, try to launch http://localhost:8000/ in your browser
you can change ALLOWED_HOSTS in settings.py file to suit your liking. 
  
