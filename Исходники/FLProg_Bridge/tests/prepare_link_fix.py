from pathlib import Path
import json,shutil,hashlib
r=Path(r'E:\FLP\Flprog_network');old=Path(r'E:\SAI\FLProg_Network\_work\bridge_flash_20261028');w=Path(r'E:\SAI\FLProg_Network\_work\ethernet_link_20261028');w.mkdir(exist_ok=True)
libs=w/'libraries'
if not libs.exists():shutil.copytree(old/'libraries',libs)
p=libs/'FLProg_Network/src/flprogNetwork.cpp';s=p.read_text(encoding='utf-8')
before='''        if (_dhcp && wiznetDhcpRef().bound())
        {
            _ethernetReady = true;
        }
        return;'''
after='''        // DHCP lease validity does not imply a physical link. Preserve the
        // last checked readiness until the next scheduled link probe; do not
        // resurrect a disconnected interface between checks.
        // Аренда DHCP не доказывает наличие линка: сохраняем результат
        // последней проверки без дополнительных SPI-обращений в каждом цикле.
        return;'''
assert s.count(before)==1;s=s.replace(before,after,1);p.write_text(s,encoding='utf-8')
folder=w/'FLE4D_Link';folder.mkdir(exist_ok=True)
for f in (old/'FLE4D_Bridge_Flash').iterdir():
 if f.is_file() and f.suffix!='.ino':shutil.copy2(f,folder/f.name)
sketch=folder/'FLE4D_Link.ino';sketch.write_text((old/'FLE4D_Bridge_Flash/FLE4D_Bridge_Flash.ino').read_text(encoding='utf-8').replace('1.0.9-BRIDGE-FLASH','1.0.10-BRIDGE-LINK'),encoding='utf-8')
d=json.loads((old/'PREPARED.json').read_text(encoding='utf-8'));d.update(sketch=str(sketch),libraries=str(libs),version='1.0.10-BRIDGE-LINK');(w/'PREPARED.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
# Exact production function extracted into a native fake-hardware harness.
start=s.index('void FLProgNetworkInterface::updateEthernet()');end=s.index('\nvoid FLProgNetworkInterface::updateActiveInterface()',start)
func=s[start:end]
harness=r'''#include <cstdint>
#include <cassert>
#include <cstdio>
uint32_t clockMs=0; uint32_t millis(){return clockMs;}
struct IPAddress {uint32_t v;IPAddress(int a=0,int b=0,int c=0,int d=0):v((uint32_t(a)<<24)|(b<<16)|(c<<8)|d){}bool operator!=(IPAddress o)const{return v!=o.v;}};
enum {FLPROG_SPI_STATUS_BUSY=1,FLPROG_WIZNET_LINK_OFF=0,FLPROG_WIZNET_LINK_ON=1,FLPROG_WIZNET_LINK_UNKNOWN=2,FLPROG_WIZNET_CHIP_W5100=51,FLPROG_NETWORK_ETHERNET_DHCP_ERROR=11,FLPROG_NETWORK_ETHERNET_LINK_ERROR=12,FLPROG_NETWORK_ETHERNET_HARDWARE_ERROR=13,FLPROG_NETWORK_NOT_ERROR=0};
struct Dhcp{bool lease=true,fail=false;int polls=0;void pool(){++polls;}bool failed(){return fail;}bool bound(){return lease;}IPAddress leasedIP(){return IPAddress(192,168,1,10);}};
struct Wiz{int link=1,status=0,chip=55,reads=0;int getLinkStatus(){++reads;return link;}int lastSpiStatus(){return status;}int spiOperationStatus(){return status;}int chipCode(){return chip;}};
struct FLProgNetworkInterface{bool _ethernetStarted=true,_ethernetReady=false,_dhcp=true,_ethernetConfigured=false;uint32_t _lastEthernetCheck=0,_checkStatusPeriod=100;int _error=0;IPAddress _wiznetIpCache;Dhcp d;Wiz w;bool staticOk=true;Dhcp& wiznetDhcpRef(){return d;}Wiz& wiznetRef(){return w;}bool configureStaticEthernet(){if(staticOk)_wiznetIpCache=IPAddress(192,168,1,20);return staticOk;}void updateEthernet();};
'''
tests=r'''
int main(){
 FLProgNetworkInterface n;
 clockMs=100;n.updateEthernet();assert(n._ethernetReady && n.w.reads==1);
 n.w.link=0;clockMs=200;n.updateEthernet();assert(!n._ethernetReady && n._error==12);
 for(clockMs=201;clockMs<300;++clockMs){n.updateEthernet();assert(!n._ethernetReady);assert(n.w.reads==2);}
 n.w.link=1;clockMs=300;n.updateEthernet();assert(n._ethernetReady && n._error==0);
 n.d.lease=false;clockMs=301;n.updateEthernet();assert(!n._ethernetReady);
 n.d.lease=true;clockMs=302;n.updateEthernet();assert(!n._ethernetReady);
 clockMs=400;n.updateEthernet();assert(n._ethernetReady);
 n.w.link=0;n.w.status=1;clockMs=500;n.updateEthernet();assert(n._ethernetReady);
 n.w.status=0;clockMs=600;n.updateEthernet();assert(!n._ethernetReady);
 n.d.fail=true;clockMs=601;n.updateEthernet();assert(!n._ethernetReady && n._error==11);
 FLProgNetworkInterface st;st._dhcp=false;clockMs=700;st.updateEthernet();assert(st._ethernetReady);st.w.link=0;clockMs=800;st.updateEthernet();assert(!st._ethernetReady);clockMs=801;st.updateEthernet();assert(!st._ethernetReady);
 FLProgNetworkInterface startup;clockMs=0;startup.updateEthernet();assert(!startup._ethernetReady && startup.w.reads==0);clockMs=100;startup.updateEthernet();assert(startup._ethernetReady);
 FLProgNetworkInterface legacy;legacy.w.link=2;legacy.w.chip=51;clockMs=200;legacy.updateEthernet();assert(legacy._ethernetReady);
 FLProgNetworkInterface invalid;invalid.w.link=2;clockMs=300;invalid.updateEthernet();assert(!invalid._ethernetReady && invalid._error==13);
 FLProgNetworkInterface rollover;rollover._lastEthernetCheck=0xfffffff0U;rollover._ethernetReady=false;clockMs=10;rollover.updateEthernet();assert(rollover.w.reads==0 && !rollover._ethernetReady);clockMs=100;rollover.updateEthernet();assert(rollover.w.reads==1 && rollover._ethernetReady);
 puts("PASS: DHCP link loss, 99 fast cycles, reconnect, lease acquisition, SPI busy, DHCP failure, static IP, startup, W5100, unknown hardware, millis rollover");
}
'''
(w/'link_test.cpp').write_text(harness+func+tests,encoding='utf-8')
# Negative control against the exact previous production function.
orig=(old/'libraries/FLProg_Network/src/flprogNetwork.cpp').read_text(encoding='utf-8');a=orig.index('void FLProgNetworkInterface::updateEthernet()');z=orig.index('\nvoid FLProgNetworkInterface::updateActiveInterface()',a)
(w/'link_test_before.cpp').write_text(harness+orig[a:z]+tests,encoding='utf-8')
print(w)
