"""
Machine Learning Monitor
Receives sensor data and performs anomaly detection
"""

import paho.mqtt.client as mqtt
import json
import numpy as np
from datetime import datetime
from collections import deque
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import time

class MLPredictiveMonitor:
    """ML-based monitoring system for predictive maintenance"""
    
    def __init__(self):
        self.client = mqtt.Client(client_id=f"ml_monitor_{int(time.time())}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # Data storage for each machine
        self.machine_data = {}
        self.alert_history = []
        
        # ML Model
        self.model = None
        self.scaler = StandardScaler()
        self.model_trained = False
        self.training_data = []
        self.min_training_samples = 30
        
        # Statistics
        self.total_readings = 0
        self.anomalies_detected = 0
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✓ ML Monitor connected to MQTT Broker")
            # Subscribe to all machine sensors
            client.subscribe("factory/machines/+/sensors", qos=1)
            print("✓ Subscribed to: factory/machines/+/sensors")
        else:
            print(f"✗ Connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        """Process incoming sensor data"""
        try:
            data = json.loads(msg.payload.decode())
            self.process_sensor_data(data)
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def process_sensor_data(self, data):
        """Process and analyze sensor readings"""
        machine_id = data["machine_id"]
        self.total_readings += 1
        
        # Initialize storage for new machine
        if machine_id not in self.machine_data:
            self.machine_data[machine_id] = {
                "readings": deque(maxlen=50),
                "alerts": []
            }
        
        # Store reading
        self.machine_data[machine_id]["readings"].append(data)
        
        # Extract features for ML
        features = self.extract_features(data)
        
        # Collect training data
        if not self.model_trained:
            self.training_data.append(features)
            
            if len(self.training_data) >= self.min_training_samples:
                self.train_model()
        
        # Perform anomaly detection if model is ready
        if self.model_trained:
            is_anomaly, anomaly_score = self.detect_anomaly(features)
            
            if is_anomaly:
                self.handle_anomaly(machine_id, data, anomaly_score)
            else:
                self.log_normal_operation(machine_id, data)
    
    def extract_features(self, data):
        """Extract relevant features from sensor data"""
        return [
            data.get("temperature", 0),
            data.get("vibration", 0),
            data.get("current", 0),
            data.get("pressure", 0),
            data.get("rpm", 0)
        ]
    
    def train_model(self):
        """Train the Isolation Forest model"""
        print("\n" + "="*60)
        print("🧠 Training ML Model...")
        print("="*60)
        
        X = np.array(self.training_data)
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=0.15,  # Expected anomaly rate
            random_state=42,
            n_estimators=100
        )
        self.model.fit(X_scaled)
        
        self.model_trained = True
        
        print(f"✓ Model trained on {len(self.training_data)} samples")
        print(f"✓ Features: temperature, vibration, current, pressure, rpm")
        print("="*60 + "\n")
        
        # Save model
        with open('models/anomaly_detector.pkl', 'wb') as f:
            pickle.dump({'model': self.model, 'scaler': self.scaler}, f)
        print("✓ Model saved to models/anomaly_detector.pkl\n")
    
    def detect_anomaly(self, features):
        """Detect if current reading is anomalous"""
        X = np.array([features])
        X_scaled = self.scaler.transform(X)
        
        # Predict (-1 for anomaly, 1 for normal)
        prediction = self.model.predict(X_scaled)[0]
        
        # Get anomaly score
        score = self.model.score_samples(X_scaled)[0]
        
        is_anomaly = (prediction == -1)
        
        return is_anomaly, score
    
    def handle_anomaly(self, machine_id, data, score):
        """Handle detected anomaly"""
        self.anomalies_detected += 1
        
        alert = {
            "alert_id": f"ALERT_{self.anomalies_detected:04d}",
            "machine_id": machine_id,
            "timestamp": data["timestamp"],
            "anomaly_score": round(float(score), 4),
            "metrics": {
                "temperature": data["temperature"],
                "vibration": data["vibration"],
                "current": data["current"],
                "pressure": data["pressure"],
                "rpm": data["rpm"]
            },
            "severity": self.calculate_severity(score),
            "recommendation": self.get_recommendation(data)
        }
        
        # Store alert
        self.machine_data[machine_id]["alerts"].append(alert)
        self.alert_history.append(alert)
        
        # Publish alert
        self.client.publish(
            "factory/alerts/anomaly",
            json.dumps(alert),
            qos=2
        )
        
        # Display alert
        severity_icon = {
            "CRITICAL": "🔴",
            "WARNING": "🟡",
            "INFO": "🔵"
        }
        
        print(f"\n{'='*60}")
        print(f"{severity_icon[alert['severity']]} ANOMALY DETECTED!")
        print(f"{'='*60}")
        print(f"Alert ID: {alert['alert_id']}")
        print(f"Machine: {machine_id}")
        print(f"Time: {datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Severity: {alert['severity']}")
        print(f"Anomaly Score: {alert['anomaly_score']:.4f}")
        print(f"\nMetrics:")
        for key, value in alert['metrics'].items():
            print(f"  - {key.capitalize()}: {value}")
        print(f"\n💡 Recommendation: {alert['recommendation']}")
        print(f"{'='*60}\n")
    
    def calculate_severity(self, score):
        """Calculate alert severity based on anomaly score"""
        if score < -0.5:
            return "CRITICAL"
        elif score < -0.3:
            return "WARNING"
        else:
            return "INFO"
    
    def get_recommendation(self, data):
        """Generate maintenance recommendation"""
        issues = []
        
        if data["temperature"] > 80:
            issues.append("Temperature exceeds safe threshold")
        if data["vibration"] > 4.0:
            issues.append("Excessive vibration detected")
        if data["current"] > 15:
            issues.append("High current draw")
        if data["rpm"] < 1400:
            issues.append("RPM below optimal range")
        
        if issues:
            return f"Schedule inspection: {'; '.join(issues)}"
        else:
            return "Monitor closely for additional anomalies"
    
    def log_normal_operation(self, machine_id, data):
        """Log normal operation"""
        print(f"✓ {machine_id}: Normal operation | "
              f"T={data['temperature']:.1f}°C, "
              f"V={data['vibration']:.2f}mm/s, "
              f"I={data['current']:.1f}A")
    
    def print_statistics(self):
        """Print monitoring statistics"""
        print("\n" + "="*60)
        print("📊 MONITORING STATISTICS")
        print("="*60)
        print(f"Total Readings: {self.total_readings}")
        print(f"Anomalies Detected: {self.anomalies_detected}")
        print(f"Anomaly Rate: {(self.anomalies_detected/max(self.total_readings,1))*100:.2f}%")
        print(f"Machines Monitored: {len(self.machine_data)}")
        print(f"Model Status: {'✓ Trained' if self.model_trained else '⏳ Training...'}")
        print("="*60 + "\n")
    
    def run(self, broker="broker.hivemq.com", port=1883):
        """Start the monitoring system"""
        print("="*60)
        print("🤖 ML PREDICTIVE MAINTENANCE MONITOR")
        print("="*60)
        print(f"Connecting to {broker}:{port}...")
        
        self.client.connect(broker, port, 60)
        
        print("✓ System ready - Waiting for sensor data...")
        print(f"✓ Will train model after {self.min_training_samples} readings\n")
        
        try:
            # Print stats periodically
            last_stats_time = time.time()
            
            self.client.loop_start()
            
            while True:
                time.sleep(1)
                
                # Print stats every 30 seconds
                if time.time() - last_stats_time > 30:
                    self.print_statistics()
                    last_stats_time = time.time()
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor stopped by user")
            self.print_statistics()
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            print("✓ Disconnected from MQTT broker")

if __name__ == "__main__":
    monitor = MLPredictiveMonitor()
    monitor.run()
