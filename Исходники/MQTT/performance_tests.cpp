// Appended to the complete real MQTT implementation; only hardware is stubbed.
static std::vector<std::string> messages;
static void messageCallback(const char*,const uint8_t*p,size_t n,bool){messages.push_back(std::string((const char*)p,n));}
static std::vector<uint8_t> publishPacket(size_t payloadSize) {
 std::vector<uint8_t> r{0x30};uint32_t n=(uint32_t)payloadSize+3;
 do{uint8_t v=n%128;n/=128;r.push_back(v|(n?128:0));}while(n);
 r.push_back(0);r.push_back(1);r.push_back('t');
 for(size_t i=0;i<payloadSize;i++)r.push_back('a'+i%26);
 return r;
}
static void ready(FLProgNetworkMqttClient& c){
 static FLProgNetworkInterface n;assert(c.begin(n));c.setBroker("127.0.0.1");c.setClientId("gate");session(c);c._tcp.link=true;c._wantConnected=true;c.setKeepAlive(0);c.setMessageCallback(messageCallback);
}
static void networkPass(FLProgNetworkMqttClient& c){c.tcp()->pool();c.pool();}
void performanceTests(){
 {FLProgNetworkMqttClient c;ready(c);assert(c.pollInterval()==10);
  for(unsigned i=0;i<100000;i++){ticks=i/100;networkPass(c);}
  assert(c._tcp.pollCalls==100 && c._tcp.availableCalls==100);
  printf("IDLE 1 second / 100000 PLC scans: TCP polls=%zu, RX availability=%zu\n",c._tcp.pollCalls,c._tcp.availableCalls);
  // Unrelated TCP socket must still advance on every call.
  FLProgNetworkTcpClient other;for(int i=0;i<100;i++)other.pool();assert(other.pollCalls==100);
 }
 {FLProgNetworkMqttClient c;ready(c);c.setPollInterval(50);ticks=0;networkPass(c);ticks=49;networkPass(c);assert(c._tcp.pollCalls==1);ticks=50;networkPass(c);assert(c._tcp.pollCalls==2);
  c.setPollInterval(0);for(int i=0;i<20;i++)networkPass(c);assert(c._tcp.pollCalls==22);
 }
 {FLProgNetworkMqttClient c;ready(c);ticks=0;networkPass(c);ticks=3;
  assert(c.publish("t","command"));assert(c._tcp.writeCalls==0);networkPass(c);assert(c._tcp.writeCalls==1 && c.publishCount()==1);
  // Explicit command wakes before idle deadline, but queuing itself has no IO.
  ticks=4;assert(c.subscribe("t/#"));size_t before=c._tcp.writeCalls;networkPass(c);assert(c._tcp.writeCalls==before+1 && c.state()==FLPROG_MQTT_STATE_WAIT_SUBACK);
  for(int i=0;i<100;i++)networkPass(c);assert(c._tcp.writeCalls==before+1);
  c._tcp.rx={0x90,3,(uint8_t)(c._waitingPacketId>>8),(uint8_t)c._waitingPacketId,0};ticks=5;networkPass(c);assert(c.subscriptionCount()==1);
  ticks=6;c.disconnect();networkPass(c);assert(!c.connected() && c.state()==FLPROG_MQTT_STATE_IDLE);
 }
 {FLProgNetworkMqttClient c;ready(c);ticks=0;networkPass(c);messages.clear();c._tcp.rx=publishPacket(280);
  for(ticks=1;ticks<10;ticks++)networkPass(c);assert(messages.empty());
  for(ticks=10;ticks<=14;ticks++)networkPass(c);
  assert(messages.size()==1 && messages[0].size()==280 && c._tcp.readCalls==5 && c._tcp.byteReads==0 && c._tcp.maxRead==64);
  size_t before=c._tcp.pollCalls;ticks=15;networkPass(c);assert(c._tcp.pollCalls==before);
  printf("RX 286-byte MQTT packet: bulk reads=%zu, per-byte reads=%zu, max chunk=%zu, drain=4 ms after first read\n",c._tcp.readCalls,c._tcp.byteReads,c._tcp.maxRead);
 }
 {FLProgNetworkMqttClient c;ready(c);ticks=0;messages.clear();auto p=publishPacket(1);c._tcp.rx=p;c._tcp.rx.insert(c._tcp.rx.end(),p.begin(),p.end());networkPass(c);assert(messages.size()==2 && c._tcp.readCalls==1);
  // Parser state and byte order survive a partial packet, and transport short/zero read.
  c._tcp.rx=publishPacket(140);c._tcp.rxOffset=0;c._tcp.shortRead=3;ticks=10;
  for(int i=0;i<49;i++,ticks++)networkPass(c);assert(messages.size()==3 && messages.back().size()==140);
  c._tcp.rx=publishPacket(5);c._tcp.rxOffset=0;c._tcp.shortRead=0;ticks+=10;networkPass(c);assert(c._rxBacklog);auto r=c._tcp.readCalls;
  networkPass(c);assert(c._tcp.readCalls==r);++ticks;c._tcp.shortRead=9999;networkPass(c);assert(messages.size()==4);
 }
 {FLProgNetworkMqttClient c;ready(c);ticks=0;networkPass(c);std::string payload(280,'x');assert(c.publish("t",(const uint8_t*)payload.data(),payload.size()));
  for(ticks=1;ticks<=5;ticks++){networkPass(c);for(int j=0;j<100;j++)networkPass(c);}
  assert(c.publishCount()==1 && c._tcp.writeCalls==5 && c._tcp.maxWrite==64 && c._tcp.tx.size()==286);
  c._tcp.shortWrite=3;assert(c.publish("t","abcdefghijklmnop"));for(int i=0;i<7;i++,ticks++)networkPass(c);assert(c.publishCount()==2);
 }
 {FLProgNetworkMqttClient c;ready(c);ticks=100;networkPass(c);assert(c.subscribe("t"));networkPass(c);assert(c.state()==FLPROG_MQTT_STATE_WAIT_SUBACK);c.setResponseTimeout(7);
  // Unrelated publishes cannot renew the SUBACK deadline.
  for(ticks=101;ticks<=106;ticks++){auto p=publishPacket(1);c._tcp.rx.insert(c._tcp.rx.end(),p.begin(),p.end());networkPass(c);assert(c.busy());}
  ticks=107;networkPass(c);assert(c.error()==FLPROG_MQTT_ERROR_TIMEOUT && c.reconnectScheduled());
  ticks=c._reconnectAt-1;networkPass(c);assert(c.reconnectScheduled());ticks=c._reconnectAt;networkPass(c);assert(c.state()==FLPROG_MQTT_STATE_TCP_CONNECTING);
 }
 {FLProgNetworkMqttClient c;ready(c);ticks=0xfffffff8U;networkPass(c);ticks=1;networkPass(c);assert(c._tcp.pollCalls==1);ticks=2;networkPass(c);assert(c._tcp.pollCalls==2);
  c.setResponseTimeout(4);c._state=FLPROG_MQTT_STATE_WAIT_PINGRESP;c._stateStartedAt=0xfffffffeU;c._pollStarted=false;networkPass(c);assert(c.error()==FLPROG_MQTT_ERROR_TIMEOUT);
 }
 {FLProgNetworkMqttClient c;ready(c);ticks=0;networkPass(c);c.setPollInterval(900);c.setKeepAlive(1);c._lastTxAt=0;ticks=999;networkPass(c);assert(c.state()==FLPROG_MQTT_STATE_CONNECTED);ticks=1000;networkPass(c);assert(c.state()==FLPROG_MQTT_STATE_SENDING);ticks=1001;networkPass(c);assert(c.state()==FLPROG_MQTT_STATE_WAIT_PINGRESP);c._tcp.rx={0xd0,0};ticks=1002;networkPass(c);assert(c.pingResponseCount()==1);
  c._tcp.link=false;ticks=1902;networkPass(c);assert(c.reconnectScheduled());
 }
 {FLProgNetworkMqttClient c;ready(c);ticks=0;c._tcp.rx={0x30,0xff,0x7f};networkPass(c);assert(c.error()==FLPROG_MQTT_ERROR_PACKET_TOO_LARGE);
 }
 {FLProgNetworkMqttClient c;ready(c);ticks=0;assert(c.publish("t","pending"));c._tcp.shortWrite=0;c.setResponseTimeout(3);for(ticks=0;ticks<=3;ticks++)networkPass(c);assert(c.error()==FLPROG_MQTT_ERROR_TIMEOUT);
 }
 {FLProgNetworkMqttClient c;ready(c);ticks=0;c._state=FLPROG_MQTT_STATE_WAIT_CONNACK;c._sessionConnected=false;c.setResponseTimeout(0);for(ticks=0;ticks<100;ticks++)networkPass(c);assert(c.state()==FLPROG_MQTT_STATE_WAIT_CONNACK);c.cancel();networkPass(c);assert(c.state()==FLPROG_MQTT_STATE_IDLE);
  // Real command path: reconnect through TCP, CONNECT packet, CONNACK.
  c.setBroker("127.0.0.1");c.setClientId("gate");assert(c.connect());networkPass(c);assert(c.state()==FLPROG_MQTT_STATE_TCP_CONNECTING);++ticks;networkPass(c);++ticks;networkPass(c);assert(c.state()==FLPROG_MQTT_STATE_WAIT_CONNACK);c._tcp.rx={0x20,2,0,0};++ticks;networkPass(c);assert(c.connected());
 }
 {FLProgMqttUserBlocks b;FLProgNetworkInterface n; b.control(&n,true,false,false,"127.0.0.1",1883,"id","","",0,25);assert(!b.error() && b.mqtt.pollInterval()==25);
  for(int i=0;i<1000;i++)b.control(&n,true,false,false,"127.0.0.1",1883,"id","","",0,25);assert(b.mqtt._tcp.pollCalls==0);b.control(&n,false,false,false,"",1883,"id","","",0);b.control(&n,true,false,false,"127.0.0.1",1883,"id","","",0,1001);assert(b.error()==20);
  b.control(&n,false,false,false,"",1883,"id","","",0);b.control(&n,true,false,false,"127.0.0.1",1883,"id","","",0);assert(b.mqtt.pollInterval()==10);
 }
 puts("PASS: shared socket owner, configurable idle poll, immediate commands, 64-byte RX/TX, fragmented/coalesced packets, short/zero IO, timeouts, reconnect, keepalive, rollover, disabled timeout, Core v0.2 compatibility");
}
