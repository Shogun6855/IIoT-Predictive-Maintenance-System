# IIoT Predictive Maintenance System

> Real-time machine monitoring and anomaly detection using Machine Learning

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

---

## 📋 Overview

An **Industrial IoT (IIoT) predictive maintenance system** that simulates factory equipment, monitors sensor data in real-time, and uses Machine Learning to predict equipment failures before they happen.

### Key Features

- 🏭 **Virtual Industrial Machines** - Simulates realistic sensor data from factory equipment
- 🤖 **ML-Powered Anomaly Detection** - Isolation Forest algorithm identifies abnormal patterns
- 📊 **Real-time Dashboard** - Live web interface with charts and alerts
- ⚡ **Instant Notifications** - WebSocket-based real-time updates
- 🔔 **Smart Alerts** - Prioritized alerts with maintenance recommendations

---

## 🎯 What Problem Does This Solve?

### Traditional Maintenance ❌
- Wait for equipment to break
- Expensive emergency repairs
- Unplanned production downtime
- Safety risks

### Predictive Maintenance ✅
- Detect issues before failure
- Scheduled maintenance
- Reduced downtime
- Lower costs
- Improved safety

---

## 🏗️ System Architecture

```
┌─────────────────────┐
│  Sensor Simulator   │  ← Generates realistic sensor data
│   (3 Machines)      │
└──────────┬──────────┘
           │
           ↓ MQTT
┌─────────────────────┐
│   MQTT Broker       │  ← Message routing
│  (HiveMQ Cloud)     │
└─────┬─────────┬─────┘
      │         │
      │         ↓
      │  ┌──────────────────┐
      │  │   ML Monitor     │  ← Anomaly detection
      │  │ (Isolation Forest)│
      │  └──────────┬───────┘
      │             │
      │             ↓ Alerts
      └─────────────┤
                    ↓
           ┌────────────────┐
           │   Dashboard    │  ← Web visualization
           │  (Flask + WS)  │
           └────────┬───────┘
                    │
                    ↓
            [Your Browser]
         http://localhost:5000
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Internet connection (for MQTT broker)

### Installation

1. **Clone or download this project**
   ```bash
   cd IOT
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the System

Open **3 separate terminals** and run:

**Terminal 1 - Sensor Simulator:**
```bash
python sensor_simulator.py
```

**Terminal 2 - ML Monitor:**
```bash
python ml_monitor.py
```

**Terminal 3 - Dashboard:**
```bash
python dashboard.py
```

**Open your browser:**
```
http://localhost:5000
```

---

## 📦 Project Structure

```
IOT/
├── sensor_simulator.py      # Virtual sensor data generator
├── ml_monitor.py            # ML anomaly detection engine
├── dashboard.py             # Flask web server
├── templates/
│   └── dashboard.html       # Real-time web interface
├── models/                  # Saved ML models
├── logs/                    # System logs
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── PROJECT_DOCUMENTATION.md # Detailed technical docs
```

---

## 🔧 How It Works

### 1. Data Generation
- 3 virtual machines generate sensor readings every 3 seconds
- **Sensors monitored:**
  - 🌡️ Temperature (°C)
  - 📳 Vibration (mm/s)
  - ⚡ Current (Amperes)
  - 🔧 Pressure (Bar)
  - 🔄 RPM

### 2. Machine Learning
- Collects first 30 readings to learn "normal" behavior
- Trains Isolation Forest model
- Analyzes each new reading for anomalies
- Detects unusual patterns across all 5 sensors

### 3. Real-time Monitoring
- Dashboard displays live sensor data
- Charts show historical trends
- Color-coded status indicators
- Instant alerts when anomalies detected

---

## 📊 Dashboard Features

### Machine Status Cards
- Current sensor readings
- Status indicator (Normal/Anomaly)
- Real-time metric updates

### Live Charts
- Temperature trends over time
- Interactive graphs
- Historical data visualization

### Alert Feed
- Anomaly notifications
- Severity levels (Critical/Warning/Info)
- Maintenance recommendations
- Timestamp tracking

### Statistics Panel
- Total readings processed
- Anomalies detected
- Active machines count
- System health metrics

---

## 🧠 Machine Learning Details

### Algorithm: Isolation Forest

**Why Isolation Forest?**
- ✅ Unsupervised learning (no labeled data needed)
- ✅ Excellent for anomaly detection
- ✅ Fast and scalable
- ✅ Handles multi-dimensional data

