# IIoT Predictive Maintenance System - Documentation

## Project Overview

This is a **simulated Industrial IoT (IIoT) system** that monitors factory machines and predicts when they might fail, enabling proactive maintenance before breakdowns occur.

---

## System Architecture

### Three Main Components

#### 1. Sensor Simulator (`sensor_simulator.py`)
**Purpose:** Simulates factory machines with sensors

**What it does:**
- Creates 3 virtual industrial machines that generate realistic sensor data
- Measures multiple parameters:
  - Temperature (°C)
  - Vibration (mm/s)
  - Electrical Current (Amperes)
  - Pressure (Bar)
  - RPM (Rotations Per Minute)
- One machine is programmed to gradually degrade over time (simulating wear and tear)
- Publishes data every 3 seconds via MQTT protocol
- Uses a public MQTT broker (broker.hivemq.com) for communication

**Key Features:**
- Realistic sensor noise and daily load variations
- Gradual degradation simulation for predictive maintenance testing
- Color-coded status indicators (🟢 Normal, 🟡 Warning, 🔴 Critical)

**Think of it as:** A video game simulation of factory equipment

---

#### 2. ML Monitor (`ml_monitor.py`)
**Purpose:** Intelligent anomaly detection system

**What it does:**
- Subscribes to sensor data from all machines via MQTT
- Collects baseline data (first 30 readings) to understand "normal" operation
- Trains a Machine Learning model (Isolation Forest algorithm) to detect anomalies
- Analyzes every incoming sensor reading in real-time
- Generates alerts when abnormal patterns are detected
- Publishes alerts with severity levels and maintenance recommendations

**Machine Learning Details:**
- **Algorithm:** Isolation Forest (unsupervised anomaly detection)
- **Features:** Temperature, Vibration, Current, Pressure, RPM
- **Training:** Auto-trains after 30 samples
- **Contamination Rate:** 15% (expected anomaly rate)
- **Model Persistence:** Saves trained model to `models/anomaly_detector.pkl`

**Alert Severity Levels:**
- 🔴 **CRITICAL**: Anomaly score < -0.5
- 🟡 **WARNING**: Anomaly score < -0.3
- 🔵 **INFO**: Anomaly score ≥ -0.3

**Think of it as:** A smart security guard watching monitors and raising alarms when something's wrong

---

#### 3. Web Dashboard (`dashboard.py` + `dashboard.html`)
**Purpose:** Real-time visualization and monitoring interface

**What it does:**
- Runs a Flask web server on port 5000
- Provides a web-based control panel accessible at `http://localhost:5000`
- Displays live sensor data from all machines
- Shows real-time alerts and anomalies
- Maintains historical data (last 50 readings per machine, last 100 alerts)
- Updates automatically without page refresh using WebSockets

**API Endpoints:**
- `/` - Main dashboard page
- `/api/data` - Complete system data
- `/api/machines` - List of all machines with current status
- `/api/alerts` - Recent alerts (last 20)
- `/api/statistics` - System statistics

**Real-time Features:**
- WebSocket connection for instant updates
- Live charts and graphs
- Machine status indicators
- Alert notifications

**Think of it as:** Mission control center for your factory

---

## Data Flow

```
┌─────────────────┐
│ Sensor Simulator│
│  (3 Machines)   │
└────────┬────────┘
         │ Publishes sensor data
         │ every 3 seconds
         ↓
┌─────────────────┐
│  MQTT Broker    │
│ (HiveMQ Public) │
└────┬───────┬────┘
     │       │
     │       │ Subscribes to sensors
     │       ↓
     │   ┌──────────────┐
     │   │  ML Monitor  │
     │   │ (Analyzes)   │
     │   └──────┬───────┘
     │          │
     │          │ Publishes alerts
     │          ↓
     │   ┌──────────────┐
     │   │ MQTT Broker  │
     │   └──────────────┘
     │          │
     └──────┬───┘
            │ Both subscribe
            ↓
    ┌───────────────┐
    │   Dashboard   │
    │ (Flask + WS)  │
    └───────┬───────┘
            │
            ↓
    ┌───────────────┐
    │ Web Browser   │
    │ localhost:5000│
    └───────────────┘
```

---

## Technology Stack

### Backend
- **Python 3.x** - Main programming language
- **Paho MQTT** - MQTT client library for IoT messaging
- **Flask** - Web framework for HTTP server
- **Flask-SocketIO** - WebSocket support for real-time updates
- **Scikit-learn** - Machine Learning library (Isolation Forest)
- **NumPy** - Numerical computing

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling
- **JavaScript** - Interactivity
- **Socket.IO** - WebSocket client

### Communication
- **MQTT Protocol** - Lightweight messaging for IoT devices
- **WebSockets** - Real-time bidirectional communication
- **REST API** - HTTP endpoints for data retrieval

---

## How to Run the System

### Prerequisites
Install required packages:
```bash
pip install paho-mqtt flask flask-socketio scikit-learn numpy
```

### Execution Order

**Terminal 1 - Start Sensor Simulator:**
```bash
python sensor_simulator.py
```
*This will start generating sensor data from 3 machines*

**Terminal 2 - Start ML Monitor:**
```bash
python ml_monitor.py
```
*This will start analyzing data and detecting anomalies*

