# Customer Process Management (Flask + SQLite)

A beginner-friendly Customer Process Management website built with Flask and SQLite. Customers can register, log in, submit service requests, and track request status. Admins can manage customers and update request statuses.

## Features
- Customer registration, login, logout
- Admin login with separate credentials
- Session-based authentication (no JWT)
- Service request creation and status tracking
- Customer profile updates
- Admin management dashboard (view/delete customers and requests, update status)
- Flash messages and clean responsive UI

## Tech Stack
- **Frontend:** HTML + CSS
- **Backend:** Python (Flask)
- **Database:** SQLite

## Project Structure
```
app.py
templates/
  base.html
  login.html
  register.html
  customer_dashboard.html
  admin_dashboard.html
static/
  css/style.css
database.db
```

## How to Run Locally
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Customer-Management-System-CMS-
   ```

2. **Create and activate a virtual environment (optional but recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in your browser**
   ```
   http://127.0.0.1:5000
   ```

## Admin Credentials
By default, the app creates an admin user on startup if it does not exist.

- **Email:** `admin@example.com`
- **Password:** `admin123`

You can override these defaults using environment variables:

```bash
export ADMIN_EMAIL="your-admin@example.com"
export ADMIN_PASSWORD="your-secure-password"
```

## Notes for Beginners
- The database file (`database.db`) is created automatically the first time the app runs.
- Passwords are securely hashed using `werkzeug.security`.
- The session stores the logged-in user ID and role.
