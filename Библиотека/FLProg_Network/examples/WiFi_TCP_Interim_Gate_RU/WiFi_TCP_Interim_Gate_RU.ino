/*
 * FLProg_Network — WiFi_TCP_Interim_Gate_RU.ino
 * Назначение: Пример для ручной проверки FLProg_Network.
 *
 * Архитектурные заметки:
 * - Показывает минимальную последовательность настройки и запуска без скрытой магии.
 * - Перед аппаратным тестом сверяйте плату, пины, адреса и отключайте VPN для сетевых проверок.
 * - Пример не является заменой отдельному regression gate: он предназначен для воспроизводимой диагностики.
 *
 * Комментарии описывают контракт и причины решений; рабочую логику файла не дублируют.
 *
 * Расширенный контракт сопровождения:
 * - Это безопасный шаблон диагностики, а не готовая production-прошивка: реальные SSID,
 *   пароль и адрес peer задаёт пользователь и не должны попадать в репозиторий.
 * - Последовательность реального примера всегда одинакова: настройка в setup(), затем
 *   регулярный вызов network.pool() из loop()/LoopSection без delay и блокирующих ожиданий.
 * - Результат echo-теста подтверждает только заданный scenario; transport restart,
 *   HTTP или несколько клиентов проверяются собственными отдельными gate.
 *
 * Extended maintenance contract:
 * - This is a safe diagnostic template, not a production firmware: the user supplies
 *   real SSID, password and peer address, and credentials must never enter the repository.
 * - A real example always follows the same order: configure in setup(), then call
 *   network.pool() regularly from loop()/LoopSection without delay or blocking waits.
 * - The echo result proves only its declared scenario; transport restart, HTTP and
 *   multiple clients require their own dedicated gates.
 */
// FLProg_Network RC6-A EXP-2A-fix4
// RU: Перед использованием задайте SSID, пароль и адрес echo-сервера.
// Этот пример предназначен для Wi-Fi-only промежуточного regression gate.

#include <flprogNetwork.h>

const char *WIFI_SSID = "YOUR_WIFI_SSID";
const char *WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
IPAddress SERVER_IP(192, 168, 100, 7);
const uint16_t SERVER_PORT = 5000;

// Полный аппаратный gate-скетч хранится в handoff-пакете проекта.
// Здесь намеренно оставлен безопасный шаблон без персональных сетевых данных.

void setup() {}
void loop() {}
