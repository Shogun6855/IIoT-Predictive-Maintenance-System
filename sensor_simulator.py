"""
Simulated Industrial Sensor System
Publishes sensor data via MQTT without any physical hardware
"""

import paho.mqtt.client as mqtt
import time
import random
import json
import math
from datetime import datetime

class VirtualIndustrialMachine:
    """Simulates an industrial machine with sensors"""
    
    def __init__(self, machine_id, failure_mode=False):
        self.machine_id = machine_id
        self.failure_mode = failure_mode
        self.runtime_hours = 0
        self.cycle_count = 0
        
        # Normal operating parameters
        self.base_temp = 65.0
        self.base_vibration = 2.0
        self.base_current = 10.0
        
        # Degradation tracking
        self.degradation_factor = 0.0
        
    def simulate_readings(self):
        """Generate realistic sensor readings"""
        
        # Simulate time-of-day effects
        hour = datetime.now().hour
        daily_load_factor = 1.0 + 0.2 * math.sin(2 * math.pi * hour / 24)
        
        # Add gradual degradation
        if self.failure_mode:
            self.degradation_factor += random.uniform(0.001, 0.005)
        
        # Temperature (°C)
        temperature = (
            self.base_temp * daily_load_factor +
            self.degradation_factor * 15 +  # Overheating as it degrades
            random.gauss(0, 2)  # Normal sensor noise
        )
        
        # Vibration (mm/s)
        vibration = (
            self.base_vibration +
            self.degradation_factor * 3 +  # Increased vibration when degraded
            random.gauss(0, 0.3) +
            0.5 * math.sin(self.cycle_count * 0.1)  # Cyclic pattern
        )
        
        # Current (Amperes)
        current = (
            self.base_current * daily_load_factor +
            self.degradation_factor * 5 +  # Higher current draw
            random.gauss(0, 0.5)
        )
        
        # Pressure (Bar) - optional
        pressure = 6.0 + random.gauss(0, 0.2)
        
        # RPM
        rpm = 1500 + random.gauss(0, 50) - (self.degradation_factor * 100)
        
        self.cycle_count += 1
        self.runtime_hours += 0.001  # Increment slightly
        
        return {
            "machine_id": self.machine_id,
            "timestamp": datetime.now().isoformat(),
            "temperature": round(temperature, 2),
            "vibration": round(vibration, 2),
            "current": round(current, 2),
            "pressure": round(pressure, 2),
            "rpm": round(rpm, 0),
            "runtime_hours": round(self.runtime_hours, 2),
            "degradation_level": round(self.degradation_factor * 100, 1)
        }

class SensorPublisher:
    """Publishes simulated sensor data via MQTT"""
    
    def __init__(self, broker="broker.hivemq.com", port=1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(client_id=f"sensor_sim_{random.randint(1000,9999)}")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✓ Connected to MQTT Broker at {self.broker}")
        else:
            print(f"✗ Connection failed with code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected from broker")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            print(f"Connecting to {self.broker}:{self.port}...")
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            time.sleep(2)  # Wait for connection
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def publish(self, topic, data):
        """Publish data to MQTT topic"""
        payload = json.dumps(data)
        result = self.client.publish(topic, payload, qos=1)
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    def disconnect(self):
        """Disconnect from broker"""
        self.client.loop_stop()
        self.client.disconnect()

def run_simulation(num_machines=3, interval_seconds=2, duration_minutes=None):
    """
    Run the complete sensor simulation
    
    Args:
        num_machines: Number of machines to simulate
        interval_seconds: Time between sensor readings
        duration_minutes: How long to run (None = forever)
    """
    
    print("=" * 60)
    print("🏭 INDUSTRIAL IoT SENSOR SIMULATOR")
    print("=" * 60)
    print(f"Simulating {num_machines} machines")
    print(f"Publishing every {interval_seconds} seconds")
    print(f"Duration: {'Infinite (Ctrl+C to stop)' if not duration_minutes else f'{duration_minutes} minutes'}")
    print("=" * 60)
    
    # Create publisher
    publisher = SensorPublisher()
    if not publisher.connect():
        print("Failed to connect to MQTT broker. Exiting.")
        return
    
    # Create virtual machines
    machines = []
    for i in range(num_machines):
        # Make one machine operate in failure mode
        failure_mode = (i == num_machines - 1)
        machine = VirtualIndustrialMachine(
            machine_id=f"MACHINE_{i+1:03d}",
            failure_mode=failure_mode
        )
        machines.append(machine)
        
        if failure_mode:
            print(f"⚠️  {machine.machine_id} is in DEGRADATION MODE (will show anomalies)")
    
    print("\n📡 Starting data transmission...\n")
    
    start_time = time.time()
    reading_count = 0
    
    try:
        while True:
            # Check duration
            if duration_minutes:
                elapsed = (time.time() - start_time) / 60
                if elapsed >= duration_minutes:
                    print(f"\n✓ Simulation completed ({duration_minutes} minutes)")
                    break
            
            # Generate and publish readings for each machine
            for machine in machines:
                readings = machine.simulate_readings()
                
                # Publish to different topics
                publisher.publish(
                    f"factory/machines/{machine.machine_id}/sensors",
                    readings
                )
                
                # Also publish individual metrics for flexibility
                publisher.publish(
                    f"factory/sensors/temperature",
                    {
                        "machine_id": machine.machine_id,
                        "value": readings["temperature"],
                        "timestamp": readings["timestamp"]
                    }
                )
                
                # Display status
                status_icon = "🔴" if readings["degradation_level"] > 50 else \
                              "🟡" if readings["degradation_level"] > 20 else "🟢"
                
                print(f"{status_icon} {machine.machine_id}: "
                      f"Temp={readings['temperature']:.1f}°C, "
                      f"Vib={readings['vibration']:.2f}mm/s, "
                      f"Curr={readings['current']:.1f}A, "
                      f"Degrade={readings['degradation_level']:.1f}%")
            
            reading_count += 1
            print(f"   [{reading_count} readings published]\n")
            
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation stopped by user")
    finally:
        publisher.disconnect()
        print("✓ Disconnected from MQTT broker")
        print(f"✓ Total readings published: {reading_count}")

if __name__ == "__main__":
    # Configuration
    NUM_MACHINES = 3
    INTERVAL_SECONDS = 3
    DURATION_MINUTES = None  # Set to a number for limited duration, None for infinite
    
    run_simulation(
        num_machines=NUM_MACHINES,
        interval_seconds=INTERVAL_SECONDS,
        duration_minutes=DURATION_MINUTES
    )
