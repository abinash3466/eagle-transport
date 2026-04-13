from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import Any

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "eagle_transport_secret_key_demo"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "eagle_transport.db")


TRUCK_TYPES = [
    {"name": "Mini Truck", "capacity": "1 to 3 Tons", "best_for": "Small load and local delivery", "icon": "🚚"},
    {"name": "Pickup", "capacity": "1 to 2 Tons", "best_for": "Short distance and quick trip", "icon": "🛻"},
    {"name": "Light Commercial", "capacity": "3 to 7 Tons", "best_for": "District and city transport", "icon": "🚛"},
    {"name": "Heavy Truck", "capacity": "10 to 16 Tons", "best_for": "State level bulk load", "icon": "🏗️"},
    {"name": "Trailer", "capacity": "20 to 28 Tons", "best_for": "India level long route cargo", "icon": "🚜"},
    {"name": "Container Truck", "capacity": "15 to 25 Tons", "best_for": "Industrial and container load", "icon": "📦"},
]

TRIP_LEVELS = ["District Level", "State Level", "Indian Level"]

COMPANY_LOGOS = ["Tata Motors", "Ashok Leyland", "Mahindra", "BharatBenz", "Eicher", "Volvo"]

RATE_MAP = {"District Level": 22, "State Level": 38, "Indian Level": 56}

