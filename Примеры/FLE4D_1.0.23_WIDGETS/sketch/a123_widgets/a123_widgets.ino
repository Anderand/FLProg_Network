#define RT_HW_FLPROG_PRG "FLProg 9.8.1 - SP 0.0"
#define RT_HW_FLPROG_PRJ "FLProg 1.1.1 - SP 0.0"



#include "flprogUtilites.h"
#include "RT_HW_FLProg_ADC_i2c_ADS1115.hpp"
#include "RT_HW_FLProg_PWM_STM32F407V_PA12_bright.hpp"
#include "RT_HW_FLProg_DAC_BUS.hpp"
#include "RT_HW_FLProg_i2c_TCA9555_KEY_BTN5.hpp"
#include "RT_HW_FLProg_ADC_BUS.hpp"
#include "RT_HW_FLProg_PWM_STM32F407V_PC1_sound.hpp"
#include <a123_webui.h>
#include <flprogOtaUniversalBlock.h>

#include "flprogEthernet.h"
#include "RT_HW_FLProg_DAC_pin_STM32.hpp"
#ifdef RT_HW_SPECIAL_INCLUDE
#include RT_HW_SPECIAL_INCLUDE
#endif
#ifdef RT_HW_SPECIAL_ISTANCE
RT_HW_SPECIAL_ISTANCE
#endif
FLProgWiznetInterface WiznetInterface_44431013(PB12, 0);
#define FLPROG_WIZNET_INTERFACE1 WiznetInterface_44431013

RT_HW_FLProg_ADC_BUS FLProgADC;
RT_HW_FLProg_ADC_i2c_ADS1115  FLProgADS1115(1, 0x48, 400000,100); //--ADS1115: bus,adr, speed,period;
RT_HW_FLProg_DAC_BUS FLProgDAC;
RT_HW_FLProg_DAC_pin_STM32 FLProgDAC_STM32;
RT_HW_FLProg_i2c_TCA9555_KEY_BTN5   FLProgBTN5(0,0x25,400000,100); //--Пульт 5 кнопок TCA9555: bus,adr,speed,period;
RT_HW_FLProg_PWM_STM32F407V_PC1_sound 	FLProgSound;	//--Звук через программный PWM 0-100:  частота 2700Гц, уровень(0-100)=50;
RT_HW_FLProg_PWM_STM32F407V_PA12_bright	FLProgBright;	//--Яркость через программный PWM 0-100: частота 1000Гц, уровень(0-100)=50;
#define RT_HW_FLProg_i2c_ADS1115_INTERFACE1 FLProgADS1115	//--Доступ к ADS1115;
#define RT_HW_FLProg_ADC_BUS_INTERFACE1 FLProgADC
#define RT_HW_FLProg_ADC_i2c_ADS1115_INTERFACE1 FLProgADS1115
#define RT_HW_FLProg_i2c_TCA9555_KEY_BTN5_INTERFACE1 FLProgBTN5 //--Доступ к пульту BTN5;



FLProgOtaUniversalBlock a123Ota;
static const String a123OtaPassword;
static const String a123OtaVersion("1.0.23-WIDGETS");

