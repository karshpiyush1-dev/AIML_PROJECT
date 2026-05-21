import sqlite3
from datetime import datetime

DATABASE = 'parking.db'

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables and default data."""
    conn = get_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')

    # Create parking slots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_number TEXT NOT NULL UNIQUE,
            is_occupied INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create historical data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_number TEXT NOT NULL,
            is_occupied INTEGER NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            day_of_week INTEGER,
            hour_of_day INTEGER
        )
    ''')

    # Insert default admin user (password: admin123)
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role)
        VALUES (?, ?, ?)
    ''', ('admin', 'admin123', 'admin'))

    # Insert default regular user (password: user123)
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role)
        VALUES (?, ?, ?)
    ''', ('user1', 'user123', 'user'))

    # Insert default parking slots
    slots = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3', 'D1']
    for slot in slots:
        cursor.execute('''
            INSERT OR IGNORE INTO parking_slots (slot_number, is_occupied)
            VALUES (?, 0)
        ''', (slot,))

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def get_all_slots():
    """Get all parking slots."""
    conn = get_db()
    slots = conn.execute(
        'SELECT * FROM parking_slots ORDER BY slot_number'
    ).fetchall()
    conn.close()
    return slots

def get_slot(slot_number):
    """Get a specific parking slot."""
    conn = get_db()
    slot = conn.execute(
        'SELECT * FROM parking_slots WHERE slot_number = ?',
        (slot_number,)
    ).fetchone()
    conn.close()
    return slot

def update_slot(slot_number, is_occupied):
    """Update parking slot status and save to history."""
    now = datetime.now()
    conn = get_db()

    # Update current status
    conn.execute('''
        UPDATE parking_slots
        SET is_occupied = ?, updated_at = ?
        WHERE slot_number = ?
    ''', (is_occupied, now, slot_number))

    # Save to history
    conn.execute('''
        INSERT INTO parking_history
        (slot_number, is_occupied, recorded_at, day_of_week, hour_of_day)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        slot_number,
        is_occupied,
        now,
        now.weekday(),
        now.hour
    ))

    conn.commit()
    conn.close()

def get_history(limit=100):
    """Get recent parking history."""
    conn = get_db()
    history = conn.execute('''
        SELECT * FROM parking_history
        ORDER BY recorded_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return history

def get_user(username):
    """Get user by username."""
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    conn.close()
    return user

def get_stats():
    """Get basic parking statistics."""
    conn = get_db()
    total = conn.execute(
        'SELECT COUNT(*) as count FROM parking_slots'
    ).fetchone()['count']

    occupied = conn.execute(
        'SELECT COUNT(*) as count FROM parking_slots WHERE is_occupied = 1'
    ).fetchone()['count']

    conn.close()
    return {
        'total': total,
        'occupied': occupied,
        'available': total - occupied
    }
