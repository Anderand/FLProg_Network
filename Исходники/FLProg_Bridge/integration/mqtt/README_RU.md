# Исходники MQTT-транспорта через ESP

src содержит изменения к FLProg_Network r17. При подготовке кандидата дополнительно копируются канонические заголовки flprog_bridge/firmware/FLProgBridgeProtocol.h, FLProgTcpBridge.h и FLProgBridgeTcpClient.h в src/bridge. Устанавливать нужно согласованную папку библиотеки целиком; штатные зависимости не заменяются.

Исправление EOF от29.10.2026 затрагивает FLProgBridgeTcpClient.h и FLProgMqttBridgeTransport.h. Последние принятые байты сохраняются после FIN, а разрешение TX проверяется отдельно. Проверки и готовый локальный комплект описаны в docs/SHARED_STRESS_RU.md относительно flprog_bridge.
