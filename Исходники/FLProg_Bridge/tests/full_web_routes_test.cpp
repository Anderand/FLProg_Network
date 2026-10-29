#include "http_read_native_adapter.h"
int main(){
 MockServer viewer;String token="viewer-only";registerPlcReadHttpRoutes();registerReadRpc(viewer,token,true);
 viewer.headers["Cookie"]="flpadmin="+adminSession;
 viewer.args={{"token","form-token"},{"op","hello"},{"channel","0"}};
 viewer.invoke("/plc-api/start",HTTP_POST);assert(viewer.code==403&&plcReadJob.ticket==0);
 viewer.args["token"]="viewer-only";tcpBusy=true;viewer.invoke("/plc-api/start",HTTP_POST);assert(viewer.code==409);tcpBusy=false;
 viewer.invoke("/plc-api/start",HTTP_POST);assert(viewer.code==202&&viewerLease.active(clockNow));
 setupServer.headers=viewer.headers;setupServer.args={{"token","form-token"},{"op","hello"},{"channel","0"}};setupServer.invoke("/plc-api/start",HTTP_POST);assert(setupServer.code==409);
 plcReadJob.client.cancel();clockNow=5001;assert(!viewerLease.active(clockNow));
 for(const char* op:{"write","command","reset"}){viewer.args["op"]=op;viewer.invoke("/plc-api/start",HTTP_POST);assert(viewer.code==(std::string(op)=="write"?403:400));}
 viewer.args["op"]="chunk";viewer.args["count"]="225";viewer.args["offset"]="0";viewer.invoke("/plc-api/start",HTTP_POST);assert(viewer.code==400);
 viewer.args["op"]="batch";viewer.args["channels"]="1,1";viewer.invoke("/plc-api/start",HTTP_POST);assert(viewer.code==400);
 uint8_t channels[16],n;assert(parseChannelList("0,1,255",channels,n)&&n==3);assert(!parseChannelList("1,",channels,n));assert(!parseChannelList("256",channels,n));
 FLProgViewerLease lease;assert(lease.touch(0xfffffff0u,false));assert(lease.active(0xfffffff0u+4999u));assert(!lease.active(0xfffffff0u+5000u));assert(!lease.touch(1,true));
 puts("PASS: viewer/admin token separation, TCP exclusion, lease expiry/wrap, no writes, chunk bounds and batch validation");
}
