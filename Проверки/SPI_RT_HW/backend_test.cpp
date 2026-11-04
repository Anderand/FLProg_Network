
#include <stdint.h>
#include <cassert>

#include "hardware/flprogSpiBackend.h"
struct RT_HW_STRUCT_SPI_DEV { uint8_t bus=0; int cs=-1; uint32_t speed=0; };
struct Base {
 int initialized=0,opened=0,closed=0,busy=0;
 void *spiGetLink(uint8_t bus) { return bus==1||bus==2 ? this : nullptr; }
 uint8_t getBusETH0(){return 1;} int getCsETH0(){return 6;}
 void spiInitDevice(RT_HW_STRUCT_SPI_DEV&){++initialized;}
 void spiSetBusy(uint8_t){++busy;} void spiClearBusy(uint8_t){--busy;}
 void spiBeginTransaction(RT_HW_STRUCT_SPI_DEV&){++opened;}
 void spiEndTransaction(RT_HW_STRUCT_SPI_DEV&){++closed;}
 void spiBeginCS(RT_HW_STRUCT_SPI_DEV&){} void spiEndCS(RT_HW_STRUCT_SPI_DEV&){}
 uint8_t spiTransfer(uint8_t value,uint8_t bus){return value+bus;}
} RT_HW_Base;
class FLProgWiznetInterface {
public:
 FLProgSpiBackend *selected=nullptr; SPIClass *object=nullptr; uint8_t bus=255; int cs=-1;
 ~FLProgWiznetInterface(){if(selected)selected->endTransaction();}
 FLProgWiznetInterface(){}
 FLProgWiznetInterface(int pin,uint8_t n):bus(n),cs(pin){}
 void setWiznetSpiBackend(FLProgSpiBackend *p){selected=p;p->configure(bus,cs,1000000);}
 void setSpiObject(SPIClass *p){object=p;selected=nullptr;}
};
#include "hardware/flprogRtHwWiznet.h"
int main(){
 FLProgWiznetInterface first(6,1),second(7,2),defaults;
 assert(first.selected!=second.selected);
 assert(first.selected->bus()==1&&first.selected->cs()==6);
 assert(second.selected->bus()==2&&second.selected->cs()==7);
 assert(defaults.selected->bus()==1&&defaults.selected->cs()==6);
 assert(first.selected->begin()&&second.selected->begin());
 assert(first.selected->beginTransaction());assert(first.selected->transfer(10)==11);
 first.selected->endTransaction();assert(RT_HW_Base.busy==0&&RT_HW_Base.opened==RT_HW_Base.closed);
 FLProgWiznetInterface unavailable(8,9);
 assert(!unavailable.selected->busAvailable());assert(!unavailable.selected->begin());
 assert(!unavailable.selected->beginTransaction());assert(unavailable.selected->status()==FLPROG_SPI_STATUS_UNAVAILABLE);
 auto *adapter=static_cast<FLProgRtHwSpiBackend<Base,RT_HW_STRUCT_SPI_DEV> *>(first.selected);
 adapter->setBusyProbe([](uint8_t,void*){return true;});
 assert(!adapter->beginTransaction());assert(adapter->status()==FLPROG_SPI_STATUS_BUSY);assert(RT_HW_Base.busy==0);
 struct OldRtHw {};
 OldRtHw old;assert(flprog_spi_detail::rtBusAvailable(&old,1,0));

}
