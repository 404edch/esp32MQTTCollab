# ESP32 MQTT Collab

A collaborative IoT learning project implementing real sensor integration with MQTT messaging on ESP32 microcontrollers. Features progressive challenges covering sensor data acquisition, MQTT Quality of Service reliability, and multi-sensor system architecture with a practical refrigerated truck monitoring use case.

## Project Overview

This repository documents a structured learning experience in IoT development, demonstrating how to build a distributed sensor network using ESP32 boards communicating through MQTT. The project progresses through three challenges, each building upon the previous one to create a complete monitoring and control system.

## Challenges

### Challenge 1 - Real Sensor Data
Replace simulated random data with actual sensor readings using MicroPython's native libraries. Implement data acquisition from:
- **DHT11/DHT22** temperature and humidity sensors
- Real-time sensor polling and data publishing to MQTT topics

**Key Learning:** Transitioning from mock data to genuine hardware integration.

### Challenge 2 - QoS and Persistent Sessions
Investigate MQTT Quality of Service levels and implement reliable message delivery:

- **QoS 0 (Fire and Forget):** Fast but unreliable; data is lost if failures occur
- **QoS 1 (At Least Once):** Ensures delivery with acknowledgment; may result in message duplication
- **QoS 2 (Exactly Once):** Four-step handshake guarantees single delivery without duplication

**Implementation Details:**
- Set `clean_session = False` to enable persistent sessions
- Configure QoS level 1 for the subscriber
- Broker stores messages for offline devices and delivers complete backlog upon reconnection

**Challenge Overcome:** Resolved packet loss during ESP32 unexpected shutdowns by combining persistent sessions with QoS 1, ensuring no data loss during device disconnections.

### Challenge 3 - Multiple Sensors & Real-World Application
Configure multiple sensors and actuators publishing to different topics, with PC subscribing using MQTT wildcards.

**Use Case: Refrigerated Truck Monitoring System**

Monitor environmental conditions and cargo integrity inside a refrigerated transport vehicle.

**Sensors:**
- **DHT11:** Temperature and humidity measurement inside the refrigerator
- **HC-SR04:** Ultrasonic distance sensor for cargo displacement detection

**Actuators:**
- **LED:** Visual alert indicator
- **Buzzer:** Audible alarm

**Emergency Conditions Triggered:**
- Temperature > -5°C (thawing detection)
- Humidity > 80% (environmental degradation)
- Proximity < 1 meter (cargo displacement)

**Interactive Commands (PC to ESP32):**
- `lock` - Pause automatic sensor verification; disable alerts (maintenance mode)
- `unlock` - Resume automatic sensor monitoring and periodic data publishing
- `emergencia_comecar` - Manually activate emergency mode
- `emergencia_parar` - Manually deactivate emergency mode
- `status` - Request immediate publication of current sensor readings

**Challenge Overcome:** Fixed character encoding issues by implementing UTF-8 decoding standard.

## Project Structure

```
esp32MQTTCollab/
├── Desafio 1/          # Challenge 1 - Real sensor implementation
├── Desafio 3/          # Challenge 3 - Multi-sensor system
├── MQTTComputador1.py  # PC client for Challenge 1
└── MQTTComputador3.py  # PC client for Challenge 3
```

## Technical Stack

- **Microcontroller:** ESP32
- **Firmware:** MicroPython
- **Protocol:** MQTT
- **PC Language:** Python
- **Message Broker:** MQTT Broker (mqtt-dashboard.com or self-hosted)
- **Sensors:** DHT11, DHT22, HC-SR04
- **Actuators:** LED, Buzzer

## Key Learnings

1. **MQTT Architecture:** Publishing/subscribing patterns, topic organization, wildcard subscriptions
2. **Reliability Mechanisms:** Understanding QoS levels and persistent sessions for fault-tolerant IoT systems
3. **Real Hardware Integration:** Working with actual sensors and translating readings into actionable data
4. **System Design:** Building responsive systems with emergency handling and manual override capabilities
5. **Debugging:** Character encoding issues, packet loss troubleshooting, session management

## Authors

- **Bruno Moretoni**
- **Eduardo Chechin**
- **Lunna Damo**

## Getting Started

1. Flash MicroPython onto your ESP32
2. Configure WiFi credentials and MQTT broker settings in the ESP32 code
3. Upload sensor integration code to the microcontroller
4. Run the Python client scripts on your computer
5. Monitor sensor data and test interactive commands

## Requirements

- ESP32 microcontroller
- DHT11 or DHT22 temperature/humidity sensor
- HC-SR04 ultrasonic sensor (for Challenge 3)
- LED and Buzzer components
- MQTT Broker (public or self-hosted)
- Python 3.x with MQTT client library (`paho-mqtt`)
- MicroPython environment for ESP32

## Notes

- Ensure proper WiFi connectivity before attempting MQTT connections
- Test QoS levels independently to understand behavioral differences
- Use persistent sessions carefully in production to manage broker storage
- Character encoding (UTF-8) must be properly configured for special characters in messages

