# COMPAT FIX3 CONNECTED REDEFINITION

RC6-A dev.14-fix3
Fixed duplicate FLProgEthernetClient::connected() definition.
Header now declares connected(); implementation remains in flprogEthernetClient.cpp.
No server/A3/transport behavior changed.
