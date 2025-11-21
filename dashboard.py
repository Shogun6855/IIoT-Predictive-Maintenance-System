"""
Real-time Web Dashboard for IIoT Monitoring
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import json
import threading
import time
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global data storage
dashboard_data = {
    "machines": {},
    "alerts": [],
    "statistics": {
        "total_readings": 0,
        "total_anomalies": 0,
        "active_machines": 0
    }
}

# MQTT Client
mqtt_client = None

def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        print("✓ Dashboard connected to MQTT Broker")
        # Subscribe to topics
        client.subscribe("factory/machines/+/sensors", qos=1)
        client.subscribe("factory/alerts/anomaly", qos=2)
        print("✓ Subscribed to sensor and alert topics")
    else:
        print(f"✗ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """MQTT message callback"""
    try:
        data = json.loads(msg.payload.decode())
        topic = msg.topic
        
        # Handle sensor data
        if "sensors" in topic:
            handle_sensor_data(data)
        
        # Handle alerts
        elif "alerts" in topic:
            handle_alert(data)
            
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def handle_sensor_data(data):
    """Process sensor data"""
    machine_id = data["machine_id"]
    
    # Update machine data
    if machine_id not in dashboard_data["machines"]:
        dashboard_data["machines"][machine_id] = {
            "readings": [],
            "status": "normal",
            "last_update": None
        }
        dashboard_data["statistics"]["active_machines"] += 1
    
    # Store reading (keep last 50)
    machine_info = dashboard_data["machines"][machine_id]
    machine_info["readings"].append(data)
    if len(machine_info["readings"]) > 50:
        machine_info["readings"].pop(0)
    
    machine_info["last_update"] = data["timestamp"]
    dashboard_data["statistics"]["total_readings"] += 1
    
    # Emit to web clients
    socketio.emit('sensor_update', {
        'machine_id': machine_id,
        'data': data
    })

def handle_alert(alert):
    """Process anomaly alert"""
    # Store alert (keep last 100)
    dashboard_data["alerts"].insert(0, alert)
    if len(dashboard_data["alerts"]) > 100:
        dashboard_data["alerts"].pop()
    
    dashboard_data["statistics"]["total_anomalies"] += 1
    
    # Update machine status
    machine_id = alert["machine_id"]
    if machine_id in dashboard_data["machines"]:
        dashboard_data["machines"][machine_id]["status"] = "anomaly"
    
    # Emit to web clients
    socketio.emit('alert', alert)

def start_mqtt_client():
    """Start MQTT client in background thread"""
    global mqtt_client
    
    mqtt_client = mqtt.Client(client_id=f"dashboard_{int(time.time())}")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect("broker.hivemq.com", 1883, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT connection error: {e}")

# Flask Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    """API endpoint for current data"""
    return jsonify(dashboard_data)

@app.route('/api/machines')
def get_machines():
    """Get list of machines"""
    machines = []
    for machine_id, info in dashboard_data["machines"].items():
        latest = info["readings"][-1] if info["readings"] else {}
        machines.append({
            "id": machine_id,
            "status": info["status"],
            "last_update": info["last_update"],
            "latest_readings": latest
        })
    return jsonify(machines)

@app.route('/api/alerts')
def get_alerts():
    """Get recent alerts"""
    return jsonify(dashboard_data["alerts"][:20])

@app.route('/api/statistics')
def get_statistics():
    """Get system statistics"""
    return jsonify(dashboard_data["statistics"])

@socketio.on('connect')
def handle_connect():
    """Handle web socket connection"""
    print(f"✓ Client connected: {datetime.now()}")
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle web socket disconnection"""
    print(f"✗ Client disconnected: {datetime.now()}")

if __name__ == '__main__':
    print("="*60)
    print("🌐 IIOT DASHBOARD SERVER")
    print("="*60)
    print("Starting MQTT client thread...")
    
    # Start MQTT in background
    mqtt_thread = threading.Thread(target=start_mqtt_client, daemon=True)
    mqtt_thread.start()
    
    time.sleep(2)  # Wait for MQTT to connect
    
    print("✓ Dashboard ready")
    print("✓ Open browser to: http://localhost:5000")
    print("="*60 + "\n")
    
    # Start Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
