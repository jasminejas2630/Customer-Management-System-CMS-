# Customer Management System (CMS)

A simple Customer Management System designed to manage customer records efficiently.  
This project allows users to perform basic CRUD operations such as adding, viewing, updating, and deleting customer information.

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
- ```
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
# Customer-Management-System-CMS-
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
