# JOStudi

This project is a Django-based e-commerce application that uses Railway to host the database and website. 
It allows users to add products to a shopping cart and complete their order

## Features:
- User authentication and profile management
- Shopping cart functionality
- Checkout and order creation
- Admin dashboard for managing orders

---

## Getting Started

Follow the steps below to get the project up and running locally.

### 1. Create a Virtual Environment

Before running the project, it's a good idea to create a virtual environment to isolate the dependencies.

```bash
# Create a virtual environment (use python3 or python depending on your setup)
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 2. Install Required Packages
```bash
pip install -r requirements.txt
```

### 3. Configure Settings
Before running the server, configure the following settings in your settings.py file:

Database Settings: Railway is used for hosting the database. Make sure to set up your database connection with the Railway credentials (provided in your Railway dashboard).

Use the DATABASE_URL provided by Railway to set up the database connection. You can use dj-database-url to parse the URL:
```python

# DATABASE CONFIGURATION FOR LOCAL DEVELOPMENT
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# DATABASE CONFIGURATION FOR PROD
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
```

### 4. Apply Database Migrations
After configuring the settings, apply the migrations to set up your database schema.
```bash
python manage.py migrate
```

### 5. Create a Superuser (Optional)
If you need an admin account to access the Django admin panel, you can create a superuser with the following command:
```bash
python manage.py createsuperuser
```
Follow the prompts to create the superuser.

### 6. Start the Development Server
Once the migrations are complete and the settings are configured, you can start the Django development server.
```bash
python manage.py runserver
```
This will start the server at http://127.0.0.1:8000/. You can now access the site in your browser.

### 7. Additional Commands
To collect static files (for production use):
```bash
python manage.py collectstatic
```

To run tests:
```bash
python manage.py test
```

### Deployment
This project is deployed on Railway, which handles both the database and the website hosting. You can view the deployed project by visiting the Railway dashboard.

URL of the deployed site: https://your-railway-project-url.railway.app/

### Notes
Make sure to keep your environment variables (e.g.,database URLs...) secure.

Railway handles the database automatically in the cloud, so no need to manually set up a local database.

If you face any issues during the setup or deployment, check the logs on the Railway dashboard for more details.