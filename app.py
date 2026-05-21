from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, jsonify
)
from database import (
    init_db, get_all_slots, get_slot,
    update_slot, get_history, get_stats
)
from predict import (
    predict_availability, predict_all_slots,
    train_model, get_occupancy_trend
)
import random

app = Flask(__name__)
app.secret_key = 'parking_secret_key_2024'

# ─────────────────────────────────────────────
# Main Routes
# ─────────────────────────────────────────────

@app.route('/')
def index():
    # Go directly to dashboard
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    slots   = get_all_slots()
    stats   = get_stats()
    history = get_history(20)
    return render_template('dashboard.html',
                           slots=slots,
                           stats=stats,
                           history=history)

@app.route('/parking')
def user_view():
    slots = get_all_slots()
    stats = get_stats()
    return render_template('user_view.html',
                           slots=slots,
                           stats=stats)

@app.route('/predict')
def prediction_view():
    predictions = predict_all_slots()
    trend       = get_occupancy_trend()
    return render_template('prediction.html',
                           predictions=predictions,
                           trend=trend)

# ─────────────────────────────────────────────
# Admin Action Routes
# ─────────────────────────────────────────────

@app.route('/update_slot', methods=['POST'])
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
def simulate_sensors():
    slots = get_all_slots()
    for slot in slots:
        is_occupied = random.choices([0, 1], weights=[40, 60])[0]
        update_slot(slot['slot_number'], is_occupied)

    flash('Sensor simulation complete! Slot data updated randomly.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/train_model')
def retrain_model():
    try:
        model, accuracy = train_model()
        flash(f'Model retrained successfully! Accuracy: {accuracy*100:.2f}%',
              'success')
    except Exception as e:
        flash(f'Model training failed: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))

# ─────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────

@app.route('/api/slots')
def api_slots():
    slots = get_all_slots()
    data  = [
        {
            'slot_number': s['slot_number'],
            'is_occupied': s['is_occupied'],
            'updated_at' : s['updated_at']
        }
        for s in slots
    ]
    return jsonify({'slots': data, 'stats': get_stats()})

@app.route('/api/predict/<slot_number>')
def api_predict(slot_number):
    result = predict_availability(slot_number)
    return jsonify(result)

@app.route('/api/stats')
def api_stats():
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