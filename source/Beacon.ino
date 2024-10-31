#include <WiFi.h>
#include <WebSocketsClient.h>
#include <MQTTPubSubClient.h>
#include <ArduinoBLE.h>

const char* ssid = "your_ssid";
const char* pass = "your_password";
const char* mqtt_server = "broker server";
const int mqtt_port = 443;  // Use the port you need for WSS
const char* mqtt_user = "username";
const char* mqtt_password = "password";
const char* mqtt_topic = "trilateration/beacon";
const char* mqtt_path = "/";  // The path for your WebSocket

WebSocketsClient client;
MQTTPubSubClient mqtt;

void connect() {
  connect_to_wifi:
  Serial.print("connecting to wifi...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println(" connected!");

  connect_to_host:
  Serial.println("connecting to host...");
  client.disconnect();
  client.beginSSL(mqtt_server, mqtt_port, mqtt_path, "", "mqtt");  // Use SSL and specify path
  client.setReconnectInterval(2000);  // Set reconnect interval to 2 seconds
  Serial.print("connecting to mqtt broker...");
  while (!mqtt.connect(WiFi.macAddress().c_str(), mqtt_user, mqtt_password)) {  // Unique client name
    Serial.print(".");
    delay(1000);
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi disconnected");
      goto connect_to_wifi;
    }
    if (!client.isConnected()) {
      Serial.println("WebSocketsClient disconnected");
      goto connect_to_host;
    }
  }
  Serial.println(" connected!");
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, pass);

  // initialize mqtt client
  mqtt.begin(client);

  // connect to wifi, host and mqtt broker
  connect();

  Serial.println("Starting the BLE module...");
  if (!BLE.begin()) {
    Serial.println("Failed to start BLE module!");
    while (1)
      ;
  }
}

void loop() {
  mqtt.update();  // should be called to trigger callbacks
  if (!mqtt.isConnected()) {
    connect();
  }

  Serial.println("Starting scan...");
  BLE.scan();
  delay(50000);

  int deviceCount = 0;
  String json = "{";
  json += "\"mac-address\":\"" + String(BLE.address()) + "\",";
  json += "\"device_connected\":";
  BLEDevice peripheral;
  String logs = "\"logs\":[";
  while (peripheral = BLE.available()) {
    if (deviceCount > 0) {
      logs += ",";
    }
    logs += "{";
    logs += "\"mac-address\":\"" + peripheral.address() + "\",";
    logs += "\"name\":\"" + peripheral.localName() + "\",";
    logs += "\"RSSI\":" + String(peripheral.rssi());
    logs += "}";
    deviceCount++;
  }
  logs += "]";
  json += String(deviceCount) + ",";
  json += logs;
  json += "}";
  Serial.println(json);

  // Publish JSON data to MQTT topic
  mqtt.publish(mqtt_topic, json);

  BLE.stopScan();
  delay(10000);
}