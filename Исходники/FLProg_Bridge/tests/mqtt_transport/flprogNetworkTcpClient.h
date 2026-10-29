#pragma once
#include <Arduino.h>
#include <IPAddress.h>
#define FLPROG_TCP_HOSTNAME_MAX_LENGTH 127
#define FLPROG_TCP_CLIENT_ERROR_NONE 0
#define FLPROG_TCP_DNS_POLICY_PRIVATE 1
#define FLPROG_SOCKET_STATE_ERROR 8
#define FLPROG_SOCKET_STATE_UNSUPPORTED 9
class FLProgNetworkInterface;
class FLProgNetworkTcpClient{public:static unsigned nativeBegin,nativeConnect;virtual~FLProgNetworkTcpClient(){};virtual void pool(){};bool begin(FLProgNetworkInterface&,uint8_t){++nativeBegin;return true;}void end(){};void stop(){};void setAutoReconnect(bool){};void setReconnectOnInitialFailure(bool){};void setDnsPolicy(uint8_t){};void setNoDelay(bool){};void setTimeout(uint32_t){};void setRoute(uint8_t){};void clearClientError(){};uint8_t clientError()const{return 0;}uint8_t dnsError()const{return 0;}uint8_t state()const{return 0;}uint8_t connect(const char*,uint16_t){++nativeConnect;return 0;}uint8_t connect(IPAddress,uint16_t){++nativeConnect;return 0;}bool connected(){return false;}int available(){return 0;}int read(uint8_t*,size_t){return 0;}size_t write(const uint8_t*,size_t){return 0;}};
