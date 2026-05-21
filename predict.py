import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import sqlite3
import os
from datetime import datetime

MODEL_PATH = 'model/parking_model.pkl'
DATA_PATH  = 'data/sample_data.csv'

def load_data_from_csv():
    df = pd.read_csv(DATA_PATH)
    return df

def load_data_from_db():
    conn = sqlite3.connect('parking.db')
    df = pd.read_sql_query(
        '''SELECT slot_number, day_of_week,
                  hour_of_day, is_occupied
           FROM parking_history''',
        conn
    )
    conn.close()
    return df

def train_model():
    # Load data
    try:
        db_data = load_data_from_db()
        if len(db_data) > 200:
            df = db_data
            print(f"Training with {len(df)} records from database.")
        else:
            raise ValueError("Not enough database records.")
    except Exception:
        df = load_data_from_csv()
        print(f"Training with {len(df)} records from CSV.")

    # Encode slot number to integer
    slot_categories = sorted(df['slot_number'].unique())
    slot_map = {name: idx for idx, name in enumerate(slot_categories)}
    df['slot_code'] = df['slot_number'].map(slot_map)

    # Save slot map for prediction use
    joblib.dump(slot_map, 'model/slot_map.pkl')

    # Features and target
    X = df[['slot_code', 'day_of_week', 'hour_of_day']]
    y = df['is_occupied']

    # Split data — 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y       # Keep class balance in split
    )

    # Train Random Forest with better settings
    model = RandomForestClassifier(
        n_estimators=200,    # More trees = better accuracy
        random_state=42,
        max_depth=10,        # Deeper trees learn more patterns
        min_samples_split=2,
        min_samples_leaf=1,
        class_weight='balanced'  # Handle any class imbalance
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred    = model.predict(X_test)
    accuracy  = accuracy_score(y_test, y_pred)

    print(f"\nModel Accuracy  : {accuracy * 100:.2f}%")
    print("\nDetailed Report:")
    print(classification_report(y_test, y_pred,
                                target_names=['Available','Occupied']))

    # Save model
    os.makedirs('model', exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved → {MODEL_PATH}")

    return model, accuracy

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    else:
        print("No saved model found. Training now...")
        model, _ = train_model()
        return model

def load_slot_map():
    if os.path.exists('model/slot_map.pkl'):
        return joblib.load('model/slot_map.pkl')
    # Default fallback map
    return {
        'A1': 0, 'A2': 1, 'A3': 2,
        'B1': 3, 'B2': 4, 'B3': 5,
        'C1': 6, 'C2': 7, 'C3': 8,
        'D1': 9
    }

def predict_availability(slot_number, hour=None, day=None):
    model    = load_model()
    slot_map = load_slot_map()

    now = datetime.now()
    if hour is None:
        hour = (now.hour + 1) % 24
    if day is None:
        day = now.weekday()

    slot_code = slot_map.get(slot_number, 0)
    features  = np.array([[slot_code, day, hour]])

    prediction  = model.predict(features)[0]
    probability = model.predict_proba(features)[0]

    # Handle both cases where model has 1 or 2 classes
    if len(probability) == 2:
        prob_occupied = float(probability[1])
    else:
        prob_occupied = float(probability[0])

    return {
        'slot_number'         : slot_number,
        'predicted_hour'      : hour,
        'day_of_week'         : day,
        'will_be_occupied'    : bool(prediction),
        'probability_occupied': round(prob_occupied * 100, 2),
        'probability_available': round((1 - prob_occupied) * 100, 2),
        'status': 'Likely Occupied' if prediction == 1 else 'Likely Available'
    }

def predict_all_slots():
    slots = ['A1','A2','A3','B1','B2','B3','C1','C2','C3','D1']
    return [predict_availability(s) for s in slots]

def get_occupancy_trend():
    try:
        df    = load_data_from_csv()
        trend = df.groupby('hour_of_day')['is_occupied'] \
                  .mean().reset_index()
        trend.columns = ['hour', 'occupancy_rate']
        trend['occupancy_rate'] = (trend['occupancy_rate'] * 100).round(2)
        return trend.to_dict(orient='records')
    except Exception as e:
        print(f"Trend error: {e}")
        return []

if __name__ == '__main__':
    print("=" * 50)
    print("  Training Smart Parking ML Model")
    print("=" * 50)
    model, accuracy = train_model()

    print("\nSample Predictions (next hour):")
    print("-" * 40)
    for p in predict_all_slots():
        status = "🔴 Occupied " if p['will_be_occupied'] else "🟢 Available"
        print(f"  Slot {p['slot_number']} → {status} "
              f"({p['probability_available']}% free)")