**Terminal 3 - Start Dashboard:**
```bash
python dashboard.py
```
*This will start the web server*

**Browser:**
Open `http://localhost:5000` to view the dashboard

---

## Key Features

### Predictive Maintenance
- Detects anomalies before complete failure
- Provides early warning for degrading equipment
- Recommends specific maintenance actions

### Real-time Monitoring
- Live sensor data visualization
- Instant alert notifications
- No page refresh needed

### Machine Learning
- Unsupervised learning (no labeled data needed)
- Automatically adapts to "normal" behavior
- Continuous anomaly detection

### Scalability
- Easily add more machines
- Modular architecture
- Cloud-ready (can use any MQTT broker)

---

## Real-World Applications

### Manufacturing
- Monitor assembly line equipment
- Predict motor failures
- Reduce unplanned downtime

### Energy
- Monitor turbines and generators
- Detect bearing wear
- Optimize maintenance schedules

### Transportation
- Fleet vehicle monitoring
- Engine health tracking
- Preventive maintenance

### Benefits
- **Cost Savings**: Fix before breaking (cheaper than emergency repairs)
- **Safety**: Prevent accidents from equipment failure
- **Efficiency**: Optimize maintenance schedules
- **Uptime**: Reduce unexpected downtime

---

## Project Structure

```
IOT/
├── sensor_simulator.py      # Simulates industrial machines
├── ml_monitor.py            # ML-based anomaly detection
├── dashboard.py             # Flask web server
├── templates/
│   └── dashboard.html       # Web interface
├── models/                  # Saved ML models
├── logs/                    # System logs
└── requirements.txt         # Python dependencies
```

---

## Configuration

### Sensor Simulator
- `NUM_MACHINES`: Number of machines to simulate (default: 3)
- `INTERVAL_SECONDS`: Time between readings (default: 3)
- `DURATION_MINUTES`: Run duration (default: None = infinite)

### ML Monitor
- `min_training_samples`: Samples needed before training (default: 30)
- `contamination`: Expected anomaly rate (default: 0.15)
- `n_estimators`: Number of trees in Isolation Forest (default: 100)

### Dashboard
- `host`: Server host (default: '0.0.0.0')
- `port`: Server port (default: 5000)
- `debug`: Debug mode (default: False)

---

## MQTT Topics

### Published Topics
- `factory/machines/{MACHINE_ID}/sensors` - Individual machine sensor data
- `factory/sensors/temperature` - Temperature readings
- `factory/alerts/anomaly` - Anomaly alerts

### Subscribed Topics
- `factory/machines/+/sensors` - All machine sensors (+ is wildcard)
- `factory/alerts/anomaly` - Anomaly alerts

---

## Understanding the Output

### Sensor Simulator Console
```
🟢 MACHINE_001: Temp=67.2°C, Vib=2.15mm/s, Curr=10.3A, Degrade=0.0%
🟢 MACHINE_002: Temp=65.8°C, Vib=2.03mm/s, Curr=9.8A, Degrade=0.0%
🔴 MACHINE_003: Temp=82.4°C, Vib=4.67mm/s, Curr=14.2A, Degrade=78.3%
```
- 🟢 Normal operation (degradation < 20%)
- 🟡 Warning (degradation 20-50%)
- 🔴 Critical (degradation > 50%)

### ML Monitor Console
```
✓ MACHINE_001: Normal operation | T=67.2°C, V=2.15mm/s, I=10.3A

🔴 ANOMALY DETECTED!
Alert ID: ALERT_0042
Machine: MACHINE_003
Severity: CRITICAL
Anomaly Score: -0.6234
💡 Recommendation: Schedule inspection: Temperature exceeds safe threshold; Excessive vibration detected
```

---

## Why This Matters

### Traditional Maintenance (Reactive)
- Wait for equipment to break
- Expensive emergency repairs
- Unplanned downtime
- Potential safety hazards

### Predictive Maintenance (Proactive)
- Fix before breaking
- Scheduled maintenance
- Optimized costs
- Improved safety

**This system is like getting a check engine light before your car actually breaks down, not after.**

---

## Future Enhancements

- Historical data analytics and trends
- Multiple ML algorithms comparison
- Email/SMS alert notifications
- Mobile app integration
- Cloud deployment (Azure IoT Hub, AWS IoT Core)
- Database storage (PostgreSQL, InfluxDB)
- Advanced visualizations (Grafana integration)
- Maintenance scheduling system
- Cost impact analysis

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'paho'"
**Solution:** Install required packages
```bash
pip install paho-mqtt flask flask-socketio scikit-learn numpy
```

### "Site not found" when accessing localhost:5000
**Solution:** Dashboard server is not running. Execute:
```bash
python dashboard.py
```

### No alerts appearing
**Solution:** 
- Wait for ML model to train (needs 30 readings)
- Check that all three programs are running
- Verify MQTT connection messages

### MQTT connection failed
**Solution:**
- Check internet connection
- Try alternative broker: `test.mosquitto.org`
- Ensure port 1883 is not blocked by firewall

---

## License & Credits

**Academic Project** - IoT & Machine Learning Integration
**Semester 5** - Internet of Things Course
**Technologies:** Python, MQTT, Flask, Scikit-learn

---

*Last Updated: November 21, 2025*
