╔══════════════════════════════════════════════════════════╗
║         IMPLEMENTATION STEPS - SMART PARKING            ║
╚══════════════════════════════════════════════════════════╝

STEP 1: Setup Environment
─────────────────────────
  1. Install Python 3.9+ from python.org
  2. Open terminal / command prompt
  3. Create project folder:
       mkdir smart_parking
       cd smart_parking
  4. Create virtual environment:
       python -m venv venv
  5. Activate it:
       Windows:  venv\Scripts\activate
       Mac/Linux: source venv/bin/activate
  6. Install dependencies:
       pip install -r requirements.txt

STEP 2: Train the ML Model
───────────────────────────
  python predict.py

  Expected output:
  ✓ Training with XX records from CSV file.
  ✓ Model Accuracy: 75-85%
  ✓ Model saved to model/parking_model.pkl

STEP 3: Run the Application
────────────────────────────
  python app.py

  Expected output:
  ✓ Database initialized successfully.
  ✓ Training ML model...
  ✓ Starting Flask server...
  ✓ Running on http://127.0.0.1:5000

STEP 4: Test the Application
──────────────────────────────
  Open browser → http://127.0.0.1:5000

  Login as Admin:
    Username: admin
    Password: admin123

  Login as User:
    Username: user1
    Password: user123

STEP 5: Test Features
──────────────────────
  ✓ View parking slots (user & admin)
  ✓ Update slot status (admin only)
  ✓ Click "Simulate Sensors" button
  ✓ Click "Retrain ML Model" button
  ✓ View predictions page
  ✓ Check occupancy trend chart
