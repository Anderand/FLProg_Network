#include "http_read_native_adapter.h"
int main(){
 registerPlcReadHttpRoutes();auto &s=setupServer;
 s.args={{"op","hello"},{"channel","0"},{"token","form-token"}};
 s.invoke("/plc-api/start",HTTP_POST);assert(s.code==403&&plcReadJob.ticket==0);
 s.headers["Cookie"]="flpadmin="+adminSession;
 s.invoke("/plc-api/session",HTTP_GET);assert(s.code==200&&s.body.find("form-token")!=std::string::npos);
 s.args["token"]="wrong";s.invoke("/plc-api/start",HTTP_POST);assert(s.code==403&&plcReadJob.ticket==0);
 s.args["token"]="form-token";s.args["op"]="write";s.invoke("/plc-api/start",HTTP_POST);assert(s.code==403&&plcReadJob.ticket==0);
 s.args["op"]="hello";s.args["channel"]="256";s.invoke("/plc-api/start",HTTP_POST);assert(s.code==400);
 s.args["channel"]="-1";s.invoke("/plc-api/start",HTTP_POST);assert(s.code==400);
 s.args["channel"]="0";tcpBusy=true;s.invoke("/plc-api/start",HTTP_POST);assert(s.code==409&&plcReadJob.ticket==0);tcpBusy=false;
 s.invoke("/plc-api/start",HTTP_GET);assert(s.code==404&&plcReadJob.ticket==0);
 s.invoke("/plc-api/start",HTTP_POST);assert(s.code==202&&plcReadJob.ticket==1);
 s.invoke("/plc-api/start",HTTP_POST);assert(s.code==409&&plcReadJob.ticket==1);
 Port a,b;a.other=&b;b.other=&a;flprog_bridge::Server server("{\"model\":\"native-http-test\"}");
 for(int i=0;i<100&&plcReadJob.client.busy();++i){plcReadJob.client.pool(a,clockNow,64);server.pool(b,clockNow,64);++clockNow;}
 assert(plcReadJob.client.state()==FLProgReadClient::Done);
 s.args={{"ticket","99"}};s.invoke("/plc-api/result",HTTP_GET);assert(s.code==409);
 s.args["ticket"]="1";auto before=a.writes;
 for(int i=0;i<10;++i){s.invoke("/plc-api/result",HTTP_GET);assert(s.code==200&&s.body.find("\"state\":3")!=std::string::npos);}
 assert(a.writes==before);
 setupMode=true;s.invoke("/plc-api/result",HTTP_GET);assert(s.code==503);setupMode=false;
 WiFi.value=0;s.invoke("/plc-api/session",HTTP_GET);assert(s.code==503);WiFi.value=WL_CONNECTED;
 s.headers.clear();s.invoke("/plc-api/result",HTTP_GET);assert(s.code==403);
 s.headers["Cookie"]="flpadmin="+adminSession;s.invoke("/plc",HTTP_GET);assert(s.code==200&&s.body.find("Только чтение")!=std::string::npos);
 puts("PASS: actual HTTP routes, cookie/token, read-only allowlist, channel validation, busy/ownership, tickets, cached result, AP/network gating");
}
