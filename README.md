# Smart Food Waste Management System

A beginner-friendly full-stack Flask project that connects food donors with NGOs and collection organizations. Donors can upload surplus food, the system predicts freshness using a Scikit-learn Decision Tree model, nearby NGOs can accept donations, and admins can monitor system-wide impact.

## Features

- User authentication with donor, NGO, and admin roles
- Food donation CRUD-style flow with image upload
- Secure password hashing and session handling
- MySQL database integration with foreign keys and timestamps
- Food freshness prediction using Scikit-learn
- Location-based NGO matching using pickup area text
- NGO dashboard to accept donations
- Admin dashboard with analytics and Chart.js visualizations
- Flask-Mail notifications for new and accepted donations
- Responsive Bootstrap UI

## Project Structure

```text
smart-food-waste-management/
├── app.py
├── requirements.txt
├── README.md
├── config.py
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   └── images/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── donate.html
│   ├── ngo_dashboard.html
│   ├── admin_dashboard.html
│   └── donations.html
├── uploads/
├── models/freshness_model.pkl
├── ml/
│   ├── train_model.py
│   └── food_data.csv
└── database/schema.sql
```

## Installation

```bash
cd smart-food-waste-management
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, activate the environment with:

```bash
source venv/bin/activate
```

## Database Setup

1. Start MySQL.
2. Run the SQL script:

```bash
mysql -u root -p < database/schema.sql
```

3. Update environment variables if your MySQL credentials differ:

```bash
set MYSQL_HOST=localhost
set MYSQL_USER=root
set MYSQL_PASSWORD=your_password
set MYSQL_DB=smart_food_waste
```

## Train the Machine Learning Model

```bash
python ml/train_model.py
```

This creates `models/freshness_model.pkl`.

## Run the App

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Email Notifications

Set mail credentials before running the app:

```bash
set MAIL_USERNAME=your_email@gmail.com
set MAIL_PASSWORD=your_app_password
set MAIL_DEFAULT_SENDER=your_email@gmail.com
```

For Gmail, use an app password instead of your normal account password.

## Screenshots

Add screenshots here after running the app:

- Home page
- Donor dashboard
- Donation form
- NGO dashboard
- Admin analytics dashboard

## Deployment

For Render and Railway, use a production server instead of the Flask development server:

```bash
gunicorn app:app
```

Required environment variables:

```text
SECRET_KEY=use_a_long_random_secret
MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=smart_food_waste
MYSQL_PORT=3306
MAIL_USERNAME=optional_email_username
MAIL_PASSWORD=optional_email_app_password
MAIL_DEFAULT_SENDER=optional_sender_email
```

On Railway, the app also accepts Railway's common MySQL variable names: `MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`, and `MYSQLPORT`.

Import `database/schema.sql` into the deployed MySQL database before opening the live app URL. The home page reads from MySQL, so wrong database credentials or missing tables will cause a server error.

### Render

1. Push the project to GitHub.
2. Create a new Render Web Service.
3. Use `pip install -r requirements.txt && python ml/train_model.py` as the build command.
4. Use `gunicorn app:app` as the start command.
5. Add MySQL and mail settings as environment variables.
6. Import `database/schema.sql` into your cloud MySQL database.

### Railway

1. Create a Railway project from your GitHub repository.
2. Add a MySQL service.
3. Set the database environment variables.
4. Use `gunicorn app:app` as the start command.
5. Import `database/schema.sql` into the Railway MySQL database.

### PythonAnywhere

1. Upload the project files.
2. Create a virtual environment and install requirements.
3. Create a MySQL database from the PythonAnywhere dashboard.
4. Import `database/schema.sql`.
5. Configure the WSGI file to import `app` from `app.py`.

## Production Notes

- Replace the default `SECRET_KEY`.
- Disable Flask debug mode in production.
- Store uploaded files in cloud storage for larger deployments.
- Use real geocoding or Google Maps Distance Matrix API for precise NGO matching.
- Add CSRF protection with Flask-WTF for public production deployments.
