"""Flask app for a beginner-friendly Customer Process Management system."""
from __future__ import annotations

import os
import sqlite3
from functools import wraps
from typing import Callable

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Basic configuration (override with environment variables for production)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["DATABASE"] = os.path.join(app.root_path, "database.db")
app.config["ADMIN_EMAIL"] = os.environ.get("ADMIN_EMAIL", "admin@example.com")
app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD", "admin123")


# --------------------------
# Database helpers
# --------------------------

def get_db() -> sqlite3.Connection:
    """Open a new database connection if there is none yet for this request."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception: Exception | None = None) -> None:
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Create tables and ensure the admin user exists."""
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # Users table: stores both customers and admin accounts
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """
    )

    # Requests table: service requests linked to customers
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    # Ensure an admin account exists
    cursor.execute("SELECT id FROM users WHERE email = ? AND role = 'admin'", (app.config["ADMIN_EMAIL"],))
    admin_exists = cursor.fetchone()
    if not admin_exists:
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, 'admin')",
            (
                "Admin",
                app.config["ADMIN_EMAIL"],
                generate_password_hash(app.config["ADMIN_PASSWORD"]),
            ),
        )

    db.commit()
    db.close()


# Initialize the database at startup
init_db()


# --------------------------
# Authentication helpers
# --------------------------

def login_required(view: Callable) -> Callable:
    """Require a logged-in user for protected routes."""

    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            if request.path.startswith("/admin"):
                return redirect(url_for("admin_login"))
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def role_required(role: str) -> Callable:
    """Ensure the current user has the correct role."""

    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapped_view(**kwargs):
            if session.get("role") != role:
                flash("You do not have permission to access that page.", "danger")
                return redirect(url_for("index"))
            return view(**kwargs)

        return wrapped_view

    return decorator


# --------------------------
# Public routes
# --------------------------

@app.route("/")
def index():
    """Redirect users based on their authentication status."""
    if session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))
    if session.get("role") == "customer":
        return redirect(url_for("customer_dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new customer account."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        db = get_db()
        existing_user = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            flash("An account with that email already exists.", "danger")
            return render_template("register.html")

        db.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, 'customer')",
            (name, email, generate_password_hash(password)),
        )
        db.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Customer login."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("login.html", is_admin=False)

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ? AND role = 'customer'", (email,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["name"]
            flash("Welcome back!", "success")
            return redirect(url_for("customer_dashboard"))

        flash("Invalid credentials.", "danger")

    return render_template("login.html", is_admin=False)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login route."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("login.html", is_admin=True)

        db = get_db()
        admin = db.execute(
            "SELECT * FROM users WHERE email = ? AND role = 'admin'", (email,)
        ).fetchone()

        if admin and check_password_hash(admin["password"], password):
            session.clear()
            session["user_id"] = admin["id"]
            session["role"] = admin["role"]
            session["name"] = admin["name"]
            flash("Admin login successful.", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials.", "danger")

    return render_template("login.html", is_admin=True)


@app.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# --------------------------
# Customer routes
# --------------------------

@app.route("/customer/dashboard")
@login_required
@role_required("customer")
def customer_dashboard():
    """Display customer dashboard and their requests."""
    db = get_db()
    customer = db.execute(
        "SELECT name, email FROM users WHERE id = ?",
        (session["user_id"],),
    ).fetchone()
    requests = db.execute(
        "SELECT * FROM requests WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],),
    ).fetchall()

    return render_template("customer_dashboard.html", requests=requests, customer=customer)


@app.route("/customer/request/new", methods=["POST"])
@login_required
@role_required("customer")
def new_request():
    """Handle submission of a new service request."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not title or not description:
        flash("Title and description are required.", "danger")
        return redirect(url_for("customer_dashboard"))

    db = get_db()
    db.execute(
        "INSERT INTO requests (user_id, title, description, status) VALUES (?, ?, ?, 'Pending')",
        (session["user_id"], title, description),
    )
    db.commit()
    flash("Service request submitted.", "success")
    return redirect(url_for("customer_dashboard"))


@app.route("/customer/profile", methods=["POST"])
@login_required
@role_required("customer")
def update_profile():
    """Update the customer's profile details."""
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email:
        flash("Name and email are required.", "danger")
        return redirect(url_for("customer_dashboard"))

    db = get_db()
    existing_user = db.execute(
        "SELECT id FROM users WHERE email = ? AND id != ?",
        (email, session["user_id"]),
    ).fetchone()

    if existing_user:
        flash("That email is already in use.", "danger")
        return redirect(url_for("customer_dashboard"))

    if password:
        db.execute(
            "UPDATE users SET name = ?, email = ?, password = ? WHERE id = ?",
            (name, email, generate_password_hash(password), session["user_id"]),
        )
    else:
        db.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (name, email, session["user_id"]),
        )

    db.commit()
    session["name"] = name
    flash("Profile updated successfully.", "success")
    return redirect(url_for("customer_dashboard"))


# --------------------------
# Admin routes
# --------------------------

@app.route("/admin/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    """Display the admin dashboard with customers and requests."""
    db = get_db()
    customers = db.execute("SELECT * FROM users WHERE role = 'customer' ORDER BY name").fetchall()
    requests = db.execute(
        """
        SELECT requests.*, users.name AS customer_name, users.email AS customer_email
        FROM requests
        JOIN users ON requests.user_id = users.id
        ORDER BY requests.created_at DESC
        """
    ).fetchall()

    return render_template("admin_dashboard.html", customers=customers, requests=requests)


@app.route("/admin/requests/<int:request_id>/status", methods=["POST"])
@login_required
@role_required("admin")
def update_request_status(request_id: int):
    """Update the status of a service request."""
    status = request.form.get("status", "").strip()
    if status not in {"Pending", "Approved", "Completed"}:
        flash("Invalid status selected.", "danger")
        return redirect(url_for("admin_dashboard"))

    db = get_db()
    db.execute("UPDATE requests SET status = ? WHERE id = ?", (status, request_id))
    db.commit()
    flash("Request status updated.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/requests/<int:request_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_request(request_id: int):
    """Delete a service request."""
    db = get_db()
    db.execute("DELETE FROM requests WHERE id = ?", (request_id,))
    db.commit()
    flash("Request deleted.", "info")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/customers/<int:customer_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_customer(customer_id: int):
    """Delete a customer account and their requests."""
    db = get_db()
    db.execute("DELETE FROM requests WHERE user_id = ?", (customer_id,))
    db.execute("DELETE FROM users WHERE id = ? AND role = 'customer'", (customer_id,))
    db.commit()
    flash("Customer deleted.", "info")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
