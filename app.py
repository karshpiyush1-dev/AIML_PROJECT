from flask import (
    Flask, render_template, request,
    redirect, url_for, session, jsonify, flash
)
from database import (
    init_db, get_all_slots, get_slot,
    update_slot, get_history, get_user, get_stats
)
from predict import (
    predict_availability, predict_all_slots,
    train_model, get_occupancy_trend
)
import random
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'parking_secret_key_2024'

# ─────────────────────────────────────────────
# Decorators
# ─────────────────────────────────────────────

def login_required(f):
    """Ensure user is logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Ensure user is admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('user_view'))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────
# Authentication Routes
# ─────────────────────────────────────────────

@app.route('/')
def index():
    if 'user' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('dashboard'))
        return redirect(url_for('user_view'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = get_user(username)

        if user and user['password'] == password:
            session['user'] = username
            session['role'] = user['role']
            flash(f'Welcome, {username}!', 'success')

            if user['role'] == 'admin':
                return redirect(url_for('dashboard'))
            return redirect(url_for('user_view'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ─────────────────────────────────────────────
# User Routes
# ─────────────────────────────────────────────

@app.route('/parking')
@login_required
def user_view():
    slots = get_all_slots()
    stats = get_stats()
    return render_template('user_view.html', slots=slots, stats=stats)

@app.route('/predict')
@login_required
def prediction_view():
    predictions = predict_all_slots()
    trend = get_occupancy_trend()
    return render_template('prediction.html',
                           predictions=predictions,
                           trend=trend)

# ─────────────────────────────────────────────
# Admin Routes
# ─────────────────────────────────────────────

@app.route('/dashboard')
@admin_required
def dashboard():
    slots = get_all_slots()
    stats = get_stats()
    history = get_history(20)
    return render_template('dashboard.html',
                           slots=slots,
                           stats=stats,
                           history=history)

@app.route('/update_slot', methods=['POST'])
@admin_required
def update_slot_route():
    slot_number = request.form.get('slot_number')
    is_occupied = int(request.form.get('is_occupied', 0))

    if slot_number:
        update_slot(slot_number, is_occupied)
        status = 'Occupied' if is_occupied else 'Available'
        flash(f'Slot {slot_number} marked as {status}.', 'success')
    else:
        flash('Invalid slot number.', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/simulate_sensors')
@admin_required
def simulate_sensors():
    """Simulate random sensor data for all slots."""
    slots = get_all_slots()
    for slot in slots:
        # Randomly set occupied or free (60% chance of being occupied)
        is_occupied = random.choices([0, 1], weights=[40, 60])[0]
        update_slot(slot['slot_number'], is_occupied)

    flash('Sensor simulation complete! Slot data updated randomly.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/train_model')
@admin_required
def retrain_model():
    """Retrain ML model with latest data."""
    try:
        model, accuracy = train_model()
        flash(f'Model retrained successfully! Accuracy: {accuracy*100:.2f}%',
              'success')
    except Exception as e:
        flash(f'Model training failed: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))

# ─────────────────────────────────────────────
# API Routes (JSON)
# ─────────────────────────────────────────────

@app.route('/api/slots')
@login_required
def api_slots():
    """API endpoint: Get all slot statuses."""
    slots = get_all_slots()
    data = [
        {
            'slot_number': s['slot_number'],
            'is_occupied': s['is_occupied'],
            'updated_at': s['updated_at']
        }
        for s in slots
    ]
    return jsonify({'slots': data, 'stats': get_stats()})

@app.route('/api/predict/<slot_number>')
@login_required
def api_predict(slot_number):
    """API endpoint: Predict availability for a slot."""
    result = predict_availability(slot_number)
    return jsonify(result)

@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint: Get parking statistics."""
    return jsonify(get_stats())

# ─────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────

if __name__ == '__main__':
    print("Initializing database...")
    init_db()

    print("Training ML model...")
    try:
        train_model()
    except Exception as e:
        print(f"Warning: Model training skipped - {e}")

    print("Starting Flask server...")
    app.run(debug=True, port=5000)