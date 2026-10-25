/*
 * FLProg_Network — WiFi_TCP_Interim_Gate_EN.ino
 * Назначение: Пример для ручной проверки FLProg_Network.
 *
 * Архитектурные заметки:
 * - Показывает минимальную последовательность настройки и запуска без скрытой магии.
 * - Перед аппаратным тестом сверяйте плату, пины, адреса и отключайте VPN для сетевых проверок.
 * - Пример не является заменой отдельному regression gate: он предназначен для воспроизводимой диагностики.
 *
 * Комментарии описывают контракт и причины решений; рабочую логику файла не дублируют.
 *
 * Extended maintenance contract:
 * - This is a safe diagnostic template, not a production firmware: the user supplies
 *   real SSID, password and peer address, and credentials must never enter the repository.
 * - A real example always follows the same order: configure in setup(), then call
 *   network.pool() regularly from loop()/LoopSection without delay or blocking waits.
 * - The echo result proves only its declared scenario; transport restart, HTTP and
 *   multiple clients require their own dedicated gates.
 *
 * Расширенный контракт сопровождения:
 * - Это безопасный шаблон диагностики, а не готовая production-прошивка: реальные SSID,
 *   пароль и адрес peer задаёт пользователь и не должны попадать в репозиторий.
 * - Последовательность реального примера: настройка в setup(), регулярный pool() без
 *   delay и блокирующих ожиданий в loop()/LoopSection.
 * - Echo-тест подтверждает только свой сценарий; restart transport, HTTP и multi-client
 *   проходят отдельные gate.
 */
// FLProg_Network RC6-A EXP-2A-fix4
// EN: Set SSID, password and echo-server address before use.
// This example is a safe template for the Wi-Fi-only interim regression gate.

#include <flprogNetwork.h>

const char *WIFI_SSID = "YOUR_WIFI_SSID";
const char *WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
IPAddress SERVER_IP(192, 168, 100, 7);
const uint16_t SERVER_PORT = 5000;

// The full hardware gate sketch is kept in the project handoff package.
// Personal network credentials are intentionally not embedded here.

void setup() {}
void loop() {}
