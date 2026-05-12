"""Flask backend for the Smart Food Waste Management System."""

from datetime import datetime
from functools import wraps
import os
import pickle

import pandas as pd
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import Config


app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)
mail = Mail(app)


def allowed_file(filename):
    """Return True when an upload has an accepted image extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


def login_required(view):
    """Protect routes that require an authenticated user."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def role_required(*roles):
    """Protect routes that are only valid for specific user roles."""
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if session.get("role") not in roles:
                flash("You do not have permission to access that page.", "danger")
                return redirect(url_for("dashboard"))
            return view(*args, **kwargs)

        return wrapped_view

    return decorator


def get_cursor():
    """Create a MySQL cursor using the configured DictCursor."""
    return mysql.connection.cursor()


def send_email(to_email, subject, body):
    """Send an email when mail credentials are configured."""
    if not to_email or not app.config.get("MAIL_USERNAME"):
        return
    try:
        mail.send(Message(subject=subject, recipients=[to_email], body=body))
    except Exception as exc:
        app.logger.warning("Email notification skipped: %s", exc)


def load_freshness_model():
    """Load the trained model if it exists."""
    model_path = os.path.join(app.root_path, "models", "freshness_model.pkl")
    if not os.path.exists(model_path):
        return None
    with open(model_path, "rb") as model_file:
        return pickle.load(model_file)


def predict_freshness(storage_hours, temperature=26, humidity=75):
    """Predict whether donated food is fresh or spoiled."""
    model_bundle = load_freshness_model()
    if not model_bundle:
        return "fresh", 0.75

    row = pd.DataFrame(
        [{"storage_hours": storage_hours, "temperature": temperature, "humidity": humidity}]
    )
    model = model_bundle["model"]
    encoder = model_bundle["label_encoder"]
    prediction = model.predict(row)[0]
    probabilities = model.predict_proba(row)[0]
    return encoder.inverse_transform([prediction])[0], round(float(max(probabilities)) * 100, 2)


def find_matching_ngos(location):
    """Match NGOs using simple location text similarity."""
    cursor = get_cursor()
    like_location = f"%{location}%"
    cursor.execute(
        """
        SELECT ngos.*, users.email AS user_email
        FROM ngos
        JOIN users ON users.id = ngos.user_id
        WHERE ngos.location LIKE %s OR ngos.address LIKE %s
        ORDER BY ngos.verified DESC, ngos.capacity DESC
        """,
        (like_location, like_location),
    )
    return cursor.fetchall()


@app.route("/")
def index():
    """Render the landing page with recent donation activity."""
    cursor = get_cursor()
    cursor.execute(
        """
        SELECT food_name, category, quantity, pickup_location, status, created_at
        FROM food_donations
        ORDER BY created_at DESC
        LIMIT 6
        """
    )
    recent_donations = cursor.fetchall()
    return render_template("index.html", recent_donations=recent_donations)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Create donor, NGO, or admin accounts."""
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form["role"]
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        location = request.form.get("location", "").strip()

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for("register"))
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        cursor = get_cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Email is already registered.", "danger")
            return redirect(url_for("register"))

        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, phone, address, location, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (name, email, generate_password_hash(password), phone, address, location, role),
        )
        user_id = cursor.lastrowid

        if role == "ngo":
            cursor.execute(
                """
                INSERT INTO ngos (user_id, organization_name, contact_person, phone, email, address, location, capacity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    request.form.get("organization_name") or name,
                    name,
                    phone,
                    email,
                    address,
                    location,
                    int(request.form.get("capacity") or 50),
                ),
            )
        elif role == "admin":
            cursor.execute("INSERT INTO admin (user_id) VALUES (%s)", (user_id,))

        mysql.connection.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate users and initialize the session."""
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        cursor = get_cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clear session state and log the current user out."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Route users to the right dashboard for their role."""
    if session.get("role") == "ngo":
        return redirect(url_for("ngo_dashboard"))
    if session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))

    cursor = get_cursor()
    cursor.execute(
        "SELECT * FROM food_donations WHERE donor_id = %s ORDER BY created_at DESC",
        (session["user_id"],),
    )
    donations = cursor.fetchall()
    return render_template("dashboard.html", donations=donations)


