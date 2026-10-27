/*
 * FLProg_Network - MQTT_Runtime_Gate_RU.ino
 *
 * Назначение: минимальный аппаратный gate native MQTT 3.1.1 client.
 *
 * Порядок работы:
 * 1. Задать Wi-Fi и MQTT broker ниже.
 * 2. Прошить на ESP8266/ESP32 с доступом к broker.
 * 3. Подписаться с ПК на FLPROG_MQTT_GATE_IN и отправить туда сообщение.
 * 4. Проверить ответ на FLPROG_MQTT_GATE_OUT и Serial diagnostics.
 *
 * Расширенный контракт сопровождения:
 * - Пример intentionally использует native FLProgNetworkMqttClient, поэтому
 *   проверяет service layer без отсутствующего штатного FLProg MQTT-блока.
 * - network.pool() является единственным обязательным циклическим вызовом;
 *   MQTT/DNS/TCP progress выполняется cooperative без delay().
 * - SSID, пароль и credentials остаются placeholder и не должны попадать
 *   в репозиторий или публичный отчёт.
 *
 * Extended maintenance contract:
 * - This example intentionally uses the native FLProgNetworkMqttClient and
 *   tests the service layer without a missing built-in FLProg MQTT block.
 * - network.pool() is the only required loop call; MQTT/DNS/TCP progress is
 *   cooperative and does not use delay().
 * - SSID, password and credentials remain placeholders and must never enter
 *   the repository or a public report.
 */

#include <flprogNetwork.h>

const char *WIFI_SSID = "YOUR_WIFI_SSID";
const char *WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char *MQTT_BROKER = "192.168.100.7";
const uint16_t MQTT_PORT = 1883;
const char *MQTT_CLIENT_ID = "flprog-network-gate";
const char *MQTT_USERNAME = "";
const char *MQTT_PASSWORD = "";
const char *MQTT_GATE_IN = "flprog/network/gate/in";
const char *MQTT_GATE_OUT = "flprog/network/gate/out";

// OnBoardWifi включает рабочий режим и Wi-Fi transport уже в конструкторе.
FLProgOnBoardWifiInterface network;
FLProgNetworkMqttClient mqtt;

bool subscribed = false;
bool selfTestQueued = false;
uint32_t lastPublishAt = 0;
uint32_t lastStatusAt = 0;
uint32_t subscribedAt = 0;

void onMqttMessage(const char *topic, const uint8_t *payload, size_t length, bool retained)
{
    Serial.print("MQTT RX topic=");
    Serial.print(topic);
    Serial.print(" retained=");
    Serial.print(retained ? 1 : 0);
    Serial.print(" payload=");
    for (size_t i = 0; i < length; ++i) Serial.write(payload[i]);
    Serial.println();
    mqtt.publish(MQTT_GATE_OUT, "echo", false);
}

void setup()
{
    Serial.begin(115200);
    Serial.println();
    Serial.println("FLProg MQTT gate: start");
    Serial.print("Broker: ");
    Serial.print(MQTT_BROKER);
    Serial.print(":");
    Serial.println(MQTT_PORT);
    network.setClientSsid(WIFI_SSID);
    network.setClientPassword(WIFI_PASSWORD);
    network.clientOn();

    mqtt.setBroker(MQTT_BROKER);
    mqtt.setPort(MQTT_PORT);
    mqtt.setClientId(MQTT_CLIENT_ID);
    if (MQTT_USERNAME[0] != 0) mqtt.setCredentials(MQTT_USERNAME, MQTT_PASSWORD);
    mqtt.setMessageCallback(onMqttMessage);
    mqtt.setAutoReconnect(true);
    mqtt.begin(network);
    mqtt.connect();
    Serial.println("Wi-Fi and MQTT connection requested");
}

void loop()
{
    network.pool();

    if (millis() - lastStatusAt >= 3000UL)
    {
        lastStatusAt = millis();
        Serial.print("WiFiReady=");
        Serial.print(network.clientIsReady() ? 1 : 0);
        Serial.print(" MQTT connected=");
        Serial.print(mqtt.connected() ? 1 : 0);
        Serial.print(" state=");
        Serial.print(mqtt.state());
        Serial.print(" error=");
        Serial.println(mqtt.error());
    }

    if (mqtt.connected() && !subscribed)
    {
        subscribed = mqtt.subscribe(MQTT_GATE_IN);
        Serial.println(subscribed ? "MQTT subscribe queued" : "MQTT subscribe rejected");
        if (subscribed)
        {
            subscribedAt = millis();
        }
    }

    // subscribe() queues a packet. Give the broker time to process SUBSCRIBE
    // before publishing the loopback test into the subscribed topic.
    if (subscribed && !selfTestQueued && millis() - subscribedAt >= 1000UL)
    {
        selfTestQueued = mqtt.publish(MQTT_GATE_IN, "self-test", false);
        Serial.println(selfTestQueued ? "MQTT self-test queued" : "MQTT self-test rejected");
    }

    if (mqtt.connected() && millis() - lastPublishAt >= 15000UL)
    {
        lastPublishAt = millis();
        mqtt.publish(MQTT_GATE_OUT, "alive", false);
        Serial.print("MQTT state=");
        Serial.print(mqtt.state());
        Serial.print(" error=");
        Serial.print(mqtt.error());
        Serial.print(" connectSuccess=");
        Serial.print(mqtt.connectSuccessCount());
        Serial.print(" messages=");
        Serial.println(mqtt.messageCount());
    }
}
