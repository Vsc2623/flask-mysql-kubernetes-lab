import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

app.secret_key =os.environ["FLASK_SECRET_KEY"]

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "mysql-db"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ.get("DB_NAME", "flaskdb"),
    )


@app.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        message = request.form.get("message", "").strip()

        if not message:
            flash("Please enter a message.")
            return redirect(url_for("hello_world"))

        if len(message) > 5000:
            flash("Message must be 5000 characters or fewer.")
            return redirect(url_for("hello_world"))

        connection = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO messages (message) VALUES (%s)",
                (message,),
            )
            connection.commit()
            cursor.close()
            flash("Message saved successfully!")
        except mysql.connector.Error:
            app.logger.exception("Unable to save message to MySQL")
            flash("Unable to save your message. Please try again.")
        finally:
            if connection and connection.is_connected():
                connection.close()

        return redirect(url_for("hello_world"))

    messages = []
    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, message, created_at FROM messages ORDER BY id DESC"
        )
        messages = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error:
        app.logger.exception("Unable to read messages from MySQL")
        flash("Database is unavailable. Please try again later.")
    finally:
        if connection and connection.is_connected():
            connection.close()

    return render_template("index.html", messages=messages)


@app.route("/health")
def health():
    return "Server is up and running"
