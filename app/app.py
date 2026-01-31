from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
import time

app = Flask(__name__)

def get_db_connection():
    """Create and return a database connection"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            return connection
        except mysql.connector.Error as err:
            if attempt < max_retries - 1:
                print(f"Database connection attempt {attempt + 1} failed: {err}")
                time.sleep(retry_delay)
            else:
                raise

def init_db():
    """Initialize database and create table if it doesn't exist"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Create entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.route("/")
def index():
    """Display all entries and the form to add new entries"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Fetch all entries
        cursor.execute("SELECT * FROM entries ORDER BY created_at DESC")
        entries = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template("index.html", entries=entries)
    except Exception as e:
        return render_template("index.html", entries=[], error=f"Database error: {str(e)}")

@app.route("/add", methods=["POST"])
def add_entry():
    """Add a new entry to the database"""
    try:
        title = request.form.get("title")
        description = request.form.get("description")
        
        if not title or not description:
            return redirect(url_for("index"))
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Insert new entry
        cursor.execute(
            "INSERT INTO entries (title, description) VALUES (%s, %s)",
            (title, description)
        )
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return redirect(url_for("index"))
    except Exception as e:
        print(f"Error adding entry: {e}")
        return redirect(url_for("index"))

if __name__ == "__main__":
    # Initialize database on startup
    init_db()
    
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
