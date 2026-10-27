# API COMPAT GATE 03 UDP RU

RC6-A dev.15 — API Compatibility Gate 0.3

Добавлен legacy FLProgUdpClient поверх FLProgNetworkUdp/A3.
Старая raw-socket архитектура не возвращается.

Первый этап: compile/API gate на ESP8266 без реального UDP-трафика.
После PASS — отдельный semantic UDP echo gate по Wi-Fi.
