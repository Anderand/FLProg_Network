# API COMPAT GATE 01 RU

FLProg_Network RC6-A API Compatibility Gate 0.1

Цель:
Сохранить имя FLProgAbstractTcpInterface для существующего FLProg-кода без возврата старой raw-socket архитектуры Flprog_Ethernet.

Реализация:
1. FLProgAbstractTcpInterface является source-compatibility alias для FLProgNetworkInterface.
2. В FLProgNetworkInterface добавлены legacy interface-level методы:
   isReadyForDNS(), isImitation(), isInit(), maxSoketNum().
3. flprogEthernet.h экспортирует compatibility header.
4. Старые raw-socket virtual методы (readFromSoket/writeToSoket/get*Socket и т.п.) намеренно НЕ возвращены в Core. Их должны закрывать последующие TCP/UDP compatibility adapters через A3 backend.

Не изменено:
- NET NUM / Registry
- TransportIdentity / generation
- lease/socket backend
- WiFi EXP-2A-fix4 logic
- public Native FLProg_Network API (только добавлены compatibility methods)

Gate:
Сначала compile/source API gate. Затем A1 CLEAN resource gate. Функциональные A2/TCP тесты только после закрытия этого шага.

RC6-A dev.13-fix1: removed duplicate FLProgNetworkInterface::isImitation() declaration found by API Compatibility Gate 0.1. No other code changes.

RC6-A dev.13-fix2:
- maxSoketNum() больше не тянет Wiznet backend в WiFi-only profile.
- При FLPROG_NETWORK_COMPILE_WIRED=0 возвращает логический лимит A3 FLPROG_NETWORK_MAX_MANAGED_SOCKETS.
- При wired profile сохраняет делегирование native maxSocketNum().
- EXP-2A-fix4/A3 поведение не изменялось.