@app.route("/donate", methods=["GET", "POST"])
@login_required
@role_required("donor")
def donate():
    """Create a new food donation with image upload and ML prediction."""
    prediction = None
    confidence = None
    matches = []

    if request.method == "POST":
        food_name = request.form["food_name"].strip()
        category = request.form["category"]
        quantity = request.form["quantity"].strip()
        storage_hours = int(request.form.get("storage_hours") or 0)
        expiry_time = request.form["expiry_time"]
        pickup_location = request.form["pickup_location"].strip()
        temperature = int(request.form.get("temperature") or 26)
        humidity = int(request.form.get("humidity") or 75)

        image = request.files.get("food_image")
        image_filename = None
        if image and image.filename:
            if not allowed_file(image.filename):
                flash("Please upload a valid image file.", "danger")
                return redirect(url_for("donate"))
            image_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secure_filename(image.filename)}"
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        prediction, confidence = predict_freshness(storage_hours, temperature, humidity)

        cursor = get_cursor()
        cursor.execute(
            """
            INSERT INTO food_donations
            (donor_id, food_name, category, quantity, storage_hours, expiry_time, pickup_location,
             image_filename, freshness_prediction, prediction_confidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session["user_id"],
                food_name,
                category,
                quantity,
                storage_hours,
                expiry_time,
                pickup_location,
                image_filename,
                prediction,
                confidence,
            ),
        )
        donation_id = cursor.lastrowid
        mysql.connection.commit()

        matches = find_matching_ngos(pickup_location)
        for ngo in matches[:5]:
            send_email(
                ngo.get("user_email") or ngo.get("email"),
                "New food donation available nearby",
                f"{food_name} ({quantity}) is available at {pickup_location}. Donation ID: {donation_id}.",
            )

        flash("Food donation added successfully.", "success")

    return render_template("donate.html", prediction=prediction, confidence=confidence, matches=matches)


@app.route("/donations")
@login_required
def donations():
    """Display all active donations for donors, NGOs, and admins."""
    cursor = get_cursor()
    cursor.execute(
        """
        SELECT d.*, u.name AS donor_name
        FROM food_donations d
        JOIN users u ON u.id = d.donor_id
        ORDER BY d.created_at DESC
        """
    )
    all_donations = cursor.fetchall()
    return render_template("donations.html", donations=all_donations)


@app.route("/ngo-dashboard")
@login_required
@role_required("ngo")
def ngo_dashboard():
    """Show nearby food donations and accepted requests for an NGO."""
    cursor = get_cursor()
    cursor.execute("SELECT * FROM ngos WHERE user_id = %s", (session["user_id"],))
    ngo = cursor.fetchone()
    if not ngo:
        flash("Please complete NGO registration details.", "warning")
        return redirect(url_for("dashboard"))

    cursor.execute(
        """
        SELECT d.*, u.name AS donor_name, u.email AS donor_email
        FROM food_donations d
        JOIN users u ON u.id = d.donor_id
        WHERE d.status = 'pending'
          AND d.pickup_location LIKE %s
        ORDER BY d.created_at DESC
        """,
        (f"%{ngo['location']}%",),
    )
    nearby_donations = cursor.fetchall()

    cursor.execute(
        """
        SELECT r.*, d.food_name, d.quantity, d.pickup_location
        FROM donation_requests r
        JOIN food_donations d ON d.id = r.donation_id
        WHERE r.ngo_id = %s
        ORDER BY r.created_at DESC
        """,
        (ngo["id"],),
    )
    requests = cursor.fetchall()
    return render_template("ngo_dashboard.html", ngo=ngo, donations=nearby_donations, requests=requests)


@app.route("/accept-donation/<int:donation_id>", methods=["POST"])
@login_required
@role_required("ngo")
def accept_donation(donation_id):
    """Allow an NGO to accept a pending donation."""
    cursor = get_cursor()
    cursor.execute("SELECT * FROM ngos WHERE user_id = %s", (session["user_id"],))
    ngo = cursor.fetchone()
    if not ngo:
        flash("NGO profile was not found.", "danger")
        return redirect(url_for("ngo_dashboard"))

    cursor.execute("SELECT * FROM food_donations WHERE id = %s AND status = 'pending'", (donation_id,))
    donation = cursor.fetchone()
    if not donation:
        flash("Donation is no longer available.", "warning")
        return redirect(url_for("ngo_dashboard"))

    cursor.execute(
        """
        INSERT INTO donation_requests (donation_id, ngo_id, donor_id, status, message)
        VALUES (%s, %s, %s, 'accepted', %s)
        """,
        (donation_id, ngo["id"], donation["donor_id"], "Accepted by NGO for collection."),
    )
    cursor.execute(
        "UPDATE food_donations SET status = 'accepted', accepted_by = %s WHERE id = %s",
        (ngo["id"], donation_id),
    )
    cursor.execute("SELECT email FROM users WHERE id = %s", (donation["donor_id"],))
    donor = cursor.fetchone()
    mysql.connection.commit()

    send_email(
        donor["email"],
        "Your food donation has been accepted",
        f"{ngo['organization_name']} accepted your donation: {donation['food_name']}.",
    )

    flash("Donation accepted and donor notified.", "success")
    return redirect(url_for("ngo_dashboard"))


@app.route("/admin-dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    """Render admin analytics and management tables."""
    cursor = get_cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM users")
    total_users = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM ngos")
    total_ngos = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM food_donations")
    total_donations = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM donation_requests WHERE status = 'requested'")
    pending_requests = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM food_donations WHERE status = 'accepted'")
    accepted_donations = cursor.fetchone()["total"]
    cursor.execute("SELECT COALESCE(SUM(CAST(quantity AS UNSIGNED)), 0) AS total FROM food_donations")
    waste_reduction = cursor.fetchone()["total"]
    cursor.execute(
        """
        SELECT category, COUNT(*) AS total
        FROM food_donations
        GROUP BY category
        ORDER BY total DESC
        """
    )
    category_stats = cursor.fetchall()
    cursor.execute("SELECT * FROM food_donations ORDER BY created_at DESC LIMIT 10")
    latest_donations = cursor.fetchall()

    stats = {
        "total_users": total_users,
        "total_ngos": total_ngos,
        "total_donations": total_donations,
        "pending_requests": pending_requests,
        "accepted_donations": accepted_donations,
        "waste_reduction": waste_reduction,
    }
    return render_template(
        "admin_dashboard.html",
        stats=stats,
        category_stats=category_stats,
        latest_donations=latest_donations,
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded food images."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.errorhandler(404)
def not_found(error):
    """Render a friendly page for unknown URLs."""
    return render_template("base.html", page_error="Page not found."), 404


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
