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

### Render

1. Push the project to GitHub.
2. Create a new Render Web Service.
3. Use `pip install -r requirements.txt` as the build command.
4. Use `gunicorn app:app` as the start command.
5. Add MySQL and mail settings as environment variables.

### Railway

1. Create a Railway project from your GitHub repository.
2. Add a MySQL service.
3. Set the database environment variables.
4. Use `python app.py` for testing or `gunicorn app:app` for production.

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