void setup()
{


RT_HW_Base.spiSetPins(PB13, PB14, PB15, 0);
RT_HW_Base.spiSetPins(PB3, PB4, PB5, 1);
RT_HW_Base.i2cSetPins(PB9, PB8, 0);
RT_HW_Base.i2cSetPins(PB11, PB10, 1);
RT_HW_Base.uartSetPins(PA10, PA9, 1);
RT_HW_Base.uartSetPins(PD6, PD5, 2);
RT_HW_Base.uartSetPins(PD9, PD8, 3);
RT_HW_Base.uartSetPins(PC11, PC10, 4);
RT_HW_Base.uartSetPins(PD2, PC12, 5);
RT_HW_Base.uartSetPins(PC7, PC6, 6);
RT_HW_Base.shed.quick.qnt = 5;
RT_HW_Base.shed.fast.qnt = 4;
RT_HW_Base.shed.slow.qnt = 4;
RT_HW_Base.shed.back.qnt = 5;
RT_HW_Base.shed.frdm.qnt = 50;
RT_HW_Base.spiBegin(0);
WiznetInterface_44431013.mac(0x78,  0xAC,  0xC0,  0xE0,  0x22,  0xD4);
WiznetInterface_44431013.setSkippingEvents(0);
WiznetInterface_44431013.setDhcp();
RT_HW_Base.shed.sysQuick.qnt = 101; 
//--------------------------------------------------------------------------------------------------
//                                  ADC BUS
//--------------------------------------------------------------------------------------------------
  FLProgADC.setQnt(4);
  if(!FLProgADC.AD[0].custom){FLProgADC.setCorrect(0,10000); FLProgADC.AD[0].custom=1; }	//--AD.0
  if(!FLProgADC.AD[1].custom){FLProgADC.setCorrect(1,10000); FLProgADC.AD[1].custom=1; }	//--AD.1
  if(!FLProgADC.AD[2].custom){FLProgADC.setCorrect(2,10000); FLProgADC.AD[2].custom=1; }	//--AD.2
  if(!FLProgADC.AD[3].custom){FLProgADC.setCorrect(3,10000); FLProgADC.AD[3].custom=1; }	//--AD.3
//--------------------------------------------------------------------------------------------------
//                                  ADS1115
//--------------------------------------------------------------------------------------------------
  if(!FLProgADS1115.custom){
  	FLProgADS1115.setStartAD(0);	  	//--AIN0...AIN3 подключаются к AD[0]...AD[3];
  	FLProgADS1115.setPGA(RT_HW_FLProg_ADC_i2c_ADS1115_PGA_2048);	 	 //--Диапазон ADS1115 ±2.048 В;
 	FLProgADS1115.setSPS(RT_HW_FLProg_ADC_i2c_ADS1115_SPS_128);   //--Скорость преобразования 128 SPS;
	FLProgADS1115.setDividerAD(5200);   //--Коэффициент входного делителя: 5.200;
 	FLProgADS1115.setRangeMV(10000);   //--Номинальный диапазон входа: 0...10000 мВ;
	FLProgADS1115.setRetry(100,2000);   //--Динамическая пауза после ошибки: 100...2000 мс;
	FLProgADS1115.custom=1;
  }
//--------------------------------------------------------------------------------------------------
//							STM32 DAC PA4,PA5
//--------------------------------------------------------------------------------------------------
  FLProgDAC.setQnt(2);
//--------------------------------------------------------------------------------------------------
  if(!FLProgDAC.DA[0].custom){
  	FLProgDAC.DA[0].setSource(RT_HW_FLProg_DAC_SOURCE_AUTO);
	FLProgDAC.DA[0].setSafeSystem(0);	
	FLProgDAC.DA[0].setPermit(1);
	FLProgDAC.setCorrect(0,10000);
	FLProgDAC.DA[0].custom=1;
  }
//--------------------------------------------------------------------------------------------------
  if(!FLProgDAC.DA[1].custom){
  	FLProgDAC.DA[1].setSource(RT_HW_FLProg_DAC_SOURCE_AUTO);
  	FLProgDAC.DA[1].setSafeSystem(0);
  	FLProgDAC.DA[1].setPermit(1);
	FLProgDAC.setCorrect(1,10000);
 	FLProgDAC.DA[1].custom=1;
  }
//--------------------------------------------------------------------------------------------------
  if(!FLProgDAC_STM32.custom){
  	FLProgDAC_STM32.setPA4(0); //--PA4 получает DA[0];
  	FLProgDAC_STM32.setPA5(1); //--PA5 получает DA[1];
  	FLProgDAC_STM32.custom=1;
  }
//--------------------------------------------------------------------------------------------------

flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)1, &FLPROG_WIZNET_INTERFACE1);
FLPROG_WEBUI_BEGIN_SELECTED();


flprog::specialSetup();
}
void loop()
{
 a123Ota.control(true, 1, a123OtaPassword, a123OtaVersion);

RT_HW_Base.sheduler();
flprog::specialPool();
if (RT_HW_Base.shed.sysQuick.num == 1) {FLProgBTN5.pool();}
if (RT_HW_Base.shed.sysQuick.num == 2) {FLProgSound.pool();}
if (RT_HW_Base.shed.sysQuick.num == 3) {FLProgBright.pool();}
if (RT_HW_Base.shed.sysQuick.num == 4) { FLProgADS1115.pool(FLProgADC);  FLProgADC.pool();}
if (RT_HW_Base.shed.sysQuick.num == 5) {FLProgDAC.pool(); FLProgDAC_STM32.pool(FLProgDAC);}

 if(RT_HW_Base.shed.sysQuick.num == 1) {
WiznetInterface_44431013.pool();
}





//Плата:1
if (RT_HW_Base.shed.frdm.num == 1) {
}







}