TRUCK_MULTIPLIER = {
    "Pickup": 1.0,
    "Mini Truck": 1.1,
    "Light Commercial": 1.25,
    "Heavy Truck": 1.45,
    "Trailer Truck": 1.7,
    "Trailer": 1.7,
    "Container Truck": 1.6,
}


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def query_all(sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    conn = get_db_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def query_one(sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    conn = get_db_connection()
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return row


def execute_sql(sql: str, params: tuple[Any, ...] = ()) -> None:
    conn = get_db_connection()
    conn.execute(sql, params)
    conn.commit()
    conn.close()


def init_db() -> None:
    if os.path.exists(DB_NAME):
        return

    schema_path = os.path.join(BASE_DIR, "schema.sql")
    if not os.path.exists(schema_path):
        raise FileNotFoundError("schema.sql file not found in project folder.")

    conn = get_db_connection()
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.execute(
        "INSERT INTO owners (username, password, full_name) VALUES (?, ?, ?)",
        ("admin", "eagle123", "Eagle Transport Owner"),
    )

    trucks = [
        ("Mini Eagle 1", "TN01ET1001", "Mini", 2.0, "Ravi", "Chennai", 82, 88, 76, 91, 12.7, "Good", "Active"),
        ("Mini Eagle 2", "TN01ET1002", "Mini", 2.5, "Kumar", "Madurai", 64, 84, 80, 75, 12.4, "Moderate", "Active"),
        ("Light Eagle 1", "TN01ET1101", "Light", 5.0, "Suresh", "Trichy", 58, 70, 68, 66, 12.1, "Moderate", "Service Due"),
        ("Heavy Eagle 1", "TN01ET2001", "Heavy", 10.0, "Manoj", "Salem", 90, 92, 88, 95, 12.9, "Good", "Active"),
        ("Heavy Eagle 2", "TN01ET2002", "Heavy", 12.0, "Ajay", "Coimbatore", 48, 55, 61, 58, 11.9, "Moderate", "Active"),
        ("Trailer Eagle 1", "TN01ET3001", "Trailer", 20.0, "Dinesh", "Bangalore", 73, 82, 91, 79, 12.6, "Good", "Active"),
        ("Trailer Eagle 2", "TN01ET3002", "Trailer", 24.0, "Vignesh", "Hyderabad", 17, 33, 29, 52, 11.6, "Poor", "Alert"),
        ("Container Eagle 1", "TN01ET4001", "Container", 18.0, "Arun", "Mumbai", 86, 90, 87, 85, 12.8, "Good", "Active"),
    ]

    conn.executemany(
        """
        INSERT INTO trucks (
            truck_name, truck_number, category, capacity_tons, driver_name,
            current_location, diesel_percent, coolant_level, engine_oil_level,
            brake_oil_level, battery_voltage, tyre_condition, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        trucks,
    )

    drivers = [
        ("ravi", "driver123", "Ravi", "9000000001", 1),
        ("kumar", "driver123", "Kumar", "9000000002", 2),
        ("suresh", "driver123", "Suresh", "9000000003", 3),
        ("manoj", "driver123", "Manoj", "9000000004", 4),
        ("ajay", "driver123", "Ajay", "9000000005", 5),
        ("dinesh", "driver123", "Dinesh", "9000000006", 6),
        ("vignesh", "driver123", "Vignesh", "9000000007", 7),
        ("arun", "driver123", "Arun", "9000000008", 8),
    ]

    conn.executemany(
        "INSERT INTO drivers (username, password, full_name, mobile, assigned_truck_id) VALUES (?, ?, ?, ?, ?)",
        drivers,
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sample_alerts = [
        (7, "Diesel", "Diesel is below safe limit for Trailer Eagle 2", "High", "Open", now),
        (7, "Battery", "Battery voltage is below 12V for Trailer Eagle 2", "High", "Open", now),
        (7, "Engine Oil", "Engine oil level is critically low for Trailer Eagle 2", "High", "Open", now),
    ]
    conn.executemany(
        "INSERT INTO alerts (truck_id, alert_type, message, priority, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        sample_alerts,
    )

    sample_bookings = [
        ("Saravanan", "9876543210", "Tirunelveli", "Madurai", "District Level", "Mini Truck", "Rice Bags", 2.0, 5200, "New", now),
        ("Meena Traders", "9876501234", "Chennai", "Coimbatore", "State Level", "Heavy Truck", "Cement", 10.0, 21800, "Confirmed", now),
    ]
    conn.executemany(
        """
        INSERT INTO bookings (
            customer_name, mobile, pickup_location, drop_location,
            trip_level, truck_type, goods_type, load_weight,
            estimated_amount, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_bookings,
    )

    sample_toll_logs = [
        (4, "Manoj", "Chennai to Salem", "Sriperumbudur Toll Plaza", "2026-04-11 08:15:00", 185.0, "FASTag", "Paid", "Morning crossing", now),
        (4, "Manoj", "Chennai to Salem", "Vellore Toll Plaza", "2026-04-11 10:05:00", 210.0, "FASTag", "Paid", "Smooth crossing", now),
        (5, "Ajay", "Chennai to Coimbatore", "Ulundurpet Toll Plaza", "2026-04-11 09:20:00", 320.0, "FASTag", "Paid", "State route", now),
        (6, "Dinesh", "Bangalore to Mumbai", "Tumkur Toll Plaza", "2026-04-11 07:50:00", 410.0, "FASTag", "Paid", "Long trip", now),
        (7, "Vignesh", "Hyderabad to Nagpur", "Adilabad Toll Plaza", "2026-04-11 11:40:00", 0.0, "FASTag", "Pending", "Payment issue check", now),
    ]

    conn.executemany(
        """
        INSERT INTO toll_logs (
            truck_id, driver_name, route_name, toll_name, crossed_time,
            amount_paid, payment_method, payment_status, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_toll_logs,
    )

    conn.commit()
    conn.close()


def get_health_color(value: float, metric: str) -> str:
    if metric == "battery":
        if value < 12:
            return "red"
        if value < 12.3:
            return "orange"
        return "green"
    if value < 30:
        return "red"
    if value < 60:
        return "orange"
    return "green"


def get_health_score(truck: sqlite3.Row) -> int:
    score = 100
    if truck["diesel_percent"] < 10:
        score -= 25
    elif truck["diesel_percent"] < 30:
        score -= 12

    if truck["engine_oil_level"] < 30:
        score -= 20
    elif truck["engine_oil_level"] < 60:
        score -= 10

    if truck["coolant_level"] < 30:
        score -= 15
    elif truck["coolant_level"] < 60:
        score -= 8

    if truck["brake_oil_level"] < 30:
        score -= 15
    elif truck["brake_oil_level"] < 60:
        score -= 8

    if truck["battery_voltage"] < 12:
        score -= 15
    elif truck["battery_voltage"] < 12.3:
        score -= 8

    tyre_condition = str(truck["tyre_condition"]).lower()
    if tyre_condition == "poor":
        score -= 10
    elif tyre_condition == "moderate":
        score -= 5

    return max(score, 0)


def ensure_alerts_for_truck(truck_id: int) -> None:
    truck = query_one("SELECT * FROM trucks WHERE id = ?", (truck_id,))
    if not truck:
        return

    alert_rules = []
    if truck["diesel_percent"] < 10:
        alert_rules.append(("Diesel", f"Diesel below 10% for {truck['truck_name']}"))
    if truck["engine_oil_level"] < 30:
        alert_rules.append(("Engine Oil", f"Engine oil low for {truck['truck_name']}"))
    if truck["battery_voltage"] < 12:
        alert_rules.append(("Battery", f"Battery voltage below 12V for {truck['truck_name']}"))
    if truck["coolant_level"] < 30:
        alert_rules.append(("Coolant", f"Coolant low for {truck['truck_name']}"))
    if truck["brake_oil_level"] < 30:
        alert_rules.append(("Brake Oil", f"Brake oil low for {truck['truck_name']}"))
    if str(truck["tyre_condition"]).lower() == "poor":
        alert_rules.append(("Tyre", f"Tyre condition poor for {truck['truck_name']}"))

    existing = query_all(
        "SELECT alert_type FROM alerts WHERE truck_id = ? AND status = 'Open'",
        (truck_id,),
    )
    open_types = {row["alert_type"] for row in existing}

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for alert_type, message in alert_rules:
        if alert_type not in open_types:
            execute_sql(
                """
                INSERT INTO alerts (truck_id, alert_type, message, priority, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (truck_id, alert_type, message, "High", "Open", now),
            )


def calculate_estimate(trip_level: str, truck_type: str, load_weight: float) -> float:
    base_rate = RATE_MAP.get(trip_level, 22)
    multiplier = TRUCK_MULTIPLIER.get(truck_type, 1.0)
    weight_factor = max(load_weight, 1) * 100
    return round(base_rate * 100 + weight_factor * multiplier, 2)


def dashboard_context() -> dict[str, Any]:
    trucks = query_all("SELECT * FROM trucks ORDER BY category, truck_name")
    alerts = query_all(
        """
        SELECT alerts.*, trucks.truck_name, trucks.truck_number
        FROM alerts
        JOIN trucks ON alerts.truck_id = trucks.id
        ORDER BY alerts.id DESC
        """
    )
    drivers = query_all("SELECT * FROM drivers ORDER BY full_name")
    bookings = query_all("SELECT * FROM bookings ORDER BY id DESC LIMIT 8")
    toll_logs = query_all(
        """
        SELECT toll_logs.*, trucks.truck_name, trucks.truck_number
        FROM toll_logs
        JOIN trucks ON toll_logs.truck_id = trucks.id
        ORDER BY toll_logs.crossed_time DESC
        LIMIT 12
        """
    )

    enhanced_trucks = []
    for truck in trucks:
        item = dict(truck)
        item["health_score"] = get_health_score(truck)
        item["diesel_color"] = get_health_color(truck["diesel_percent"], "level")
        item["coolant_color"] = get_health_color(truck["coolant_level"], "level")
        item["engine_oil_color"] = get_health_color(truck["engine_oil_level"], "level")
        item["brake_oil_color"] = get_health_color(truck["brake_oil_level"], "level")
        item["battery_color"] = get_health_color(truck["battery_voltage"], "battery")
        enhanced_trucks.append(item)

    total_bookings_row = query_one("SELECT COUNT(*) AS total FROM bookings")
    total_bookings = total_bookings_row["total"] if total_bookings_row else 0
    total_toll_amount = sum(float(row["amount_paid"]) for row in toll_logs)
    pending_tolls = len([row for row in toll_logs if row["payment_status"] != "Paid"])
    active_bookings = len([row for row in bookings if row["status"] in ["New", "Confirmed", "In Transit"]])

    return {
        "trucks": enhanced_trucks,
        "alerts": alerts,
        "drivers": drivers,
        "bookings": bookings,
        "toll_logs": toll_logs,
        "total_trucks": len(enhanced_trucks),
        "active_trucks": len([t for t in enhanced_trucks if t["status"] == "Active"]),
        "alert_trucks": len([t for t in enhanced_trucks if t["status"] == "Alert"]),
        "service_due": len([t for t in enhanced_trucks if t["status"] == "Service Due"]),
        "total_bookings": total_bookings,
        "total_toll_amount": total_toll_amount,
        "pending_tolls": pending_tolls,
        "active_bookings": active_bookings,
    }


@app.route("/")
def index():
    recent_bookings = query_all("SELECT * FROM bookings ORDER BY id DESC LIMIT 4")
    return render_template(
        "index.html",
        truck_types=TRUCK_TYPES,
        trip_levels=TRIP_LEVELS,
        company_logos=COMPANY_LOGOS,
        recent_bookings=recent_bookings,
    )


@app.route("/trucks")
def trucks_page():
    return render_template("trucks.html", truck_types=TRUCK_TYPES, company_logos=COMPANY_LOGOS)


@app.route("/book-truck", methods=["POST"])
def book_truck():
    customer_name = request.form.get("customer_name", "").strip()
    mobile = request.form.get("mobile", "").strip()
    pickup_location = request.form.get("pickup_location", "").strip()
    drop_location = request.form.get("drop_location", "").strip()
    trip_level = request.form.get("trip_level", "").strip()
    truck_type = request.form.get("truck_type", "").strip()
    goods_type = request.form.get("goods_type", "").strip()
    load_weight_raw = request.form.get("load_weight", "0").strip()

    try:
        load_weight = float(load_weight_raw or 0)
    except ValueError:
        load_weight = 0

    if not all([customer_name, mobile, pickup_location, drop_location, trip_level, truck_type, goods_type]) or load_weight <= 0:
        flash("Please fill all booking details correctly.", "error")
        return redirect(url_for("index"))

    estimated_amount = calculate_estimate(trip_level, truck_type, load_weight)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    execute_sql(
        """
        INSERT INTO bookings (
            customer_name, mobile, pickup_location, drop_location,
            trip_level, truck_type, goods_type, load_weight,
            estimated_amount, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            customer_name,
            mobile,
            pickup_location,
            drop_location,
            trip_level,
            truck_type,
            goods_type,
            load_weight,
            estimated_amount,
            "New",
            created_at,
        ),
    )

    flash(f"Booking received successfully. Estimated amount: ₹{estimated_amount:,.0f}", "success")
    return redirect(url_for("index"))


@app.route("/owner/login", methods=["GET", "POST"])
def owner_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        owner = query_one("SELECT * FROM owners WHERE username = ? AND password = ?", (username, password))
        if owner:
            session.clear()
            session["owner_id"] = owner["id"]
            session["owner_name"] = owner["full_name"]
            return redirect(url_for("owner_dashboard"))
        flash("Invalid owner login details.", "error")
    return render_template("owner_login.html")


@app.route("/driver/login", methods=["GET", "POST"])
def driver_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        driver = query_one("SELECT * FROM drivers WHERE username = ? AND password = ?", (username, password))
        if driver:
            session.clear()
            session["driver_id"] = driver["id"]
            session["driver_name"] = driver["full_name"]
            return redirect(url_for("driver_app"))
        flash("Invalid driver login details.", "error")
    return render_template("driver_login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/owner/dashboard")
def owner_dashboard():
    if "owner_id" not in session:
        return redirect(url_for("owner_login"))

    for truck in query_all("SELECT id FROM trucks"):
        ensure_alerts_for_truck(truck["id"])

    return render_template("owner_dashboard.html", **dashboard_context())


@app.route("/owner/add-truck", methods=["POST"])
def add_truck():
    if "owner_id" not in session:
        return redirect(url_for("owner_login"))

    truck_name = request.form.get("truck_name", "").strip()
    truck_number = request.form.get("truck_number", "").strip()
    category = request.form.get("category", "").strip()
    driver_name = request.form.get("driver_name", "").strip()
    current_location = request.form.get("current_location", "").strip()

    try:
        capacity_tons = float(request.form.get("capacity_tons", "0").strip() or 0)
    except ValueError:
        capacity_tons = 0

    if not all([truck_name, truck_number, category, driver_name, current_location]) or capacity_tons <= 0:
        flash("Please fill all new truck details correctly.", "error")
        return redirect(url_for("owner_dashboard"))

    execute_sql(
        """
        INSERT INTO trucks (
            truck_name, truck_number, category, capacity_tons, driver_name,
            current_location, diesel_percent, coolant_level, engine_oil_level,
            brake_oil_level, battery_voltage, tyre_condition, status
        ) VALUES (?, ?, ?, ?, ?, ?, 100, 100, 100, 100, 12.8, 'Good', 'Active')
        """,
        (truck_name, truck_number, category, capacity_tons, driver_name, current_location),
    )

    flash("New truck added successfully.", "success")
    return redirect(url_for("owner_dashboard"))


@app.route("/owner/add-driver", methods=["POST"])
def add_driver():
    if "owner_id" not in session:
        return redirect(url_for("owner_login"))

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "driver123").strip()
    full_name = request.form.get("full_name", "").strip()
    mobile = request.form.get("mobile", "").strip()

    try:
        assigned_truck_id = int(request.form.get("assigned_truck_id", "0").strip() or 0)
    except ValueError:
        assigned_truck_id = 0

    if not all([username, password, full_name, mobile]) or assigned_truck_id <= 0:
        flash("Please fill all new driver details correctly.", "error")
        return redirect(url_for("owner_dashboard"))

    execute_sql(
        "INSERT INTO drivers (username, password, full_name, mobile, assigned_truck_id) VALUES (?, ?, ?, ?, ?)",
        (username, password, full_name, mobile, assigned_truck_id),
    )

    flash("New driver added successfully.", "success")
    return redirect(url_for("owner_dashboard"))


@app.route("/owner/update-toll-payment", methods=["POST"])
def update_toll_payment():
    if "owner_id" not in session:
        return redirect(url_for("owner_login"))

    try:
        toll_id = int(request.form.get("toll_id", "0").strip() or 0)
    except ValueError:
        toll_id = 0

    try:
        amount_paid = float(request.form.get("amount_paid", "0").strip() or 0)
    except ValueError:
        amount_paid = 0

    payment_method = request.form.get("payment_method", "").strip()
    payment_status = request.form.get("payment_status", "Paid").strip()

    if toll_id <= 0 or amount_paid <= 0 or not payment_method:
        flash("Please fill toll payment details correctly.", "error")
        return redirect(url_for("owner_dashboard"))

    execute_sql(
        """
        UPDATE toll_logs
        SET amount_paid = ?, payment_method = ?, payment_status = ?
        WHERE id = ?
        """,
        (amount_paid, payment_method, payment_status, toll_id),
    )

    flash("Toll payment updated successfully.", "success")
    return redirect(url_for("owner_dashboard"))


@app.route("/owner/update-booking-status", methods=["POST"])
def update_booking_status():
    if "owner_id" not in session:
        return redirect(url_for("owner_login"))

    try:
        booking_id = int(request.form.get("booking_id", "0").strip() or 0)
    except ValueError:
        booking_id = 0

    status = request.form.get("status", "").strip()
    if booking_id <= 0 or not status:
        flash("Please select booking and status.", "error")
        return redirect(url_for("owner_dashboard"))

    execute_sql("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
    flash("Booking status updated successfully.", "success")
    return redirect(url_for("owner_dashboard"))


@app.route("/owner/resolve-alert/<int:alert_id>", methods=["POST"])
def resolve_alert(alert_id: int):
    if "owner_id" not in session:
        return redirect(url_for("owner_login"))
    execute_sql("UPDATE alerts SET status = 'Resolved' WHERE id = ?", (alert_id,))
    flash("Alert marked as resolved.", "success")
    return redirect(url_for("owner_dashboard"))


@app.route("/driver/app")
def driver_app():
    if "driver_id" not in session:
        return redirect(url_for("driver_login"))

    driver = query_one("SELECT * FROM drivers WHERE id = ?", (session["driver_id"],))
    truck = query_one("SELECT * FROM trucks WHERE id = ?", (driver["assigned_truck_id"],)) if driver else None

    tyre_logs = query_all("SELECT * FROM tyre_logs WHERE driver_id = ? ORDER BY id DESC LIMIT 10", (session["driver_id"],))
    fuel_logs = query_all("SELECT * FROM fuel_logs WHERE driver_id = ? ORDER BY id DESC LIMIT 10", (session["driver_id"],))
    toll_entries = query_all(
        "SELECT * FROM toll_logs WHERE truck_id = ? ORDER BY id DESC LIMIT 10",
        (driver["assigned_truck_id"],),
    ) if driver else []

    return render_template(
        "driver_app.html",
        driver=driver,
        truck=truck,
        tyre_logs=tyre_logs,
        fuel_logs=fuel_logs,
        toll_entries=toll_entries,
    )


@app.route("/driver/tyre-log", methods=["POST"])
def add_tyre_log():
    if "driver_id" not in session:
        return redirect(url_for("driver_login"))

    driver = query_one("SELECT * FROM drivers WHERE id = ?", (session["driver_id"],))
    if not driver:
        return redirect(url_for("driver_login"))

    tyre_position = request.form.get("tyre_position", "").strip()
    reason = request.form.get("reason", "").strip()
    tyre_condition = request.form.get("tyre_condition", "Moderate").strip()

    if not all([tyre_position, reason]):
        flash("Please fill tyre log correctly.", "error")
        return redirect(url_for("driver_app"))

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_sql(
        "INSERT INTO tyre_logs (truck_id, driver_id, tyre_position, reason, created_at) VALUES (?, ?, ?, ?, ?)",
        (driver["assigned_truck_id"], driver["id"], tyre_position, reason, created_at),
    )

    execute_sql("UPDATE trucks SET tyre_condition = ? WHERE id = ?", (tyre_condition, driver["assigned_truck_id"]))
    ensure_alerts_for_truck(driver["assigned_truck_id"])
    flash("Tyre log updated successfully.", "success")
    return redirect(url_for("driver_app"))


@app.route("/driver/fuel-log", methods=["POST"])
def add_fuel_log():
    if "driver_id" not in session:
        return redirect(url_for("driver_login"))

    driver = query_one("SELECT * FROM drivers WHERE id = ?", (session["driver_id"],))
    if not driver:
        return redirect(url_for("driver_login"))

    bunk_name = request.form.get("bunk_name", "").strip()
    location = request.form.get("location", "").strip()

    try:
        litres = float(request.form.get("litres", "0").strip() or 0)
    except ValueError:
        litres = 0

    try:
        diesel_percent = float(request.form.get("diesel_percent", "100").strip() or 100)
    except ValueError:
        diesel_percent = 100

    if not all([bunk_name, location]) or litres <= 0:
        flash("Please fill fuel log correctly.", "error")
        return redirect(url_for("driver_app"))

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_sql(
        "INSERT INTO fuel_logs (truck_id, driver_id, litres, bunk_name, location, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (driver["assigned_truck_id"], driver["id"], litres, bunk_name, location, created_at),
    )

    diesel_percent = min(100, diesel_percent)
    execute_sql(
        "UPDATE trucks SET diesel_percent = ?, current_location = ? WHERE id = ?",
        (diesel_percent, location, driver["assigned_truck_id"]),
    )

    ensure_alerts_for_truck(driver["assigned_truck_id"])
    flash("Fuel log added successfully.", "success")
    return redirect(url_for("driver_app"))


@app.route("/driver/status-update", methods=["POST"])
def driver_status_update():
    if "driver_id" not in session:
        return redirect(url_for("driver_login"))

    driver = query_one("SELECT * FROM drivers WHERE id = ?", (session["driver_id"],))
    if not driver:
        return redirect(url_for("driver_login"))

    try:
        coolant_level = float(request.form.get("coolant_level", "0").strip() or 0)
        engine_oil_level = float(request.form.get("engine_oil_level", "0").strip() or 0)
        brake_oil_level = float(request.form.get("brake_oil_level", "0").strip() or 0)
        battery_voltage = float(request.form.get("battery_voltage", "0").strip() or 0)
    except ValueError:
        flash("Please enter valid truck health values.", "error")
        return redirect(url_for("driver_app"))

    current_location = request.form.get("current_location", "").strip()

    execute_sql(
        """
        UPDATE trucks
        SET coolant_level = ?, engine_oil_level = ?, brake_oil_level = ?, battery_voltage = ?, current_location = ?
        WHERE id = ?
        """,
        (coolant_level, engine_oil_level, brake_oil_level, battery_voltage, current_location, driver["assigned_truck_id"]),
    )

    ensure_alerts_for_truck(driver["assigned_truck_id"])
    flash("Truck health updated successfully.", "success")
    return redirect(url_for("driver_app"))


@app.route("/driver/location-update", methods=["POST"])
def driver_location_update():
    if "driver_id" not in session:
        return jsonify({"success": False, "message": "Login required"}), 401

    driver = query_one("SELECT * FROM drivers WHERE id = ?", (session["driver_id"],))
    if not driver:
        return jsonify({"success": False, "message": "Driver not found"}), 404

    data = request.get_json(silent=True) or {}
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    place = str(data.get("place", "")).strip()

    if latitude is None or longitude is None:
        return jsonify({"success": False, "message": "Location missing"}), 400

    current_location = f"{place} | {latitude}, {longitude}" if place else f"{latitude}, {longitude}"
    execute_sql("UPDATE trucks SET current_location = ? WHERE id = ?", (current_location, driver["assigned_truck_id"]))

    return jsonify({"success": True, "location": current_location})


@app.route("/driver/toll-entry", methods=["POST"])
def driver_toll_entry():
    if "driver_id" not in session:
        return redirect(url_for("driver_login"))

    driver = query_one("SELECT * FROM drivers WHERE id = ?", (session["driver_id"],))
    if not driver:
        return redirect(url_for("driver_login"))

    route_name = request.form.get("route_name", "").strip()
    toll_name = request.form.get("toll_name", "").strip()
    notes = request.form.get("notes", "").strip()

    if not route_name or not toll_name:
        flash("Please fill route name and tollgate name.", "error")
        return redirect(url_for("driver_app"))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_sql(
        """
        INSERT INTO toll_logs (
            truck_id, driver_name, route_name, toll_name, crossed_time,
            amount_paid, payment_method, payment_status, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (driver["assigned_truck_id"], driver["full_name"], route_name, toll_name, now, 0, "FASTag", "Pending", notes, now),
    )

    flash("Tollgate crossing saved successfully.", "success")
    return redirect(url_for("driver_app"))


@app.route("/api/trucks")
def api_trucks():
    trucks = []
    for truck in query_all("SELECT * FROM trucks ORDER BY category, truck_name"):
        item = dict(truck)
        item["health_score"] = get_health_score(truck)
        trucks.append(item)
    return jsonify(trucks)


@app.route("/api/bookings")
def api_bookings():
    return jsonify([dict(b) for b in query_all("SELECT * FROM bookings ORDER BY id DESC")])


@app.route("/api/alerts")
def api_alerts():
    return jsonify([dict(a) for a in query_all("SELECT * FROM alerts ORDER BY id DESC")])


@app.route("/api/drivers")
def api_drivers():
    return jsonify([dict(d) for d in query_all("SELECT * FROM drivers ORDER BY full_name")])


@app.route("/api/fuel-logs")
def api_fuel_logs():
    return jsonify([dict(f) for f in query_all("SELECT * FROM fuel_logs ORDER BY id DESC")])


@app.route("/api/tyre-logs")
def api_tyre_logs():
    return jsonify([dict(t) for t in query_all("SELECT * FROM tyre_logs ORDER BY id DESC")])


@app.route("/api/toll-logs")
def api_toll_logs():
    toll_logs = query_all(
        """
        SELECT toll_logs.*, trucks.truck_name, trucks.truck_number
        FROM toll_logs
        JOIN trucks ON toll_logs.truck_id = trucks.id
        ORDER BY toll_logs.crossed_time DESC
        """
    )
    return jsonify([dict(t) for t in toll_logs])


@app.route("/api/dashboard-summary")
def api_dashboard_summary():
    data = dashboard_context()
    return jsonify(
        {
            "active_bookings": data["active_bookings"],
            "pending_tolls": data["pending_tolls"],
            "total_toll_amount": data["total_toll_amount"],
            "alerts_count": len(data["alerts"]),
        }
    )


@app.route("/api/calculate-estimate", methods=["POST"])
def api_calculate_estimate():
    data = request.get_json(silent=True) or {}
    trip_level = str(data.get("trip_level", "")).strip()
    truck_type = str(data.get("truck_type", "")).strip()
    try:
        load_weight = float(data.get("load_weight", 0) or 0)
    except ValueError:
        load_weight = 0

    estimate = calculate_estimate(trip_level, truck_type, load_weight)
    return jsonify(
        {
            "trip_level": trip_level,
            "truck_type": truck_type,
            "load_weight": load_weight,
            "estimated_amount": estimate,
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

if __name__ == "__main__":
    init_db()
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)