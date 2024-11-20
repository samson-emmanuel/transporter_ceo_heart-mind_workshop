from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "event.db"


def init_db():
    """Initializes the SQLite database with demo data."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Create registrations table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            day INTEGER NOT NULL
        )
    """
    )

    # Create names table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """
    )

    # Insert demo names if table is empty
    c.execute("SELECT COUNT(*) FROM names")
    if c.fetchone()[0] == 0:
        demo_names = [
            "A&A Global",
            "ABC",
            "Abdlas",
            "Beuno",
            "BHN",
            "BIG",
            "Bufa",
            "CBV",
            "Chris Haulage",
            "Defrost",
            "Deomat",
            "Ebony",
            "Ecologique",
            "GPG",
            "HST",
            "Iquasu",
            "JBC",
            "Joza",
            "KaySky",
            "Marc Chagall",
            "Rembam",
            "Remo Commercial",
            "RVL",
            "Sagamu Global",
            "Shiwatech",
            "Tetralog",
            "TRL",
            "TSL",
            "Vicky World",
            "Whitesoul",
        ]

        c.executemany(
            "INSERT INTO names (name) VALUES (?)", [(name,) for name in demo_names]
        )

    conn.commit()
    conn.close()


# Initialize the database
init_db()


@app.route("/")
def user_page():
    """Renders the user registration page."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        """
        SELECT name FROM names WHERE name NOT IN (SELECT name FROM registrations)
    """
    )
    names = [row[0] for row in c.fetchall()]
    conn.close()

    return render_template("index.html", names=names)


@app.route("/register", methods=["POST"])
def register():
    """Handles user registration requests."""
    data = request.json
    name = data.get("name")
    email = data.get("email")
    day = data.get("day")

    if not name or not email or not day:
        return jsonify({"message": "Name, email, and day are required!"}), 400

    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        # Check slot availability
        c.execute("SELECT COUNT(*) FROM registrations WHERE day = ?", (day,))
        count = c.fetchone()[0]

        max_slots = 15 if day == 1 else 14
        if count >= max_slots:
            return jsonify({"message": "Selected day is fully booked!"}), 400

        # Register the user
        c.execute(
            "INSERT INTO registrations (name, email, day) VALUES (?, ?, ?)",
            (name, email, day),
        )
        conn.commit()
        return jsonify({"message": "Registration successful!"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"message": "This name has already been registered!"}), 400
    finally:
        conn.close()


@app.route("/admin")
def admin_dashboard():
    """Renders the admin dashboard."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Fetch slot counts
    c.execute("SELECT COUNT(*) FROM registrations WHERE day = 1")
    day1_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM registrations WHERE day = 2")
    day2_count = c.fetchone()[0]

    # Fetch all registrations
    c.execute("SELECT name, email, day FROM registrations")
    registrations = [
        {"name": row[0], "email": row[1], "day": row[2]} for row in c.fetchall()
    ]

    conn.close()
    return render_template(
        "admin.html",
        day1_count=day1_count,
        day2_count=day2_count,
        registrations=registrations,
    )


@app.route("/admin-data", methods=["GET"])
def admin_data():
    """Returns registration data in JSON format."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Fetch all registrations
    c.execute("SELECT name, email, day FROM registrations")
    registrations = [
        {"name": row[0], "email": row[1], "day": row[2]} for row in c.fetchall()
    ]
    conn.close()

    return jsonify(registrations)


@app.route("/slot-info", methods=["GET"])
def slot_info():
    """Returns the number of slots booked for each day."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Fetch slot counts
    c.execute("SELECT COUNT(*) FROM registrations WHERE day = 1")
    day1_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM registrations WHERE day = 2")
    day2_count = c.fetchone()[0]

    conn.close()
    return jsonify({"day1Count": day1_count, "day2Count": day2_count})


if __name__ == "__main__":
    app.run(debug=True)
