# API COMPAT GATE 02 RU

API Compatibility Gate 0.2 — FLProgEthernetClient

Цель:
Сохранить внешний API старого FLProgEthernetClient, но выполнять transport/socket
работу через FLProgNetworkTcpClient и RC6-A A3.

Добавлено:
- src/tcp/flprogEthernetClient.h/.cpp
- экспорт из flprogEthernet.h
- legacy ctor FLProgEthernetClient(FLProgAbstractTcpInterface*)
- setSourse()/init()
- connect(IPAddress,port), connect(host,port)
- connected(), available(), read(), peek(), write(), println() через Print, stop()
- localPort()/remoteIP()/remotePort()
- getSocketNumber()
- set/getConnectionTimeout()
- set/getDnsCacheStorageTime()
- getStatus()/status()/getError()/getErrorCode()
- legacy change flags/statusForExt

Архитектурные ограничения:
- старая raw-socket таблица НЕ возвращена;
- FLProgAbstractTcpInterface остаётся compatibility alias к FLProgNetworkInterface;
- внутри используется один FLProgNetworkTcpClient;
- A3 TransportIdentity/generation/lease/socket/backend не менялись;
- автономный reconnect адаптера отключён, чтобы не менять legacy connect-state semantics.

Ограничение Gate 0.2:
Это сначала compile/API gate. Точное соответствие старых числовых status/error и
старого Wiznet SnSR status() будет проверяться отдельным semantic/functional gate.
DNS cache legacy milliseconds временно отображается в native max TTL (seconds cap).
