from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from pymongo import MongoClient
import time, json, random, copy

# --- MongoDB Setup ---
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["iot_data"]
collection = db["sensor_readings"]

# --- AWS IoT Core MQTT Setup ---
client = AWSIoTMQTTClient("bchikara_station_001")
client.configureEndpoint("a31helc327dm1d-ats.iot.us-east-2.amazonaws.com", 8883)
client.configureCredentials(
    "AmazonRootCA1.pem",
    "bda16327272b075e0fc4a6b318c4ae5d16a4e2672a3aaa9b02c50da3330085ae-private.pem.key",
    "bda16327272b075e0fc4a6b318c4ae5d16a4e2672a3aaa9b02c50da3330085ae-certificate.pem.crt"
)

client.configureOfflinePublishQueueing(-1)  # Infinite queue
client.configureDrainingFrequency(2)
client.configureConnectDisconnectTimeout(10)
client.configureMQTTOperationTimeout(5)

# --- Connect to AWS IoT ---
print("Connecting to AWS IoT...")
client.connect()
print("Connected!")

# --- Loop: Generate + Send Data ---
while True:
    payload = {
        "station_id": "station_001",
        "temperature": round(random.uniform(-50, 50), 2),
        "humidity": round(random.uniform(0, 100), 2),
        "co2": random.randint(300, 2000),
        "timestamp": time.time()
    }

    # Insert a deepcopy so _id doesn't affect the original payload
    collection.insert_one(copy.deepcopy(payload))

    # Publish clean original payload to MQTT
    client.publish("iot/sensors", json.dumps(payload), 1)

    print("Stored in MongoDB and Published via MQTT:", payload)
    time.sleep(5)
