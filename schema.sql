DROP TABLE IF EXISTS owners;
DROP TABLE IF EXISTS drivers;
DROP TABLE IF EXISTS trucks;
DROP TABLE IF EXISTS fuel_logs;
DROP TABLE IF EXISTS tyre_logs;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS bookings;

CREATE TABLE owners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL
);

CREATE TABLE drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    mobile TEXT,
    assigned_truck_id INTEGER,
    FOREIGN KEY (assigned_truck_id) REFERENCES trucks(id)
);

CREATE TABLE trucks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_name TEXT NOT NULL,
    truck_number TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    capacity_tons REAL NOT NULL,
    driver_name TEXT,
    current_location TEXT,
    diesel_percent REAL DEFAULT 100,
    coolant_level REAL DEFAULT 100,
    engine_oil_level REAL DEFAULT 100,
    brake_oil_level REAL DEFAULT 100,
    battery_voltage REAL DEFAULT 12.8,
    tyre_condition TEXT DEFAULT 'Good',
    status TEXT DEFAULT 'Active'
);

CREATE TABLE fuel_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    litres REAL NOT NULL,
    bunk_name TEXT NOT NULL,
    location TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (truck_id) REFERENCES trucks(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id)
);

CREATE TABLE tyre_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    tyre_position TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (truck_id) REFERENCES trucks(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id)
);

CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL,
    message TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT DEFAULT 'Open',
    created_at TEXT NOT NULL,
    FOREIGN KEY (truck_id) REFERENCES trucks(id)
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    mobile TEXT NOT NULL,
    pickup_location TEXT NOT NULL,
    drop_location TEXT NOT NULL,
    trip_level TEXT NOT NULL,
    truck_type TEXT NOT NULL,
    goods_type TEXT NOT NULL,
    load_weight REAL NOT NULL,
    estimated_amount REAL NOT NULL,
    status TEXT DEFAULT 'New',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS toll_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id INTEGER NOT NULL,
    driver_name TEXT NOT NULL,
    route_name TEXT NOT NULL,
    toll_name TEXT NOT NULL,
    crossed_time TEXT NOT NULL,
    amount_paid REAL NOT NULL,
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL
);