**How it works:**
1. Learns normal patterns from initial data
2. Creates decision trees to isolate anomalies
3. Assigns anomaly score to each reading
4. Flags unusual patterns for investigation

**Training:**
- Minimum samples: 30 readings
- Features: 5 sensor parameters
- Contamination rate: 15%
- Trees: 100 estimators

---

## 📈 Use Cases

### Manufacturing
- Assembly line monitoring
- CNC machine health
- Conveyor system tracking

### Energy
- Turbine monitoring
- Generator health
- Power distribution

### Automotive
- Fleet management
- Engine diagnostics
- Vehicle health monitoring

### HVAC
- Chiller systems
- Air handler monitoring
- Pump stations

---

## 🎨 Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.8+ |
| **ML** | Scikit-learn (Isolation Forest) |
| **Web Framework** | Flask |
| **Real-time** | Flask-SocketIO, WebSockets |
| **IoT Protocol** | MQTT (Paho) |
| **Data Processing** | NumPy, Pandas |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Visualization** | Chart.js (via templates) |

---

## 📱 Screenshots

### Dashboard Overview
- Real-time machine monitoring
- Live sensor metrics
- Status indicators

### Anomaly Detection
- Instant alerts
- Severity classification
- Maintenance recommendations

---

## ⚙️ Configuration

### Sensor Simulator
```python
NUM_MACHINES = 3          # Number of virtual machines
INTERVAL_SECONDS = 3      # Time between readings
DURATION_MINUTES = None   # Run duration (None = infinite)
```

### ML Monitor
```python
min_training_samples = 30  # Samples before training
contamination = 0.15       # Expected anomaly rate
n_estimators = 100         # Decision trees
```

### Dashboard
```python
host = '0.0.0.0'          # Server host
port = 5000               # Server port
debug = False             # Debug mode
```

---

## 🔍 Monitoring Output

### Normal Operation
```
🟢 MACHINE_001: Normal operation | T=65.2°C, V=2.15mm/s, I=10.3A
🟢 MACHINE_002: Normal operation | T=64.8°C, V=2.03mm/s, I=9.8A
🟢 MACHINE_003: Normal operation | T=66.1°C, V=2.18mm/s, I=10.1A
```

### Anomaly Detected
```
🔴 ANOMALY DETECTED!
Alert ID: ALERT_0042
Machine: MACHINE_003
Severity: CRITICAL
Anomaly Score: -0.6234
💡 Recommendation: Schedule inspection: Temperature exceeds safe threshold
```

---

## 🐛 Troubleshooting

### Dashboard not loading?
**Check:** Is `dashboard.py` running?
```bash
python dashboard.py
```

### No data on dashboard?
**Check:** Are sensor simulator and ML monitor running?

### MQTT connection failed?
**Check:** Internet connection and firewall settings

### Module not found errors?
**Solution:**
```bash
pip install -r requirements.txt
```

---

## 📚 Documentation

For detailed technical documentation, see [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)

Topics covered:
- Detailed system architecture
- Data flow diagrams
- ML algorithm explanation
- API reference
- MQTT topic structure
- Advanced configuration

---

## 🎓 Educational Value

This project demonstrates:
- Industrial IoT concepts
- Real-time data streaming
- Machine Learning for anomaly detection
- Web-based monitoring systems
- MQTT protocol usage
- Predictive maintenance strategies

Perfect for:
- IoT course projects
- Machine Learning portfolios
- System integration learning
- Full-stack development practice

---

## 🚧 Future Enhancements

- [ ] Historical data storage (database integration)
- [ ] Email/SMS alert notifications
- [ ] Mobile app interface
- [ ] Cloud deployment (Azure IoT, AWS IoT Core)
- [ ] Multiple ML algorithm comparison
- [ ] Advanced analytics and reporting
- [ ] Maintenance scheduling system
- [ ] Cost-benefit analysis dashboard

---

## 📄 License

This project is open source and available for educational purposes.

---


## 🙏 Acknowledgments

- MQTT Broker: [HiveMQ Public Broker](https://www.hivemq.com/public-mqtt-broker/)
- ML Framework: [Scikit-learn](https://scikit-learn.org/)
- Web Framework: [Flask](https://flask.palletsprojects.com/)
- IoT Protocol: [Paho MQTT](https://www.eclipse.org/paho/)

---

## 📞 Support

For issues or questions:
1. Check [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)
2. Review troubleshooting section above
3. Verify all dependencies are installed

---

**⭐ If you found this project helpful, please star it!**

---

*Last Updated: November 21, 2025*
