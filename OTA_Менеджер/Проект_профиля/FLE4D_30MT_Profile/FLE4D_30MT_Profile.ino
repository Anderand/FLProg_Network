#define RT_HW_FLPROG_PRG "FLProg 9.8.1 - SP 0.0"
#define RT_HW_FLPROG_PRJ "FLProg 9.8.1 - SP 0.0"
#define RT_HW_KEY_CONTROL_DEBUG //--Разрешение диагностики от RT_HW_KEY_CONTROL.h;
#include "RT_HW_BASE.h"
#include "flprogUtilites.h"
#include "RT_HW_CONSOLE.h"
#include "flprogEthernet.h"
#include "RT_HW_FLProg_ADC_i2c_ADS1115.hpp"
#include "RT_HW_RTC_RX8025.hpp"
#include "RT_HW_FLProg_i2c_TCA9555_KEY_BTN5.hpp"
#include "flprogUart.h"
#include "RT_HW_OLED_DEBUG.hpp"
#include "RT_HW_KEY_CONTROL.h"
#include "flprogExternalEEPROM.h"
#include "RT_HW_FLProg_ADC_BUS.hpp"
#include "RT_HW_FLProg_DAC_pin_STM32.hpp"
#include "RT_HW_TEST_GPIO.hpp"
#include "flprogOled.h"
#include "flprogModbusRTU.h"
#include "RT_HW_FLProg_PWM_STM32F407V_PC1_sound.hpp"
#include "RT_HW_FLProg_DAC_BUS.hpp"
#include <flprogOtaUniversalBlock.h>
#include <FLE4D-30MT_webui.h>
#include "flprogModbusTCP.h"
#include "RT_HW_FLProg_PWM_STM32F407V_PA12_bright.hpp"
#ifdef RT_HW_SPECIAL_INCLUDE
#include RT_HW_SPECIAL_INCLUDE
#endif
#ifdef RT_HW_SPECIAL_ISTANCE
RT_HW_SPECIAL_ISTANCE
#endif
FlprogUartExecutor FLProgUart;
#define FLPROG_UART_EXECUTOR FLProgUart
FLProgUartParametrs Uart_73348587_data;
FLProgUartParametrs Uart_216360334_data;
FLProgUartParametrs Uart_156610300_data;
FLProgUartParametrs Uart_197108242_data;
FLProgUartParametrs Uart_194105114_data;
FLProgUartParametrs Uart_1830927_data;
FLProgExternalEEPROM ExternalEEPROM_252608257(1, 0x50, 6, 245, 0);
RT_HW_RTC_RX8025_ID FLProgWatch;
#define FLPROG_WATCH FLProgWatch
FLProgWiznetInterface WiznetInterface_165513604(PB12, 0);
#define FLPROG_WIZNET_INTERFACE1 WiznetInterface_165513604
RT_HW_STRUCT_SHED_TASK consoleVarBlock_17_Task;
String consoleVarBlock_17_valueArray[4];
RT_HW_TEST_GPIO FLProgTestGen_70;
RT_HW_STRUCT_SHED_TASK consoleVarBlock_22_Task;
int16_t consoleVarBlock_22_valueArray[2];
RT_HW_FILTER_RING_AVERAGE<uint32_t, 5> TaskManager_Filter;
//========================================================================================================================================
//++++ Начало объявления дисплея TFT ST7735 RGB (SPI1) ++++
//========================================================================================================================================
//!!!!! Дисплей
FlprogSpiST7735Chip oled_138862728_chip;
FlprogOledDisplay oled_138862728(7);
//#### Экран Экран 1 - 1.ГЛАВНЫЙ
FlprogOledScreen oled_scr_48392945(22);
//------  Виджет Цифровое значение - eth.err
FlprogOledNumberValueWidget oled_fld_nv_117332420(0, 101, 73, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - eth.status
FlprogOledNumberValueWidget oled_fld_nv_166583876(0, 35, 73, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Битовое значение - eth.ready
FlprogOledBooleanValueWidget oled_fld_bv_59587394(0, 5, 73, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Строковое значение - eth.ds
FlprogOledStringValueWidget oled_fld_sv_226067155(0, 4, 64, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Строковое значение - eth.gate
FlprogOledStringValueWidget oled_fld_sv_64681359(0, 4, 55, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Строковое значение - eth.mask
FlprogOledStringValueWidget oled_fld_sv_253709455(0, 4, 46, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Строковое значение
FlprogOledStringValueWidget oled_fld_sv_56713862(0, 4, 37, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Битовое значение
FlprogOledBooleanValueWidget oled_fld_bv_138544549(0, 152, 2, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Список строк
FlprogOledNumberListValueWidget oled_fld_nvl_171661469(0, 58, 16, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO, 5);
//------  Виджет Цифровое значение - Время работы в секундах
FlprogOledNumberValueWidget oled_fld_nv_164605960(0, 58, 26, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_PURPLE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_69983135(0, 16, 16, "-", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - День
FlprogOledNumberValueWidget oled_fld_nv_67445460(0, 4, 15, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Месяц
FlprogOledNumberValueWidget oled_fld_nv_156182767(0, 22, 15, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Год.xx
FlprogOledNumberValueWidget oled_fld_nv_34185301(0, 40, 15, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_150445619(0, 34, 16, "-", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_213810209(0, 34, 4, ":", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Секунды
FlprogOledNumberValueWidget oled_fld_nv_36732314(0, 40, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Минуты
FlprogOledNumberValueWidget oled_fld_nv_134819151(0, 22, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Часы
FlprogOledNumberValueWidget oled_fld_nv_25335513(0, 4, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Быстродействие
FlprogOledNumberValueWidget oled_fld_nv_196997419(0, 5, 26, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_PURPLE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_46985861(0, 57, 4, "1.ГЛАВНЫЙ", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_GREEN, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_54726843(0, 16, 4, ":", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//#### Экран Экран 2 - 2.ДЕМО
FlprogOledScreen oled_scr_200663618(13);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_93658359(0, 17, 4, ":", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Часы
FlprogOledNumberValueWidget oled_fld_nv_198685733(0, 4, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Минуты
FlprogOledNumberValueWidget oled_fld_nv_175148948(0, 22, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Секунды
FlprogOledNumberValueWidget oled_fld_nv_32528453(0, 41, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_16243548(0, 35, 4, ":", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_30079150(0, 34, 16, "-", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Год.xx
FlprogOledNumberValueWidget oled_fld_nv_41069956(0, 40, 16, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Месяц
FlprogOledNumberValueWidget oled_fld_nv_61032334(0, 22, 16, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - День
FlprogOledNumberValueWidget oled_fld_nv_108347373(0, 4, 15, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_37186508(0, 16, 16, "-", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_46475982(0, 60, 3, "2.ДЕМО", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_GREEN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Быстродействие
FlprogOledNumberValueWidget oled_fld_nv_26807825(0, 110, 3, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_PURPLE, RT_HW_OLED_FILL_NO);
//------  Виджет Прямоугольник - Рамка
FlprogOledRectWidget oled_fld_rect_43854780(0, 0, 0, 159, 127, RT_HW_OLED_FILL_ORANGE, RT_HW_OLED_FILL_NO, 1);
//#### Экран Экран 3 - 3.ВХОДЫ
FlprogOledScreen oled_scr_120866812(20);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_132134098(0, 115, 15, "mV", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_140658593(0, 73, 55, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_125727405(0, 73, 45, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_245400241(0, 73, 35, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_41839462(0, 36, 15, "SYS", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_258438336(0, 76, 15, "RAW", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_196593743(0, 73, 25, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - AD0.mV
FlprogOledNumberValueWidget oled_fld_nv_248199219(0, 110, 25, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - AD2.mV
FlprogOledNumberValueWidget oled_fld_nv_113347223(0, 110, 45, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - AD1.mV
FlprogOledNumberValueWidget oled_fld_nv_121085400(0, 110, 35, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - AD3.mV
FlprogOledNumberValueWidget oled_fld_nv_256356637(0, 110, 55, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст  - Заголовок
FlprogOledTextWidget oled_fld_txt_239059671(0, 62, 4, "3.ВХОДЫ", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_YELLOW, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Быстродействие
FlprogOledNumberValueWidget oled_fld_nv_97585484(0, 110, 3, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_PURPLE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - AD.0
FlprogOledNumberValueWidget oled_fld_nv_105742732(0, 4, 25, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - AD.1
FlprogOledNumberValueWidget oled_fld_nv_191669495(0, 4, 35, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - AD.2
FlprogOledNumberValueWidget oled_fld_nv_16086042(0, 4, 45, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - AD.3
FlprogOledNumberValueWidget oled_fld_nv_115923925(0, 4, 55, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Битовое значение - XVcc
FlprogOledBooleanValueWidget oled_fld_bv_183590754(0, 10, 90, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - DIN.1
FlprogOledNumberValueWidget oled_fld_nv_31350185(0, 10, 103, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_YELLOW, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - DIN.2
FlprogOledNumberValueWidget oled_fld_nv_58867727(0, 9, 116, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_YELLOW, RT_HW_OLED_FILL_NO);
//#### Экран Экран 4 - 4.ВЫХОДЫ
FlprogOledScreen oled_scr_29161469(9);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_245388940(0, 5, 59, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_ORANGE, RT_HW_OLED_FILL_NO);
//------  Виджет Линейный индикатор
FlprogOledGaudeWidget oled_fld_gaude_107943078(0, 3, 44, 153, 54, RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_WHITE, 1);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_185289915(0, 4, 33, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_PURPLE, RT_HW_OLED_FILL_NO);
//------  Виджет Линейный индикатор
FlprogOledGaudeWidget oled_fld_gaude_215774609(0, 3, 19, 153, 29, RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_WHITE, 1);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_161568141(0, 10, 113, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_GREEN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_37782062(0, 10, 102, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_GREEN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_58823822(0, 110, 3, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_PURPLE, RT_HW_OLED_FILL_NO);
//------  Виджет Прямоугольник - Рамка экрана
FlprogOledRectWidget oled_fld_rect_203196789(0, 1, 1, 160, 128, RT_HW_OLED_FILL_ORANGE, RT_HW_OLED_FILL_NO, 1);
//------  Виджет Текст  - Заголовок
FlprogOledTextWidget oled_fld_txt_30747158(0, 57, 4, "4.ВЫХОДЫ", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_GREEN, RT_HW_OLED_FILL_NO);
//#### Экран Экран 5 - 5.НАСТРОЙКА ПРОЕКТА
FlprogOledScreen oled_scr_73848182(8);
//------  Виджет Битовое значение
FlprogOledBooleanValueWidget oled_fld_bv_5505156(0, 126, 24, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Битовое значение
FlprogOledBooleanValueWidget oled_fld_bv_206232748(0, 112, 23, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_37048924(0, 92, 23, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Список строк
FlprogOledNumberListValueWidget oled_fld_nvl_126836762(0, 7, 24, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO, 5);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_196179951(0, 110, 3, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_PURPLE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст  - Заголовок
FlprogOledTextWidget oled_fld_txt_248331703(0, 56, 4, "5.ПРОЕКТ", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_GREEN, RT_HW_OLED_FILL_NO);
//------  Виджет Прямоугольник
FlprogOledRectWidget oled_fld_rect_28526112(0, 3, 21, 74, 32, RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO, 1);
//------  Виджет Прямоугольник - Рамка
FlprogOledRectWidget oled_fld_rect_168959227(0, 1, 0, 160, 127, RT_HW_OLED_FILL_ORANGE, RT_HW_OLED_FILL_NO, 1);
//#### Экран Экран 6 - 6.НАСТРОЙКА ПАНЕЛИ
FlprogOledScreen oled_scr_127594733(24);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_125668277(0, 110, 3, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_MAGENTA, RT_HW_OLED_FILL_NO);
//------  Виджет Текст  - Время звука
FlprogOledTextWidget oled_fld_txt_200832565(0, 4, 43, "Время звука=", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_PURPLE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_221838477(0, 3, 30, "Громкость=", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_PURPLE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_53392629(0, 65, 16, "Яркость=", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_BLUE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Номер поля
FlprogOledNumberValueWidget oled_fld_nv_50179035(0, 142, 16, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_GREEN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Значение SoundTime
FlprogOledNumberValueWidget oled_fld_nv_197292450(0, 76, 43, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Значение SoundLevel
FlprogOledNumberValueWidget oled_fld_nv_62290336(0, 66, 30, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Значение BrigthLevel
FlprogOledNumberValueWidget oled_fld_nv_222539793(0, 115, 16, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_39904101(0, 18, 4, ":", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Часы
FlprogOledNumberValueWidget oled_fld_nv_111504103(0, 4, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Минуты
FlprogOledNumberValueWidget oled_fld_nv_119285938(0, 25, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Секунды
FlprogOledNumberValueWidget oled_fld_nv_67458057(0, 46, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_39400095(0, 39, 4, ":", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_134527829(0, 39, 15, "-", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Год.xx
FlprogOledNumberValueWidget oled_fld_nv_196225129(0, 46, 15, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Месяц
FlprogOledNumberValueWidget oled_fld_nv_90867036(0, 25, 15, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - День
FlprogOledNumberValueWidget oled_fld_nv_94987733(0, 4, 15, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст
FlprogOledTextWidget oled_fld_txt_192733939(0, 18, 15, "-", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Текст  - Заголовок 6
FlprogOledTextWidget oled_fld_txt_96687945(0, 62, 4, "6.ПАНЕЛЬ", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_GREEN, RT_HW_OLED_FILL_NO);
//------  Виджет Прямоугольник - Рамка BrightLevel
FlprogOledRectWidget oled_fld_rect_118135175(0, 63, 14, 133, 25, RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO, 1);
//------  Виджет Прямоугольник - Рамка времени
FlprogOledRectWidget oled_fld_rect_135629005(0, 2, 2, 59, 25, RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO, 1);
//------  Виджет Прямоугольник - Рамка Sound
FlprogOledRectWidget oled_fld_rect_114909367(0, 2, 29, 84, 38, RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO, 1);
//------  Виджет Прямоугольник - Рамка TimeSound
FlprogOledRectWidget oled_fld_rect_207741416(0, 2, 41, 101, 52, RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO, 1);
//------  Виджет Прямоугольник - Рамка контур
FlprogOledRectWidget oled_fld_rect_110646806(0, 0, 0, 159, 127, RT_HW_OLED_FILL_ORANGE, RT_HW_OLED_FILL_NO, 1);
//#### Экран Экран 7 - 0.ЗАСТАВКА
FlprogOledScreen oled_scr_83073005(9);
//------  Виджет Текст  - чистую воду!
FlprogOledTextWidget oled_fld_txt_233296239(0, 86, 87, "чистую воду!", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст  - Планете Земля
FlprogOledTextWidget oled_fld_txt_216188546(0, 60, 75, "Планете Земля", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Текст  - EIS
FlprogOledTextWidget oled_fld_txt_114202373(0, 2, 73, "EIS", 3, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_GREEN, RT_HW_OLED_FILL_NO);
//------  Виджет Текст  -  запрограммирует тебя.
FlprogOledTextWidget oled_fld_txt_245507075(0, 27, 59, " запрограммирует тебя.", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Битовое значение - Звездочка
FlprogOledBooleanValueWidget oled_fld_bv_193114660(0, 144, 11, 2, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_MAGENTA, RT_HW_OLED_FILL_NO);
//------  Виджет Текст  - Иначе реальность
FlprogOledTextWidget oled_fld_txt_212539800(0, 11, 48, "Иначе реальность", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Текст  - Программируй реальность!
FlprogOledTextWidget oled_fld_txt_39059323(0, 5, 36, "Программируй реальность!", 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_CYAN, RT_HW_OLED_FILL_NO);
//------  Виджет Иконка - Иконка - сигнал связи
FlprogOledIconWidget oled_fld_icon_145371210(0, 6, 12, 8, 8, 51, 2, RT_HW_OLED_FILL_MAGENTA, RT_HW_OLED_FILL_NO);
//------  Виджет Текст  - FLProg
FlprogOledTextWidget oled_fld_txt_43319858(0, 30, 7, "FLProg", 3, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_MAGENTA, RT_HW_OLED_FILL_NO);
//========================================================================================================================================
//++++ Конец объявления дисплея TFT ST7735 RGB (SPI1) ++++
//========================================================================================================================================
//========================================================================================================================================
//++++ Начало объявления дисплея OLED SH1107 MONO (I2C0) ++++
//========================================================================================================================================
//!!!!! Дисплей
FlprogI2cSH1107Chip oled_156902651_chip;
FlprogOledDisplay oled_156902651(1);
//#### Экран Экран 1 - key.blink
FlprogOledScreen oled_scr_263585980(16);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_207743169(0, 97, 56, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Битовое значение
FlprogOledBooleanValueWidget oled_fld_bv_143217628(0, 51, 94, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Битовое значение
FlprogOledBooleanValueWidget oled_fld_bv_123679529(0, 29, 94, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Битовое значение
FlprogOledBooleanValueWidget oled_fld_bv_264786981(0, 6, 94, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_218060352(0, 3, 36, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Список строк
FlprogOledNumberListValueWidget oled_fld_nvl_133196007(0, 53, 77, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO, 4);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_178356505(0, 4, 77, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_168504598(0, 46, 14, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_212028031(0, 3, 66, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_151802975(0, 3, 25, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_63387461(0, 3, 56, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Битовое значение - Blink 500
FlprogOledBooleanValueWidget oled_fld_bv_183396639(0, 117, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Время работы
FlprogOledNumberValueWidget oled_fld_nv_80992857(0, 57, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение - Быстродействие
FlprogOledNumberValueWidget oled_fld_nv_66101037(0, 3, 4, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_198500841(0, 81, 14, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//------  Виджет Цифровое значение
FlprogOledNumberValueWidget oled_fld_nv_123085538(0, 3, 14, 1, (RT_HW_OLED_TEXT_NORMAL), RT_HW_OLED_FILL_WHITE, RT_HW_OLED_FILL_NO);
//========================================================================================================================================
//++++ Конец объявления дисплея OLED SH1107 MONO (I2C0) ++++
//========================================================================================================================================
int32_t table_4_1_A[] = {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43, 50, 51, 52, 53, 54, 55, 56, 57, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109};
int32_t table_4_1_2_A[] = {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43, 50, 51, 52, 53, 54, 55, 56, 57, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109};
ModbusSlaveRTU Modbus_144774688(2, &FLProgUart);
ModbusSlaveRTU Modbus_45921880(4, &FLProgUart);
ModbusSlaveRTU Modbus_251262745(5, &FLProgUart);
ModbusSlaveRTU Modbus_246570956(6, &FLProgUart);
ModbusSlaveRTU Modbus_32382178(1, &FLProgUart);
ModbusSlaveTCP Modbus_95643830(&WiznetInterface_165513604);
ModbusMasterRTU Modbus_83290452(3, 1, &FLProgUart);
bool EN;
int16_t NET_NUM;
String PASSWORD;
bool SUPPORTED;
bool READY;
bool BUSY;
bool FAULT;
int32_t STATE;
int32_t ERR;
int32_t RX_BYTES;
FLProgOtaUniversalBlock flprogOtaUniversal;
bool _gtv20 = 0; //Готовность консоли
uint8_t _gtv25 = 0;
uint8_t _gtv8 = 0;
bool _gtv26 = 0;
bool _gtv51 = 0; //Управление через пользовательское приложение
bool _gtv31 = 0; //Управление через регистры Modbus.Slave
bool _gtv23 = 0; //Управление через блок генератора теста
uint16_t _gtv50 = 0;
uint16_t _gtv24 = 0;
uint16_t _gtv53 = 0;
uint16_t _gtv57 = 0;
uint16_t _gtv14 = 0;
uint16_t _gtv38 = 0;
uint16_t _gtv39 = 0;
uint16_t _gtv40 = 0;
bool _gtv47 = 0;
uint16_t _gtv41 = 0;
uint16_t _gtv42 = 0;
uint16_t _gtv43 = 0;
uint16_t _gtv44 = 0;
uint16_t _gtv45 = 0;
uint16_t _gtv46 = 0;
uint16_t _gtv48 = 0;
uint16_t _gtv49 = 0;
bool _gtv35 = 0;
uint8_t _gtv36 = 0;
uint8_t _gtv33 = 0;
uint16_t _gtv37 = 0;
bool _gtv32 = 0;
uint16_t _gtv34 = 0;
bool _gtv12 = 0;
bool _gtv55 = 0;
bool _gtv22 = 0;
uint8_t _gtv21 = 5;
uint8_t _gtv56 = 0;
bool _gtv28 = 0;
bool _gtv29 = 0;
bool _gtv30 = 0;
bool _gtv7 = 0;
bool _gtv10 = 0;
bool _gtv11 = 0;
bool _gtv13 = 0;
bool _gtv15 = 0;
bool _gtv16 = 0;
bool _gtv19 = 0;
bool _gtv1 = 0;
bool _gtv2 = 0;
bool _gtv3 = 0;
bool _gtv4 = 0;
bool _gtv5 = 0;
bool _gtv6 = 0;
uint8_t _gtv52 = 6;
uint8_t _gtv27 = 0;
String _gtv58 = "";
String _gtv59 = "";
String _gtv60 = "";
String _gtv61 = "";
uint8_t _gtv62 = 0;
uint8_t _gtv63 = 0;
bool _gtv64 = 0;
FlprogDiscreteInputPin FLProgPin_PD3(PD3, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PD4(PD4, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PD7(PD7, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PD10(PD10, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PD11(PD11, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PD12(PD12, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PD13(PD13, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PD14(PD14, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PC8(PC8, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PC9(PC9, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PC13(PC13, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PE0(PE0, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PE1(PE1, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PE2(PE2, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PE3(PE3, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PE4(PE4, FLPROG_PULL_NOT_MODE, 1);
FlprogDiscreteInputPin FLProgPin_PA15(PA15, FLPROG_PULL_NOT_MODE, 0);
FlprogDiscreteOutputPin FLProgPin_PA0(PA0, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PA1(PA1, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PA2(PA2, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PA3(PA3, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PA6(PA6, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PA7(PA7, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PA8(PA8, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PA11(PA11, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PB0(PB0, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PB1(PB1, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PE5(PE5, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PE6(PE6, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PE7(PE7, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PE8(PE8, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PC2(PC2, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PA12(PA12, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PE11(PE11, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PE12(PE12, 0, 0);
FlprogDiscreteOutputPin FLProgPin_PC1(PC1, 0, 0);
int16_t Out_108382167_158375559;
int16_t Out_253334638_158375559;
bool DI_block_180_outValue;
bool _VarToBit_149_1 = 0;
bool _VarToBit_149_2 = 0;
bool _VarToBit_149_3 = 0;
bool _VarToBit_149_4 = 0;
bool _VarToBit_149_5 = 0;
bool _VarToBit_149_6 = 0;
bool _VarToBit_149_7 = 0;
bool _VarToBit_149_8 = 0;
bool _VarToBit_149_9 = 0;
bool _VarToBit_149_10 = 0;
bool _VarToBit_149_11 = 0;
bool _VarToBit_149_12 = 0;
bool _VarToBit_149_13 = 0;
bool _VarToBit_149_14 = 0;
bool _VarToBit_149_15 = 0;
bool _VarToBit_149_16 = 0;
bool DI_block_167_outValue;
bool DI_block_165_outValue;
bool DI_block_181_outValue;
uint16_t _mux205;
bool InitConsole_7_init = 0;
bool InitConsole_7_out = 0;
uint16_t _mux206;
uint8_t Out_46217284_55922712;
uint8_t Out_115940838_55922712;
uint8_t Out_46217284_81497009;
uint8_t Out_115940838_81497009;
bool DI_block_170_outValue;
bool DI_block_168_outValue;
uint8_t E_Counter_73_agoEn = 0;
RT_HW_COUNTER_ID E_Counter_73;
uint8_t Out_36333439_113718779;
bool Out_45575441_239928664;
int16_t MbVar_69511086_block_130_oldVal;
bool _tim40I = 0;
bool _tim40O = 0;
uint32_t _tim40P = 0UL;
int16_t Out_620703_212663958;
bool Out_188021688_212663958;
bool Out_222744586_212663958;
bool DI_block_169_outValue;
bool DI_block_171_outValue;
uint8_t Out_620703_132403258;
bool Out_94223944_132403258;
bool Out_251185179_132403258;
bool Out_123807481_132403258;
int16_t MbVar_34069315_block_131_oldVal;
bool Out_4830120_194900649;
uint8_t Out_133968906_194900649;
uint8_t Out_131944527_194900649;
uint8_t Out_620703_56845173;
bool Out_94223944_56845173;
bool Out_251185179_56845173;
bool Out_123807481_56845173;
int16_t MbVar_175017727_block_132_oldVal;
int16_t AI_block_137_outValue;
bool DI_block_174_outValue;
bool Out_114685876_24418774;
bool Out_82050884_24418774;
bool Out_215745335_24418774;
bool Out_187138713_24418774;
bool Out_117321672_24418774;
bool Out_208344287_24418774;
bool Out_3085716_24418774;
bool DI_block_172_outValue;
int16_t AI_block_144_outValue;
bool ConsoleBoardBlock15_enOut = 0;
int16_t MbVar_73391362_block_135_oldVal;
bool DI_block_177_outValue;
bool DI_block_175_outValue;
int16_t AI_block_145_outValue;
bool DI_block_173_outValue;
bool DI_block_42_outValue;
uint8_t Out_620703_242622828;
bool Out_94223944_242622828;
bool Out_251185179_242622828;
bool Out_123807481_242622828;
bool consoleVarBlock_22_ok = 1;
bool consoleVarBlock_22_run = 0;
uint16_t _mux199;
bool SetDataTimeWatchBlock_113_OES = 0;
uint8_t Out_620703_239206608;
bool Out_94223944_239206608;
bool Out_251185179_239206608;
bool Out_123807481_239206608;
bool consoleVarBlock_17_ok = 1;
bool consoleVarBlock_17_run = 0;
bool DI_block_178_outValue;
int16_t AI_block_146_outValue;
bool DI_block_176_outValue;
bool DI_block_43_outValue;
bool DI_block_44_outValue;
bool DI_block_45_outValue;
bool DI_block_46_outValue;
uint8_t Out_36333439_105013246;
uint16_t _mux201;
bool DI_block_179_outValue;
uint16_t _BitsToVar148 = 0;
bool DI_block_166_outValue;
RT_HW_FLProg_ADC_BUS FLProgADC;
RT_HW_FLProg_ADC_i2c_ADS1115 FLProgADS1115(1, 0x48, 400000, 100); //--ADS1115: bus,adr, speed,period;
RT_HW_FLProg_DAC_BUS FLProgDAC;
RT_HW_FLProg_DAC_pin_STM32 FLProgDAC_STM32;
RT_HW_FLProg_i2c_TCA9555_KEY_BTN5 FLProgBTN5(0, 0x25, 400000, 100); //--Пульт 5 кнопок TCA9555: bus,adr,speed,period;
RT_HW_FLProg_PWM_STM32F407V_PC1_sound FLProgSound; //--Звук через программный PWM 0-100:  частота 2700Гц, уровень(0-100)=50;
RT_HW_FLProg_PWM_STM32F407V_PA12_bright FLProgBright; //--Яркость через программный PWM 0-100: частота 1000Гц, уровень(0-100)=50;
#define RT_HW_FLProg_i2c_ADS1115_INTERFACE1 FLProgADS1115 //--Доступ к ADS1115;
#define RT_HW_FLProg_ADC_BUS_INTERFACE1 FLProgADC
#define RT_HW_FLProg_ADC_i2c_ADS1115_INTERFACE1 FLProgADS1115
#define RT_HW_FLProg_i2c_TCA9555_KEY_BTN5_INTERFACE1 FLProgBTN5 //--Доступ к пульту BTN5;
RT_HW_STRUCT_CORRECT_CLOCK correctClock_212663958; //--Correct RTC <-->Modbus;
//================================KEY_CONTROL_EDIT_NUMBER==========================================
RT_HW_STRUCT_KEY_CONTROL_EDIT_NUMBER keyControlEditNumber_132403258; //--edit.Number: int32_t;
//==================================================================================================
//================================KEY_CONTROL_EDIT_NUMBER==========================================
RT_HW_STRUCT_KEY_CONTROL_EDIT_NUMBER keyControlEditNumber_239206608; //--edit.Number: int32_t;
//==================================================================================================
//================================KEY_CONTROL_EDIT_NUMBER==========================================
RT_HW_STRUCT_KEY_CONTROL_EDIT_NUMBER keyControlEditNumber_56845173; //--edit.Number: int32_t;
//==================================================================================================
//================================KEY_CONTROL_EDIT_NUMBER==========================================
RT_HW_STRUCT_KEY_CONTROL_EDIT_NUMBER keyControlEditNumber_242622828; //--edit.Number: int32_t;
//==================================================================================================
//================================KEY CONTROL CORRECT RTC =========================================
RT_HW_STRUCT_KEY_CONTROL_CORRECT id_24418774; //--Корректировка времени с панели;
RT_HW_STRUCT_KEY_CONTROL_EDIT_INT ed_24418774; //--СТРУКТУРА EDIT.INT;
//==================================================================================================
RT_HW_STRUCT_KEY_CONTROL_SOUND keyControlSound_105013246; //--Управлениие звуком кнопок панели;
RT_HW_STRUCT_KEY_CONTROL_BRIGHTNESS keyControlBright_113718779;
uint8_t custom_113718779 = 0; //--Управление яркость панели;
RT_HW_STRUCT_KEY_CONTROL_BTN keyControl_194900649; //--Клавиатура BTN5: пять кнопок;
int16_t _tempVariable_int16_t;
uint32_t _tempVariable_uint32_t;
bool _tempVariable_bool;
uint16_t _tempVariable_uint16_t;
uint8_t _tempVariable_uint8_t;
// Web output control is RAM-only. Existing PLC arbitration resumes on disable.
static bool profileWebOutputEnabled = false;
static uint16_t profileWebDoMask = 0;
static uint16_t profileWebAo[2] = {0, 0};

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
    FLProgUart.setSpeedUart(115200, 2);
    Uart_73348587_data.speed = 115200;
    FLProgUart.setDataBitUart(8, 2);
    Uart_73348587_data.dataBit = 8;
    FLProgUart.setParityUart(0, 2);
    Uart_73348587_data.parity = 0;
    FLProgUart.setStopBitUart(1, 2);
    Uart_73348587_data.stopBit = 1;
    Uart_73348587_data.number = 2;
    FLProgUart.setSpeedUart(115200, 3);
    Uart_216360334_data.speed = 115200;
    FLProgUart.setDataBitUart(8, 3);
    Uart_216360334_data.dataBit = 8;
    FLProgUart.setParityUart(0, 3);
    Uart_216360334_data.parity = 0;
    FLProgUart.setStopBitUart(1, 3);
    Uart_216360334_data.stopBit = 1;
    Uart_216360334_data.number = 3;
    FLProgUart.setSpeedUart(115200, 5);
    Uart_156610300_data.speed = 115200;
    FLProgUart.setDataBitUart(8, 5);
    Uart_156610300_data.dataBit = 8;
    FLProgUart.setParityUart(0, 5);
    Uart_156610300_data.parity = 0;
    FLProgUart.setStopBitUart(1, 5);
    Uart_156610300_data.stopBit = 1;
    Uart_156610300_data.number = 5;
    FLProgUart.setSpeedUart(115200, 6);
    Uart_197108242_data.speed = 115200;
    FLProgUart.setDataBitUart(8, 6);
    Uart_197108242_data.dataBit = 8;
    FLProgUart.setParityUart(0, 6);
    Uart_197108242_data.parity = 0;
    FLProgUart.setStopBitUart(1, 6);
    Uart_197108242_data.stopBit = 1;
    Uart_197108242_data.number = 6;
    FLProgUart.setSpeedUart(115200, 4);
    Uart_194105114_data.speed = 115200;
    FLProgUart.setDataBitUart(8, 4);
    Uart_194105114_data.dataBit = 8;
    FLProgUart.setParityUart(0, 4);
    Uart_194105114_data.parity = 0;
    FLProgUart.setStopBitUart(1, 4);
    Uart_194105114_data.stopBit = 1;
    Uart_194105114_data.number = 4;
    FLProgUart.setSpeedUart(115200, 1);
    Uart_1830927_data.speed = 115200;
    FLProgUart.setDataBitUart(8, 1);
    Uart_1830927_data.dataBit = 8;
    FLProgUart.setParityUart(0, 1);
    Uart_1830927_data.parity = 0;
    FLProgUart.setStopBitUart(1, 1);
    Uart_1830927_data.stopBit = 1;
    Uart_1830927_data.number = 1;
    WiznetInterface_165513604.mac(0x78, 0xAC, 0xC0, 0x5C, 0x44, 0x8D);
    WiznetInterface_165513604.setSkippingEvents(0);
    WiznetInterface_165513604.resetDhcp();
    WiznetInterface_165513604.localIP(IPAddress(192, 168, 0, 191));
    WiznetInterface_165513604.dns(IPAddress(192, 168, 0, 1));
    WiznetInterface_165513604.gateway(IPAddress(192, 168, 0, 1));
    WiznetInterface_165513604.subnet(IPAddress(255, 255, 255, 0));
    Modbus_144774688.setSkippingEvents(0);
    Modbus_144774688.setSlaveAddress(10);
    Modbus_144774688.setPauseTime(50);
    Modbus_45921880.setSkippingEvents(0);
    Modbus_45921880.setSlaveAddress(10);
    Modbus_45921880.setPauseTime(50);
    Modbus_251262745.setSkippingEvents(0);
    Modbus_251262745.setSlaveAddress(10);
    Modbus_251262745.setPauseTime(50);
    Modbus_246570956.setSkippingEvents(0);
    Modbus_246570956.setSlaveAddress(10);
    Modbus_246570956.setPauseTime(50);
    Modbus_32382178.setSkippingEvents(0);
    Modbus_32382178.setSlaveAddress(10);
    Modbus_32382178.setPauseTime(50);
    Modbus_95643830.setSkippingEvents(0);
    Modbus_95643830.setSlaveAddress(10);
    Modbus_95643830.setTcpPort(502);
    Modbus_95643830.byTcp();
    Modbus_144774688.setLongOrder(1);
    Modbus_144774688.setFloatOrder(1);
    Modbus_144774688.setUnsignedlongOrder(1);
    Modbus_144774688.setIntOrder(1);
    Modbus_144774688.setDataTable(4, 50, table_4_1_A);
    Modbus_45921880.setData(Modbus_144774688.mainData());
    Modbus_251262745.setData(Modbus_144774688.mainData());
    Modbus_246570956.setData(Modbus_144774688.mainData());
    Modbus_32382178.setData(Modbus_144774688.mainData());
    Modbus_95643830.setData(Modbus_144774688.mainData());
    Modbus_83290452.setPauseTime(50);
    Modbus_83290452.setSlaveAddress(0, 20);
    Modbus_83290452.setPollingPeriod(20, 200);
    Modbus_83290452.setTimeOutTime(20, 1000);
    Modbus_83290452.setLongOrder(20, 1);
    Modbus_83290452.setFloatOrder(20, 1);
    Modbus_83290452.setUnsignedlongOrder(20, 1);
    Modbus_83290452.setIntOrder(20, 1);
    Modbus_83290452.setHrSendMode(20, FLPROG_SEND_AUTO);
    Modbus_83290452.setCoilSendMode(20, FLPROG_SEND_AUTO);
    Modbus_83290452.setDataTable(20, 4, 50, table_4_1_2_A);
    ExternalEEPROM_252608257.setByteStartValue(1, 100);
    ExternalEEPROM_252608257.setByteStartValue(2, 80);
    ExternalEEPROM_252608257.setByteStartValue(3, 50);
    ExternalEEPROM_252608257.setByteStartValue(4, 4);
    ExternalEEPROM_252608257.setSkippingEvents(0);
    ExternalEEPROM_252608257.begin();
#if defined(FLPROG_FLE4D_30MT_OTA_PROFILE) && FLPROG_FLE4D_30MT_OTA_PROFILE
#if defined(FLPROG_WIZNET_INTERFACE1)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)1, &FLPROG_WIZNET_INTERFACE1);
#endif
#if defined(FLPROG_WIZNET_INTERFACE2)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)2, &FLPROG_WIZNET_INTERFACE2);
#endif
#if defined(FLPROG_WIZNET_INTERFACE3)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)3, &FLPROG_WIZNET_INTERFACE3);
#endif
#if defined(FLPROG_WIZNET_INTERFACE4)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)4, &FLPROG_WIZNET_INTERFACE4);
#endif
#if defined(FLPROG_WIZNET_INTERFACE5)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)5, &FLPROG_WIZNET_INTERFACE5);
#endif
#if defined(FLPROG_WIZNET_INTERFACE6)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)6, &FLPROG_WIZNET_INTERFACE6);
#endif
#if defined(FLPROG_WIZNET_INTERFACE7)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)7, &FLPROG_WIZNET_INTERFACE7);
#endif
#if defined(FLPROG_WIZNET_INTERFACE8)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)8, &FLPROG_WIZNET_INTERFACE8);
#endif
#elif defined(ESP8266) || defined(ESP32)
#if defined(FLPROG_WIFI_INTERFACE1)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)1, &FLPROG_WIFI_INTERFACE1);
#endif
#if defined(FLPROG_WIFI_INTERFACE2)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)2, &FLPROG_WIFI_INTERFACE2);
#endif
#if defined(FLPROG_WIFI_INTERFACE3)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)3, &FLPROG_WIFI_INTERFACE3);
#endif
#if defined(FLPROG_WIFI_INTERFACE4)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)4, &FLPROG_WIFI_INTERFACE4);
#endif
#if defined(FLPROG_WIFI_INTERFACE5)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)5, &FLPROG_WIFI_INTERFACE5);
#endif
#if defined(FLPROG_WIFI_INTERFACE6)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)6, &FLPROG_WIFI_INTERFACE6);
#endif
#if defined(FLPROG_WIFI_INTERFACE7)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)7, &FLPROG_WIFI_INTERFACE7);
#endif
#if defined(FLPROG_WIFI_INTERFACE8)
    flprogNetworkDevices.registerDevice((FLProgNetworkDeviceId)8, &FLPROG_WIFI_INTERFACE8);
#endif
#endif
    RT_HW_Base.shed.sysQuick.qnt = 101;
    //--------------------------------------------------------------------------------------------------
    //                                  ADC BUS
    //--------------------------------------------------------------------------------------------------
    FLProgADC.setQnt(4);
    if (!FLProgADC.AD[0].custom)
    {
        FLProgADC.setCorrect(0, 10000);
        FLProgADC.AD[0].custom = 1;
    } //--AD.0
    if (!FLProgADC.AD[1].custom)
    {
        FLProgADC.setCorrect(1, 10000);
        FLProgADC.AD[1].custom = 1;
    } //--AD.1
    if (!FLProgADC.AD[2].custom)
    {
        FLProgADC.setCorrect(2, 10000);
        FLProgADC.AD[2].custom = 1;
    } //--AD.2
    if (!FLProgADC.AD[3].custom)
    {
        FLProgADC.setCorrect(3, 10000);
        FLProgADC.AD[3].custom = 1;
    } //--AD.3
    //--------------------------------------------------------------------------------------------------
    //                                  ADS1115
    //--------------------------------------------------------------------------------------------------
    if (!FLProgADS1115.custom)
    {
        FLProgADS1115.setStartAD(0); //--AIN0...AIN3 подключаются к AD[0]...AD[3];
        FLProgADS1115.setPGA(RT_HW_FLProg_ADC_i2c_ADS1115_PGA_2048); //--Диапазон ADS1115 ±2.048 В;
        FLProgADS1115.setSPS(RT_HW_FLProg_ADC_i2c_ADS1115_SPS_128); //--Скорость преобразования 128 SPS;
        FLProgADS1115.setDividerAD(5200); //--Коэффициент входного делителя: 5.200;
        FLProgADS1115.setRangeMV(10000); //--Номинальный диапазон входа: 0...10000 мВ;
        FLProgADS1115.setRetry(100, 2000); //--Динамическая пауза после ошибки: 100...2000 мс;
        FLProgADS1115.custom = 1;
    }
    //--------------------------------------------------------------------------------------------------
    //							STM32 DAC PA4,PA5
    //--------------------------------------------------------------------------------------------------
    FLProgDAC.setQnt(2);
    //--------------------------------------------------------------------------------------------------
    if (!FLProgDAC.DA[0].custom)
    {
        FLProgDAC.DA[0].setSource(RT_HW_FLProg_DAC_SOURCE_AUTO);
        FLProgDAC.DA[0].setSafeSystem(0);
        FLProgDAC.DA[0].setPermit(1);
        FLProgDAC.setCorrect(0, 10000);
        FLProgDAC.DA[0].custom = 1;
    }
    //--------------------------------------------------------------------------------------------------
    if (!FLProgDAC.DA[1].custom)
    {
        FLProgDAC.DA[1].setSource(RT_HW_FLProg_DAC_SOURCE_AUTO);
        FLProgDAC.DA[1].setSafeSystem(0);
        FLProgDAC.DA[1].setPermit(1);
        FLProgDAC.setCorrect(1, 10000);
        FLProgDAC.DA[1].custom = 1;
    }
    //--------------------------------------------------------------------------------------------------
    if (!FLProgDAC_STM32.custom)
    {
        FLProgDAC_STM32.setPA4(0); //--PA4 получает DA[0];
        FLProgDAC_STM32.setPA5(1); //--PA5 получает DA[1];
        FLProgDAC_STM32.custom = 1;
    }
    //--------------------------------------------------------------------------------------------------
    FLPROG_WEBUI_BEGIN_SELECTED();
    //========================================================================================================================================
    //++++ Начало настройки дисплея TFT ST7735 RGB (SPI1) ++++
    //========================================================================================================================================
    oled_138862728_chip.setMode(0);
    oled_138862728_chip.setWidth(128);
    oled_138862728_chip.setHeight(160);
    oled_138862728_chip.setPeriodLimit(50);
    oled_138862728_chip.setRotation(RT_HW_OLED_TYPE_ROTATE_90);
    oled_138862728_chip.setContrast(100);
    oled_138862728_chip.sendSizePacket(0);
    oled_138862728_chip.setPinCs(PE14);
    oled_138862728_chip.setPinRs(PE13);
    oled_138862728_chip.setPinRst(PE15);
    oled_138862728_chip.setDmaMode(true);
    oled_138862728_chip.setBus(1);
    oled_138862728_chip.setSpeed(20000000);
    //#### Экран Экран 1 - 1.ГЛАВНЫЙ
    oled_138862728.setScreen(0, &oled_scr_48392945);
    //------  Виджет Текст
    oled_scr_48392945.setWidget(0, &oled_fld_txt_54726843);
    //------  Виджет Текст
    oled_scr_48392945.setWidget(1, &oled_fld_txt_46985861);
    //------  Виджет Цифровое значение - Быстродействие
    oled_scr_48392945.setWidget(2, &oled_fld_nv_196997419);
    oled_fld_nv_196997419.setLength(6);
    oled_fld_nv_196997419.setPrefix("s=");
    oled_fld_nv_196997419.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_196997419.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_196997419.setVarType(FLPROG_OLED_NUNBER_UINT32_TYPE);
    //------  Виджет Цифровое значение - Часы
    oled_scr_48392945.setWidget(3, &oled_fld_nv_25335513);
    oled_fld_nv_25335513.setLength(2);
    oled_fld_nv_25335513.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_25335513.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_25335513.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Минуты
    oled_scr_48392945.setWidget(4, &oled_fld_nv_134819151);
    oled_fld_nv_134819151.setLength(2);
    oled_fld_nv_134819151.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_134819151.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_134819151.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Секунды
    oled_scr_48392945.setWidget(5, &oled_fld_nv_36732314);
    oled_fld_nv_36732314.setLength(2);
    oled_fld_nv_36732314.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_36732314.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_36732314.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Текст
    oled_scr_48392945.setWidget(6, &oled_fld_txt_213810209);
    //------  Виджет Текст
    oled_scr_48392945.setWidget(7, &oled_fld_txt_150445619);
    //------  Виджет Цифровое значение - Год.xx
    oled_scr_48392945.setWidget(8, &oled_fld_nv_34185301);
    oled_fld_nv_34185301.setLength(2);
    oled_fld_nv_34185301.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_34185301.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_34185301.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Месяц
    oled_scr_48392945.setWidget(9, &oled_fld_nv_156182767);
    oled_fld_nv_156182767.setLength(2);
    oled_fld_nv_156182767.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_156182767.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_156182767.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - День
    oled_scr_48392945.setWidget(10, &oled_fld_nv_67445460);
    oled_fld_nv_67445460.setLength(2);
    oled_fld_nv_67445460.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_67445460.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_67445460.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Текст
    oled_scr_48392945.setWidget(11, &oled_fld_txt_69983135);
    //------  Виджет Цифровое значение - Время работы в секундах
    oled_scr_48392945.setWidget(12, &oled_fld_nv_164605960);
    oled_fld_nv_164605960.setLength(6);
    oled_fld_nv_164605960.setPrefix("t=");
    oled_fld_nv_164605960.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_164605960.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_164605960.setVarType(FLPROG_OLED_NUNBER_UINT32_TYPE);
    //------  Виджет Список строк
    oled_scr_48392945.setWidget(13, &oled_fld_nvl_171661469);
    oled_fld_nvl_171661469.setLength(9);
    oled_fld_nvl_171661469.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nvl_171661469.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nvl_171661469.setDefaultText("Default");
    oled_fld_nvl_171661469.setTextItem(0, 0, "OFF");
    oled_fld_nvl_171661469.setTextItem(1, 1, "Проект");
    oled_fld_nvl_171661469.setTextItem(2, 2, "Modbus");
    oled_fld_nvl_171661469.setTextItem(3, 3, "Test");
    oled_fld_nvl_171661469.setTextItem(4, 4, "Настройка");
    //------  Виджет Битовое значение
    oled_scr_48392945.setWidget(14, &oled_fld_bv_138544549);
    oled_fld_bv_138544549.setLength(1);
    oled_fld_bv_138544549.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_bv_138544549.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_bv_138544549.setTrueString("*");
    oled_fld_bv_138544549.setFalseString(" ");
    //------  Виджет Строковое значение
    oled_scr_48392945.setWidget(15, &oled_fld_sv_56713862);
    oled_fld_sv_56713862.setLength(15);
    oled_fld_sv_56713862.setPrefix("IP:  ");
    oled_fld_sv_56713862.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_sv_56713862.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    //------  Виджет Строковое значение - eth.mask
    oled_scr_48392945.setWidget(16, &oled_fld_sv_253709455);
    oled_fld_sv_253709455.setLength(15);
    oled_fld_sv_253709455.setPrefix("mask:");
    oled_fld_sv_253709455.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_sv_253709455.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    //------  Виджет Строковое значение - eth.gate
    oled_scr_48392945.setWidget(17, &oled_fld_sv_64681359);
    oled_fld_sv_64681359.setLength(15);
    oled_fld_sv_64681359.setPrefix("gate:");
    oled_fld_sv_64681359.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_sv_64681359.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    //------  Виджет Строковое значение - eth.ds
    oled_scr_48392945.setWidget(18, &oled_fld_sv_226067155);
    oled_fld_sv_226067155.setLength(15);
    oled_fld_sv_226067155.setPrefix("dns: ");
    oled_fld_sv_226067155.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_sv_226067155.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    //------  Виджет Битовое значение - eth.ready
    oled_scr_48392945.setWidget(19, &oled_fld_bv_59587394);
    oled_fld_bv_59587394.setLength(1);
    oled_fld_bv_59587394.setPrefix("rd=");
    oled_fld_bv_59587394.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_bv_59587394.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_bv_59587394.setTrueString("+");
    oled_fld_bv_59587394.setFalseString("-");
    //------  Виджет Цифровое значение - eth.status
    oled_scr_48392945.setWidget(20, &oled_fld_nv_166583876);
    oled_fld_nv_166583876.setLength(3);
    oled_fld_nv_166583876.setPrefix("status=");
    oled_fld_nv_166583876.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_166583876.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_166583876.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - eth.err
    oled_scr_48392945.setWidget(21, &oled_fld_nv_117332420);
    oled_fld_nv_117332420.setLength(3);
    oled_fld_nv_117332420.setPrefix("err=");
    oled_fld_nv_117332420.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_117332420.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_117332420.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //#### Экран Экран 2 - 2.ДЕМО
    oled_138862728.setScreen(1, &oled_scr_200663618);
    //------  Виджет Прямоугольник - Рамка
    oled_scr_200663618.setWidget(0, &oled_fld_rect_43854780);
    //------  Виджет Цифровое значение - Быстродействие
    oled_scr_200663618.setWidget(1, &oled_fld_nv_26807825);
    oled_fld_nv_26807825.setLength(6);
    oled_fld_nv_26807825.setPrefix("s=");
    oled_fld_nv_26807825.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_26807825.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_26807825.setVarType(FLPROG_OLED_NUNBER_UINT32_TYPE);
    //------  Виджет Текст
    oled_scr_200663618.setWidget(2, &oled_fld_txt_46475982);
    //------  Виджет Текст
    oled_scr_200663618.setWidget(3, &oled_fld_txt_37186508);
    //------  Виджет Цифровое значение - День
    oled_scr_200663618.setWidget(4, &oled_fld_nv_108347373);
    oled_fld_nv_108347373.setLength(2);
    oled_fld_nv_108347373.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_108347373.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_108347373.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Месяц
    oled_scr_200663618.setWidget(5, &oled_fld_nv_61032334);
    oled_fld_nv_61032334.setLength(2);
    oled_fld_nv_61032334.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_61032334.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_61032334.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Год.xx
    oled_scr_200663618.setWidget(6, &oled_fld_nv_41069956);
    oled_fld_nv_41069956.setLength(2);
    oled_fld_nv_41069956.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_41069956.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_41069956.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Текст
    oled_scr_200663618.setWidget(7, &oled_fld_txt_30079150);
    //------  Виджет Текст
    oled_scr_200663618.setWidget(8, &oled_fld_txt_16243548);
    //------  Виджет Цифровое значение - Секунды
    oled_scr_200663618.setWidget(9, &oled_fld_nv_32528453);
    oled_fld_nv_32528453.setLength(2);
    oled_fld_nv_32528453.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_32528453.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_32528453.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Минуты
    oled_scr_200663618.setWidget(10, &oled_fld_nv_175148948);
    oled_fld_nv_175148948.setLength(2);
    oled_fld_nv_175148948.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_175148948.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_175148948.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Часы
    oled_scr_200663618.setWidget(11, &oled_fld_nv_198685733);
    oled_fld_nv_198685733.setLength(2);
    oled_fld_nv_198685733.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_198685733.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_198685733.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Текст
    oled_scr_200663618.setWidget(12, &oled_fld_txt_93658359);
    //#### Экран Экран 3 - 3.ВХОДЫ
    oled_138862728.setScreen(2, &oled_scr_120866812);
    //------  Виджет Цифровое значение - DIN.2
    oled_scr_120866812.setWidget(0, &oled_fld_nv_58867727);
    oled_fld_nv_58867727.setLength(16);
    oled_fld_nv_58867727.setPrefix("DIN2: ");
    oled_fld_nv_58867727.setMode(FLPROG_OLED_MSB_BIN_VALUE_MODE);
    oled_fld_nv_58867727.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_58867727.setTrueChar('+');
    oled_fld_nv_58867727.setFalseChar('-');
    oled_fld_nv_58867727.setVarType(FLPROG_OLED_NUNBER_UINT16_TYPE);
    //------  Виджет Цифровое значение - DIN.1
    oled_scr_120866812.setWidget(1, &oled_fld_nv_31350185);
    oled_fld_nv_31350185.setLength(16);
    oled_fld_nv_31350185.setPrefix("DIN1: ");
    oled_fld_nv_31350185.setMode(FLPROG_OLED_MSB_BIN_VALUE_MODE);
    oled_fld_nv_31350185.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_31350185.setTrueChar('+');
    oled_fld_nv_31350185.setFalseChar('-');
    oled_fld_nv_31350185.setVarType(FLPROG_OLED_NUNBER_UINT16_TYPE);
    //------  Виджет Битовое значение - XVcc
    oled_scr_120866812.setWidget(2, &oled_fld_bv_183590754);
    oled_fld_bv_183590754.setLength(1);
    oled_fld_bv_183590754.setPrefix("XVcc=");
    oled_fld_bv_183590754.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_bv_183590754.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_bv_183590754.setTrueString("+");
    oled_fld_bv_183590754.setFalseString("-");
    //------  Виджет Цифровое значение - AD.3
    oled_scr_120866812.setWidget(3, &oled_fld_nv_115923925);
    oled_fld_nv_115923925.setLength(4);
    oled_fld_nv_115923925.setPrefix("AD.3=");
    oled_fld_nv_115923925.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_115923925.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_115923925.setVarType(FLPROG_OLED_NUNBER_UINT16_TYPE);
    //------  Виджет Цифровое значение - AD.2
    oled_scr_120866812.setWidget(4, &oled_fld_nv_16086042);
    oled_fld_nv_16086042.setLength(4);
    oled_fld_nv_16086042.setPrefix("AD.2=");
    oled_fld_nv_16086042.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_16086042.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_16086042.setVarType(FLPROG_OLED_NUNBER_UINT16_TYPE);
    //------  Виджет Цифровое значение - AD.1
    oled_scr_120866812.setWidget(5, &oled_fld_nv_191669495);
    oled_fld_nv_191669495.setLength(4);
    oled_fld_nv_191669495.setPrefix("AD.1=");
    oled_fld_nv_191669495.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_191669495.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_191669495.setVarType(FLPROG_OLED_NUNBER_UINT16_TYPE);
    //------  Виджет Цифровое значение - AD.0
    oled_scr_120866812.setWidget(6, &oled_fld_nv_105742732);
    oled_fld_nv_105742732.setLength(4);
    oled_fld_nv_105742732.setPrefix("AD.0=");
    oled_fld_nv_105742732.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_105742732.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_105742732.setVarType(FLPROG_OLED_NUNBER_UINT16_TYPE);
    //------  Виджет Цифровое значение - Быстродействие
    oled_scr_120866812.setWidget(7, &oled_fld_nv_97585484);
    oled_fld_nv_97585484.setLength(6);
    oled_fld_nv_97585484.setPrefix("s=");
    oled_fld_nv_97585484.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_97585484.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_97585484.setVarType(FLPROG_OLED_NUNBER_UINT32_TYPE);
    //------  Виджет Текст  - Заголовок
    oled_scr_120866812.setWidget(8, &oled_fld_txt_239059671);
    //------  Виджет Цифровое значение - AD3.mV
    oled_scr_120866812.setWidget(9, &oled_fld_nv_256356637);
    oled_fld_nv_256356637.setLength(5);
    oled_fld_nv_256356637.setSuffix(" mV");
    oled_fld_nv_256356637.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_256356637.setAlign(FLPROG_OLED_RIGHT_ALIGN_VALUE_MODE);
    oled_fld_nv_256356637.setVarType(FLPROG_OLED_NUNBER_INT16_TYPE);
    //------  Виджет Цифровое значение - AD1.mV
    oled_scr_120866812.setWidget(10, &oled_fld_nv_121085400);
    oled_fld_nv_121085400.setLength(5);
    oled_fld_nv_121085400.setSuffix(" mV");
    oled_fld_nv_121085400.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_121085400.setAlign(FLPROG_OLED_RIGHT_ALIGN_VALUE_MODE);
    oled_fld_nv_121085400.setVarType(FLPROG_OLED_NUNBER_INT16_TYPE);
    //------  Виджет Цифровое значение - AD2.mV
    oled_scr_120866812.setWidget(11, &oled_fld_nv_113347223);
    oled_fld_nv_113347223.setLength(5);
    oled_fld_nv_113347223.setSuffix(" mV");
    oled_fld_nv_113347223.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_113347223.setAlign(FLPROG_OLED_RIGHT_ALIGN_VALUE_MODE);
    oled_fld_nv_113347223.setVarType(FLPROG_OLED_NUNBER_INT16_TYPE);
    //------  Виджет Цифровое значение - AD0.mV
    oled_scr_120866812.setWidget(12, &oled_fld_nv_248199219);
    oled_fld_nv_248199219.setLength(5);
    oled_fld_nv_248199219.setSuffix(" mV");
    oled_fld_nv_248199219.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_248199219.setAlign(FLPROG_OLED_RIGHT_ALIGN_VALUE_MODE);
    oled_fld_nv_248199219.setVarType(FLPROG_OLED_NUNBER_INT16_TYPE);
    //------  Виджет Цифровое значение
    oled_scr_120866812.setWidget(13, &oled_fld_nv_196593743);
    oled_fld_nv_196593743.setLength(4);
    oled_fld_nv_196593743.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_196593743.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_196593743.setVarType(FLPROG_OLED_NUNBER_INT16_TYPE);
    //------  Виджет Текст
    oled_scr_120866812.setWidget(14, &oled_fld_txt_258438336);
    //------  Виджет Текст
    oled_scr_120866812.setWidget(15, &oled_fld_txt_41839462);
    //------  Виджет Цифровое значение
    oled_scr_120866812.setWidget(16, &oled_fld_nv_245400241);
    oled_fld_nv_245400241.setLength(4);
    oled_fld_nv_245400241.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_245400241.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_245400241.setVarType(FLPROG_OLED_NUNBER_INT16_TYPE);
    //------  Виджет Цифровое значение
    oled_scr_120866812.setWidget(17, &oled_fld_nv_125727405);
    oled_fld_nv_125727405.setLength(4);
    oled_fld_nv_125727405.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_125727405.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_125727405.setVarType(FLPROG_OLED_NUNBER_INT16_TYPE);
    //------  Виджет Цифровое значение
    oled_scr_120866812.setWidget(18, &oled_fld_nv_140658593);
    oled_fld_nv_140658593.setLength(4);
    oled_fld_nv_140658593.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_140658593.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_140658593.setVarType(FLPROG_OLED_NUNBER_INT16_TYPE);
    //------  Виджет Текст
    oled_scr_120866812.setWidget(19, &oled_fld_txt_132134098);
    //#### Экран Экран 4 - 4.ВЫХОДЫ
    oled_138862728.setScreen(3, &oled_scr_29161469);
    //------  Виджет Текст  - Заголовок
    oled_scr_29161469.setWidget(0, &oled_fld_txt_30747158);
    //------  Виджет Прямоугольник - Рамка экрана
    oled_scr_29161469.setWidget(1, &oled_fld_rect_203196789);
    //------  Виджет Цифровое значение
    oled_scr_29161469.setWidget(2, &oled_fld_nv_58823822);
    oled_fld_nv_58823822.setLength(6);
    oled_fld_nv_58823822.setPrefix("s=");
    oled_fld_nv_58823822.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_58823822.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_58823822.setVarType(FLPROG_OLED_NUNBER_UINT32_TYPE);
    //------  Виджет Цифровое значение
    oled_scr_29161469.setWidget(3, &oled_fld_nv_37782062);
    oled_fld_nv_37782062.setLength(16);
    oled_fld_nv_37782062.setPrefix("DOT1: ");
    oled_fld_nv_37782062.setMode(FLPROG_OLED_MSB_BIN_VALUE_MODE);
    oled_fld_nv_37782062.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_37782062.setTrueChar('+');
    oled_fld_nv_37782062.setFalseChar('-');
    oled_fld_nv_37782062.setVarType(FLPROG_OLED_NUNBER_UINT16_TYPE);
    //------  Виджет Цифровое значение
    oled_scr_29161469.setWidget(4, &oled_fld_nv_161568141);
    oled_fld_nv_161568141.setLength(16);
    oled_fld_nv_161568141.setPrefix("DOT2: ");
    oled_fld_nv_161568141.setMode(FLPROG_OLED_MSB_BIN_VALUE_MODE);
    oled_fld_nv_161568141.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_161568141.setTrueChar('+');
    oled_fld_nv_161568141.setFalseChar('-');
    oled_fld_nv_161568141.setVarType(FLPROG_OLED_NUNBER_UINT16_TYPE);
    //------  Виджет Линейный индикатор
    oled_scr_29161469.setWidget(5, &oled_fld_gaude_215774609);
    oled_fld_gaude_215774609.setLevelColor(RT_HW_OLED_FILL_PURPLE);
    oled_fld_gaude_215774609.setDirection(FLPROG_OLED_GAUDE_LEFT_RIGHT_DIRECTION);
    oled_fld_gaude_215774609.setMaxValue(4095);
    oled_fld_gaude_215774609.setMinValue(0);
    //------  Виджет Цифровое значение
    oled_scr_29161469.setWidget(6, &oled_fld_nv_185289915);
    oled_fld_nv_185289915.setLength(4);
    oled_fld_nv_185289915.setPrefix("DA0=");
    oled_fld_nv_185289915.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_185289915.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_185289915.setVarType(FLPROG_OLED_NUNBER_UINT16_TYPE);
    //------  Виджет Линейный индикатор
    oled_scr_29161469.setWidget(7, &oled_fld_gaude_107943078);
    oled_fld_gaude_107943078.setLevelColor(RT_HW_OLED_FILL_ORANGE);
    oled_fld_gaude_107943078.setDirection(FLPROG_OLED_GAUDE_LEFT_RIGHT_DIRECTION);
    oled_fld_gaude_107943078.setMaxValue(4095);
    oled_fld_gaude_107943078.setMinValue(0);
    //------  Виджет Цифровое значение
    oled_scr_29161469.setWidget(8, &oled_fld_nv_245388940);
    oled_fld_nv_245388940.setLength(4);
    oled_fld_nv_245388940.setPrefix("DA1=");
    oled_fld_nv_245388940.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_245388940.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_245388940.setVarType(FLPROG_OLED_NUNBER_UINT16_TYPE);
    //#### Экран Экран 5 - 5.НАСТРОЙКА ПРОЕКТА
    oled_138862728.setScreen(4, &oled_scr_73848182);
    //------  Виджет Прямоугольник - Рамка
    oled_scr_73848182.setWidget(0, &oled_fld_rect_168959227);
    //------  Виджет Прямоугольник
    oled_scr_73848182.setWidget(1, &oled_fld_rect_28526112);
    //------  Виджет Текст  - Заголовок
    oled_scr_73848182.setWidget(2, &oled_fld_txt_248331703);
    //------  Виджет Цифровое значение
    oled_scr_73848182.setWidget(3, &oled_fld_nv_196179951);
    oled_fld_nv_196179951.setLength(6);
    oled_fld_nv_196179951.setPrefix("s=");
    oled_fld_nv_196179951.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_196179951.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_196179951.setVarType(FLPROG_OLED_NUNBER_UINT32_TYPE);
    //------  Виджет Список строк
    oled_scr_73848182.setWidget(4, &oled_fld_nvl_126836762);
    oled_fld_nvl_126836762.setLength(11);
    oled_fld_nvl_126836762.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nvl_126836762.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nvl_126836762.setDefaultText("Default");
    oled_fld_nvl_126836762.setTextItem(0, 0, "0.OFF");
    oled_fld_nvl_126836762.setTextItem(1, 1, "1.Проект");
    oled_fld_nvl_126836762.setTextItem(2, 2, "2.Modbus");
    oled_fld_nvl_126836762.setTextItem(3, 3, "3.Test");
    oled_fld_nvl_126836762.setTextItem(4, 4, "4.Настройка");
    //------  Виджет Цифровое значение
    oled_scr_73848182.setWidget(5, &oled_fld_nv_37048924);
    oled_fld_nv_37048924.setLength(2);
    oled_fld_nv_37048924.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_37048924.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_37048924.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Битовое значение
    oled_scr_73848182.setWidget(6, &oled_fld_bv_206232748);
    oled_fld_bv_206232748.setLength(1);
    oled_fld_bv_206232748.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_bv_206232748.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_bv_206232748.setTrueString("+");
    oled_fld_bv_206232748.setFalseString("-");
    //------  Виджет Битовое значение
    oled_scr_73848182.setWidget(7, &oled_fld_bv_5505156);
    oled_fld_bv_5505156.setLength(1);
    oled_fld_bv_5505156.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_bv_5505156.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_bv_5505156.setTrueString("+");
    oled_fld_bv_5505156.setFalseString("-");
    //#### Экран Экран 6 - 6.НАСТРОЙКА ПАНЕЛИ
    oled_138862728.setScreen(5, &oled_scr_127594733);
    //------  Виджет Прямоугольник - Рамка контур
    oled_scr_127594733.setWidget(0, &oled_fld_rect_110646806);
    //------  Виджет Прямоугольник - Рамка TimeSound
    oled_scr_127594733.setWidget(1, &oled_fld_rect_207741416);
    //------  Виджет Прямоугольник - Рамка Sound
    oled_scr_127594733.setWidget(2, &oled_fld_rect_114909367);
    //------  Виджет Прямоугольник - Рамка времени
    oled_scr_127594733.setWidget(3, &oled_fld_rect_135629005);
    //------  Виджет Прямоугольник - Рамка BrightLevel
    oled_scr_127594733.setWidget(4, &oled_fld_rect_118135175);
    //------  Виджет Текст  - Заголовок 6
    oled_scr_127594733.setWidget(5, &oled_fld_txt_96687945);
    //------  Виджет Текст
    oled_scr_127594733.setWidget(6, &oled_fld_txt_192733939);
    //------  Виджет Цифровое значение - День
    oled_scr_127594733.setWidget(7, &oled_fld_nv_94987733);
    oled_fld_nv_94987733.setLength(2);
    oled_fld_nv_94987733.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_94987733.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_94987733.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Месяц
    oled_scr_127594733.setWidget(8, &oled_fld_nv_90867036);
    oled_fld_nv_90867036.setLength(2);
    oled_fld_nv_90867036.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_90867036.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_90867036.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Год.xx
    oled_scr_127594733.setWidget(9, &oled_fld_nv_196225129);
    oled_fld_nv_196225129.setLength(2);
    oled_fld_nv_196225129.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_196225129.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_196225129.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Текст
    oled_scr_127594733.setWidget(10, &oled_fld_txt_134527829);
    //------  Виджет Текст
    oled_scr_127594733.setWidget(11, &oled_fld_txt_39400095);
    //------  Виджет Цифровое значение - Секунды
    oled_scr_127594733.setWidget(12, &oled_fld_nv_67458057);
    oled_fld_nv_67458057.setLength(2);
    oled_fld_nv_67458057.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_67458057.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_67458057.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Минуты
    oled_scr_127594733.setWidget(13, &oled_fld_nv_119285938);
    oled_fld_nv_119285938.setLength(2);
    oled_fld_nv_119285938.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_119285938.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_119285938.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Часы
    oled_scr_127594733.setWidget(14, &oled_fld_nv_111504103);
    oled_fld_nv_111504103.setLength(2);
    oled_fld_nv_111504103.setMode(FLPROG_OLED_TIME_LEADING_ZERO_VALUE_MODE);
    oled_fld_nv_111504103.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_111504103.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Текст
    oled_scr_127594733.setWidget(15, &oled_fld_txt_39904101);
    //------  Виджет Цифровое значение - Значение BrigthLevel
    oled_scr_127594733.setWidget(16, &oled_fld_nv_222539793);
    oled_fld_nv_222539793.setLength(3);
    oled_fld_nv_222539793.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_222539793.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_222539793.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Значение SoundLevel
    oled_scr_127594733.setWidget(17, &oled_fld_nv_62290336);
    oled_fld_nv_62290336.setLength(3);
    oled_fld_nv_62290336.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_62290336.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_62290336.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Значение SoundTime
    oled_scr_127594733.setWidget(18, &oled_fld_nv_197292450);
    oled_fld_nv_197292450.setLength(4);
    oled_fld_nv_197292450.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_197292450.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_197292450.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Номер поля
    oled_scr_127594733.setWidget(19, &oled_fld_nv_50179035);
    oled_fld_nv_50179035.setLength(2);
    oled_fld_nv_50179035.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_50179035.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_50179035.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Текст
    oled_scr_127594733.setWidget(20, &oled_fld_txt_53392629);
    //------  Виджет Текст
    oled_scr_127594733.setWidget(21, &oled_fld_txt_221838477);
    //------  Виджет Текст  - Время звука
    oled_scr_127594733.setWidget(22, &oled_fld_txt_200832565);
    //------  Виджет Цифровое значение
    oled_scr_127594733.setWidget(23, &oled_fld_nv_125668277);
    oled_fld_nv_125668277.setLength(6);
    oled_fld_nv_125668277.setPrefix("s=");
    oled_fld_nv_125668277.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_125668277.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_125668277.setVarType(FLPROG_OLED_NUNBER_UINT32_TYPE);
    //#### Экран Экран 7 - 0.ЗАСТАВКА
    oled_138862728.setScreen(6, &oled_scr_83073005);
    //------  Виджет Текст  - FLProg
    oled_scr_83073005.setWidget(0, &oled_fld_txt_43319858);
    //------  Виджет Иконка - Иконка - сигнал связи
    oled_scr_83073005.setWidget(1, &oled_fld_icon_145371210);
    //------  Виджет Текст  - Программируй реальность!
    oled_scr_83073005.setWidget(2, &oled_fld_txt_39059323);
    //------  Виджет Текст  - Иначе реальность
    oled_scr_83073005.setWidget(3, &oled_fld_txt_212539800);
    //------  Виджет Битовое значение - Звездочка
    oled_scr_83073005.setWidget(4, &oled_fld_bv_193114660);
    oled_fld_bv_193114660.setLength(1);
    oled_fld_bv_193114660.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_bv_193114660.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_bv_193114660.setTrueString("*");
    oled_fld_bv_193114660.setFalseString(" ");
    //------  Виджет Текст  -  запрограммирует тебя.
    oled_scr_83073005.setWidget(5, &oled_fld_txt_245507075);
    //------  Виджет Текст  - EIS
    oled_scr_83073005.setWidget(6, &oled_fld_txt_114202373);
    //------  Виджет Текст  - Планете Земля
    oled_scr_83073005.setWidget(7, &oled_fld_txt_216188546);
    //------  Виджет Текст  - чистую воду!
    oled_scr_83073005.setWidget(8, &oled_fld_txt_233296239);
    oled_138862728_chip.secondDebugCallback(oled_138862728_firstDebug);
    oled_138862728_chip.secondDebugCallback(oled_138862728_secondDebug);
    //========================================================================================================================================
    //++++ Конец настройки дисплея TFT ST7735 RGB (SPI1) ++++
    //========================================================================================================================================
    //========================================================================================================================================
    //++++ Начало настройки дисплея OLED SH1107 MONO (I2C0) ++++
    //========================================================================================================================================
    oled_156902651_chip.setMode(0);
    oled_156902651_chip.setWidth(128);
    oled_156902651_chip.setHeight(128);
    oled_156902651_chip.setPeriodLimit(50);
    oled_156902651_chip.setRotation(RT_HW_OLED_TYPE_ROTATE_0);
    oled_156902651_chip.setContrast(100);
    oled_156902651_chip.sendSizePacket(0);
    oled_156902651_chip.setBus(0);
    oled_156902651_chip.setAdress(0x3C);
    oled_156902651_chip.setSpeed(400000);
    //#### Экран Экран 1 - key.blink
    oled_156902651.setScreen(0, &oled_scr_263585980);
    //------  Виджет Цифровое значение
    oled_scr_263585980.setWidget(0, &oled_fld_nv_123085538);
    oled_fld_nv_123085538.setLength(2);
    oled_fld_nv_123085538.setPrefix("scr=");
    oled_fld_nv_123085538.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_123085538.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_123085538.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение
    oled_scr_263585980.setWidget(1, &oled_fld_nv_198500841);
    oled_fld_nv_198500841.setLength(2);
    oled_fld_nv_198500841.setPrefix("f6=");
    oled_fld_nv_198500841.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_198500841.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_198500841.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение - Быстродействие
    oled_scr_263585980.setWidget(2, &oled_fld_nv_66101037);
    oled_fld_nv_66101037.setLength(6);
    oled_fld_nv_66101037.setPrefix("s=");
    oled_fld_nv_66101037.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_66101037.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_66101037.setVarType(FLPROG_OLED_NUNBER_UINT32_TYPE);
    //------  Виджет Цифровое значение - Время работы
    oled_scr_263585980.setWidget(3, &oled_fld_nv_80992857);
    oled_fld_nv_80992857.setLength(5);
    oled_fld_nv_80992857.setPrefix("t=");
    oled_fld_nv_80992857.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_80992857.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_80992857.setVarType(FLPROG_OLED_NUNBER_UINT32_TYPE);
    //------  Виджет Битовое значение - Blink 500
    oled_scr_263585980.setWidget(4, &oled_fld_bv_183396639);
    oled_fld_bv_183396639.setLength(1);
    oled_fld_bv_183396639.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_bv_183396639.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_bv_183396639.setTrueString("*");
    oled_fld_bv_183396639.setFalseString(" ");
    //------  Виджет Цифровое значение
    oled_scr_263585980.setWidget(5, &oled_fld_nv_63387461);
    oled_fld_nv_63387461.setLength(3);
    oled_fld_nv_63387461.setPrefix("soundLevel=");
    oled_fld_nv_63387461.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_63387461.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_63387461.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение
    oled_scr_263585980.setWidget(6, &oled_fld_nv_151802975);
    oled_fld_nv_151802975.setLength(3);
    oled_fld_nv_151802975.setPrefix("brigthLevel=");
    oled_fld_nv_151802975.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_151802975.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_151802975.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение
    oled_scr_263585980.setWidget(7, &oled_fld_nv_212028031);
    oled_fld_nv_212028031.setLength(3);
    oled_fld_nv_212028031.setPrefix("soundTime=");
    oled_fld_nv_212028031.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_212028031.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_212028031.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение
    oled_scr_263585980.setWidget(8, &oled_fld_nv_168504598);
    oled_fld_nv_168504598.setLength(2);
    oled_fld_nv_168504598.setPrefix("f5=");
    oled_fld_nv_168504598.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_168504598.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_168504598.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Цифровое значение
    oled_scr_263585980.setWidget(9, &oled_fld_nv_178356505);
    oled_fld_nv_178356505.setLength(3);
    oled_fld_nv_178356505.setPrefix("prj=");
    oled_fld_nv_178356505.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_178356505.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_178356505.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Список строк
    oled_scr_263585980.setWidget(10, &oled_fld_nvl_133196007);
    oled_fld_nvl_133196007.setLength(8);
    oled_fld_nvl_133196007.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nvl_133196007.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nvl_133196007.setDefaultText("Default");
    oled_fld_nvl_133196007.setTextItem(0, 0, "0.OFF");
    oled_fld_nvl_133196007.setTextItem(1, 1, "1.Проект");
    oled_fld_nvl_133196007.setTextItem(2, 2, "2.Modbus");
    oled_fld_nvl_133196007.setTextItem(3, 3, "3.Test");
    //------  Виджет Цифровое значение
    oled_scr_263585980.setWidget(11, &oled_fld_nv_218060352);
    oled_fld_nv_218060352.setLength(3);
    oled_fld_nv_218060352.setPrefix("br=");
    oled_fld_nv_218060352.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_218060352.setAlign(FLPROG_OLED_LEFT_ALIGN_VALUE_MODE);
    oled_fld_nv_218060352.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    //------  Виджет Битовое значение
    oled_scr_263585980.setWidget(12, &oled_fld_bv_264786981);
    oled_fld_bv_264786981.setLength(1);
    oled_fld_bv_264786981.setPrefix("U=");
    oled_fld_bv_264786981.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_bv_264786981.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_bv_264786981.setTrueString("+");
    oled_fld_bv_264786981.setFalseString("-");
    //------  Виджет Битовое значение
    oled_scr_263585980.setWidget(13, &oled_fld_bv_123679529);
    oled_fld_bv_123679529.setLength(1);
    oled_fld_bv_123679529.setPrefix("M=");
    oled_fld_bv_123679529.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_bv_123679529.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_bv_123679529.setTrueString("+");
    oled_fld_bv_123679529.setFalseString("-");
    //------  Виджет Битовое значение
    oled_scr_263585980.setWidget(14, &oled_fld_bv_143217628);
    oled_fld_bv_143217628.setLength(1);
    oled_fld_bv_143217628.setPrefix("T=");
    oled_fld_bv_143217628.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_bv_143217628.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_bv_143217628.setTrueString("+");
    oled_fld_bv_143217628.setFalseString("-");
    //------  Виджет Цифровое значение
    oled_scr_263585980.setWidget(15, &oled_fld_nv_207743169);
    oled_fld_nv_207743169.setLength(3);
    oled_fld_nv_207743169.setMode(FLPROG_OLED_DEFAULT_VALUE_MODE);
    oled_fld_nv_207743169.setAlign(FLPROG_OLED_CENTER_ALIGN_VALUE_MODE);
    oled_fld_nv_207743169.setVarType(FLPROG_OLED_NUNBER_UINT8_TYPE);
    oled_156902651_chip.secondDebugCallback(oled_156902651_firstDebug);
    oled_156902651_chip.secondDebugCallback(oled_156902651_secondDebug);
    //========================================================================================================================================
    //++++ Конец настройки дисплея OLED SH1107 MONO (I2C0) ++++
    //========================================================================================================================================
    flprog::specialSetup();
}
void loop()
{
    //Плата:1
    //Наименование:Настройка параметров проекта
    //Комментарии:Выполняется один раз
    if (!RT_HW_Base.shed.ready)
    {
        SysPar_54877633_modbusMaster_isEnable_set((!(1)));
        Out_45575441_239928664 = 1;
        _tempVariable_int16_t = ((ExternalEEPROM_252608257.readByte(2)));
        Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 44);
        _tempVariable_int16_t = ((ExternalEEPROM_252608257.readByte(3)));
        Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 47);
        _tempVariable_int16_t = ((ExternalEEPROM_252608257.readByte(1)));
        Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 48);
        SysPar_56202579_rasterDisplay_canWork_set((!(0)));
        if (!InitConsole_7_init)
        {
            InitConsole_7_init = 1;
            RT_HW_console.setParam((6), (RT_HW_Base.uartGetSpeed((6))));
        }
    }
    RT_HW_Base.sheduler();
    flprog::specialPool();
    if (RT_HW_Base.shed.eventSec)
    {
        TaskManager_Filter.filtered(RT_HW_Base.shed.cycle);
    }
    if (RT_HW_Base.shed.sysQuick.num == 1) { FLProgBTN5.pool(); }
    if (RT_HW_Base.shed.sysQuick.num == 2) { FLProgSound.pool(); }
    if (RT_HW_Base.shed.sysQuick.num == 3) { FLProgBright.pool(); }
    if (RT_HW_Base.shed.sysQuick.num == 4)
    {
        FLProgADS1115.pool(FLProgADC);
        FLProgADC.pool();
    }
    if (RT_HW_Base.shed.sysQuick.num == 5)
    {
        FLProgDAC.pool();
        FLProgDAC_STM32.pool(FLProgDAC);
    }
    if (RT_HW_Base.shed.sysQuick.num == 1)
    {
        WiznetInterface_165513604.pool();
    }
    if (RT_HW_Base.shed.sysQuick.num == 2)
    {
        Modbus_144774688.pool();
    }
    if (RT_HW_Base.shed.sysQuick.num == 3)
    {
        Modbus_45921880.pool();
    }
    if (RT_HW_Base.shed.sysQuick.num == 4)
    {
        Modbus_251262745.pool();
    }
    if (RT_HW_Base.shed.sysQuick.num == 5)
    {
        Modbus_246570956.pool();
    }
    if (RT_HW_Base.shed.sysQuick.num == 6)
    {
        Modbus_32382178.pool();
    }
    if (RT_HW_Base.shed.sysQuick.num == 7)
    {
        Modbus_95643830.pool();
    }
    if (RT_HW_Base.shed.sysQuick.num == 8)
    {
        Modbus_83290452.pool();
    }
    if (RT_HW_Base.shed.sysQuick.num == 9)
    {
        ExternalEEPROM_252608257.pool();
    }
    if (RT_HW_Base.shed.sysQuick.num == 10)
    {
        if (!FLProgWatch.custom)
        {
            FLProgWatch.periodGetRTC = 500;
            FLProgWatch.bus = 1;
        }
        FLProgWatch.direct();
    }
    if (RT_HW_Base.shed.sysQuick.num == 11)
    {
        if (FLProgTestGen_70.custom == 0)
        {
            _tempVariable_uint8_t = 14;
            FLProgTestGen_70.qnt = _tempVariable_uint8_t;
            FLProgTestGen_70.setParamS(1, 4, _tempVariable_uint8_t, 1, 250, 1000);
            FLProgTestGen_70.setParamT(1, 4, _tempVariable_uint8_t, 1, 250, 1000);
            FLProgTestGen_70.setParamB(1, 4, _tempVariable_uint8_t, 1, 250, 1000);
            FLProgTestGen_70.setParamC(1, 4, _tempVariable_uint8_t, 1, 250, 1000);
            FLProgTestGen_70.custom = 1;
        }
        FLProgTestGen_70.EN = (!(_gtv23));
        FLProgTestGen_70.direct();
    }
    if (RT_HW_Base.shed.sysQuick.num == 12)
    {
        //========================================================================================================================================
        //++++ Начало тела дисплея  TFT ST7735 RGB (SPI1) ++++
        //========================================================================================================================================
        oled_fld_nv_117332420.setValue(_gtv63);
        oled_fld_nv_166583876.setValue(_gtv62);
        oled_fld_bv_59587394.setValue(_gtv64);
        oled_fld_sv_226067155.setValue(_gtv61);
        oled_fld_sv_64681359.setValue(_gtv60);
        oled_fld_sv_253709455.setValue(_gtv59);
        oled_fld_sv_56713862.setValue(_gtv58);
        oled_fld_bv_138544549.setValue((SysPar_192055330_taskManager_meander500ms_get()));
        oled_fld_nvl_171661469.setValue(((ExternalEEPROM_252608257.readByte(4))));
        oled_fld_nv_164605960.setValue((SysPar_192055330_taskManager_workTime_get()));
        oled_fld_nv_67445460.setValue((SysPar_46186475_watch_currentDate_get()));
        oled_fld_nv_156182767.setValue((SysPar_46186475_watch_currentMonth_get()));
        oled_fld_nv_34185301.setValue((SysPar_46186475_watch_currentYear2_get()));
        if (_gtv26) { oled_fld_txt_213810209.setColorFigure(RT_HW_OLED_FILL_CYAN); }
        else
        {
            oled_fld_txt_213810209.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nv_36732314.setValue((SysPar_46186475_watch_currentSec_get()));
        oled_fld_nv_134819151.setValue((SysPar_46186475_watch_currentMin_get()));
        oled_fld_nv_25335513.setValue((SysPar_46186475_watch_currentHour_get()));
        oled_fld_nv_196997419.setValue((SysPar_192055330_taskManager_speedofCORE0InLoopCyclesSec_get()));
        oled_scr_48392945.isActive((_gtv8) == 1);
        oled_fld_nv_198685733.setValue((SysPar_46186475_watch_currentHour_get()));
        oled_fld_nv_175148948.setValue((SysPar_46186475_watch_currentMin_get()));
        oled_fld_nv_32528453.setValue((SysPar_46186475_watch_currentSec_get()));
        if (_gtv26) { oled_fld_txt_16243548.setColorFigure(RT_HW_OLED_FILL_CYAN); }
        else
        {
            oled_fld_txt_16243548.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nv_41069956.setValue((SysPar_46186475_watch_currentYear2_get()));
        oled_fld_nv_61032334.setValue((SysPar_46186475_watch_currentMonth_get()));
        oled_fld_nv_108347373.setValue((SysPar_46186475_watch_currentDate_get()));
        oled_fld_nv_26807825.setValue((SysPar_192055330_taskManager_speedofCORE0InLoopCyclesSec_get()));
        oled_scr_200663618.isActive((_gtv8) == 2);
        oled_fld_nv_140658593.setValue((FLProgADC.AD[3].valueDevRAM));
        oled_fld_nv_125727405.setValue((FLProgADC.AD[2].valueDevRAM));
        oled_fld_nv_245400241.setValue((FLProgADC.AD[1].valueDevRAM));
        oled_fld_nv_196593743.setValue((FLProgADC.AD[0].valueDevRAM));
        oled_fld_nv_248199219.setValue((FLProgADC.AD[0].valueMV));
        oled_fld_nv_113347223.setValue((FLProgADC.AD[2].valueMV));
        oled_fld_nv_121085400.setValue((FLProgADC.AD[1].valueMV));
        oled_fld_nv_256356637.setValue((FLProgADC.AD[3].valueMV));
        oled_fld_nv_97585484.setValue((SysPar_192055330_taskManager_speedofCORE0InLoopCyclesSec_get()));
        oled_fld_nv_105742732.setValue(_gtv41);
        oled_fld_nv_191669495.setValue(_gtv42);
        oled_fld_nv_16086042.setValue(_gtv43);
        oled_fld_nv_115923925.setValue(_gtv44);
        oled_fld_bv_183590754.setValue(_gtv47);
        oled_fld_nv_31350185.setValue(_gtv39);
        oled_fld_nv_58867727.setValue(_gtv40);
        oled_scr_120866812.isActive(((_gtv8)) == 3);
        oled_fld_nv_245388940.setValue(_gtv49);
        oled_fld_gaude_107943078.setValue(_gtv49);
        oled_fld_nv_185289915.setValue(_gtv48);
        oled_fld_gaude_215774609.setValue(_gtv48);
        oled_fld_nv_161568141.setValue(_gtv38);
        oled_fld_nv_37782062.setValue(_gtv14);
        oled_fld_nv_58823822.setValue((SysPar_192055330_taskManager_speedofCORE0InLoopCyclesSec_get()));
        oled_scr_29161469.isActive(((_gtv8)) == 4);
        oled_fld_bv_5505156.setValue(_gtv55);
        oled_fld_bv_206232748.setValue(_gtv12);
        oled_fld_nv_37048924.setValue(((ExternalEEPROM_252608257.readByte(4))));
        if (_gtv55) { oled_fld_nvl_126836762.setColorFigure(RT_HW_OLED_FILL_MAGENTA); }
        else
        {
            oled_fld_nvl_126836762.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nvl_126836762.setValue(((ExternalEEPROM_252608257.readByte(4))));
        oled_fld_nv_196179951.setValue((SysPar_192055330_taskManager_speedofCORE0InLoopCyclesSec_get()));
        if (_gtv12) { oled_fld_rect_28526112.setColorFigure(RT_HW_OLED_FILL_MAGENTA); }
        else
        {
            oled_fld_rect_28526112.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_scr_73848182.isActive(((_gtv8)) == 5);
        oled_fld_nv_125668277.setValue((SysPar_192055330_taskManager_speedofCORE0InLoopCyclesSec_get()));
        oled_fld_nv_50179035.setValue(_gtv27);
        if (_gtv16) { oled_fld_nv_197292450.setColorFigure(RT_HW_OLED_FILL_MAGENTA); }
        else
        {
            oled_fld_nv_197292450.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nv_197292450.setValue(((ExternalEEPROM_252608257.readByte(1))));
        if (_gtv13) { oled_fld_nv_62290336.setColorFigure(RT_HW_OLED_FILL_MAGENTA); }
        else
        {
            oled_fld_nv_62290336.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nv_62290336.setValue(((ExternalEEPROM_252608257.readByte(3))));
        if (_gtv10) { oled_fld_nv_222539793.setColorFigure(RT_HW_OLED_FILL_CYAN); }
        else
        {
            oled_fld_nv_222539793.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nv_222539793.setValue(((ExternalEEPROM_252608257.readByte(2))));
        if (_gtv1) { oled_fld_nv_111504103.setColorFigure(RT_HW_OLED_FILL_CYAN); }
        else
        {
            oled_fld_nv_111504103.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nv_111504103.setValue((SysPar_46186475_watch_currentHour_get()));
        if (_gtv2) { oled_fld_nv_119285938.setColorFigure(RT_HW_OLED_FILL_CYAN); }
        else
        {
            oled_fld_nv_119285938.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nv_119285938.setValue((SysPar_46186475_watch_currentMin_get()));
        if (_gtv3) { oled_fld_nv_67458057.setColorFigure(RT_HW_OLED_FILL_CYAN); }
        else
        {
            oled_fld_nv_67458057.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nv_67458057.setValue((SysPar_46186475_watch_currentSec_get()));
        if (_gtv26) { oled_fld_txt_39400095.setColorFigure(RT_HW_OLED_FILL_CYAN); }
        else
        {
            oled_fld_txt_39400095.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        if (_gtv6) { oled_fld_nv_196225129.setColorFigure(RT_HW_OLED_FILL_CYAN); }
        else
        {
            oled_fld_nv_196225129.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nv_196225129.setValue((SysPar_46186475_watch_currentYear2_get()));
        if (_gtv5) { oled_fld_nv_90867036.setColorFigure(RT_HW_OLED_FILL_CYAN); }
        else
        {
            oled_fld_nv_90867036.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nv_90867036.setValue((SysPar_46186475_watch_currentMonth_get()));
        if (_gtv4) { oled_fld_nv_94987733.setColorFigure(RT_HW_OLED_FILL_CYAN); }
        else
        {
            oled_fld_nv_94987733.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_fld_nv_94987733.setValue((SysPar_46186475_watch_currentDate_get()));
        if (_gtv7) { oled_fld_rect_118135175.setColorFigure(RT_HW_OLED_FILL_BLUE); }
        else
        {
            oled_fld_rect_118135175.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        if (_gtv19) { oled_fld_rect_135629005.setColorFigure(RT_HW_OLED_FILL_CYAN); }
        else
        {
            oled_fld_rect_135629005.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        if (_gtv11) { oled_fld_rect_114909367.setColorFigure(RT_HW_OLED_FILL_MAGENTA); }
        else
        {
            oled_fld_rect_114909367.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        if (_gtv15) { oled_fld_rect_207741416.setColorFigure(RT_HW_OLED_FILL_MAGENTA); }
        else
        {
            oled_fld_rect_207741416.setColorFigure(RT_HW_OLED_FILL_BLACK);
        }
        oled_scr_127594733.isActive(((_gtv8)) == 6);
        oled_fld_bv_193114660.setValue((SysPar_192055330_taskManager_meander500ms_get()));
        oled_scr_83073005.isActive(((_gtv8)) == 0);
        oled_138862728_chip.pool(oled_138862728.getEn());
        oled_138862728.displayOn(&oled_138862728_chip);
        RT_HW_OLED_DEBUG_outParam(oled_138862728_chip.getNum());
        //========================================================================================================================================
        //++++ Конец тела дисплея TFT ST7735 RGB (SPI1)  ++++
        //========================================================================================================================================
    }
    if (RT_HW_Base.shed.sysQuick.num == 13)
    {
        //========================================================================================================================================
        //++++ Начало тела дисплея  OLED SH1107 MONO (I2C0) ++++
        //========================================================================================================================================
        oled_fld_nv_207743169.setValue(_gtv36);
        oled_fld_bv_143217628.setValue(_gtv23);
        oled_fld_bv_123679529.setValue(_gtv31);
        oled_fld_bv_264786981.setValue(_gtv51);
        oled_fld_nv_218060352.setValue(_gtv33);
        oled_fld_nvl_133196007.setValue(((ExternalEEPROM_252608257.readByte(4))));
        oled_fld_nv_178356505.setValue(((ExternalEEPROM_252608257.readByte(4))));
        oled_fld_nv_168504598.setValue(_gtv56);
        oled_fld_nv_212028031.setValue(((ExternalEEPROM_252608257.readByte(1))));
        oled_fld_nv_151802975.setValue(((ExternalEEPROM_252608257.readByte(2))));
        oled_fld_nv_63387461.setValue(((ExternalEEPROM_252608257.readByte(3))));
        oled_fld_bv_183396639.setValue((SysPar_192055330_taskManager_meander500ms_get()));
        oled_fld_nv_80992857.setValue((SysPar_192055330_taskManager_workTime_get()));
        oled_fld_nv_66101037.setValue((SysPar_192055330_taskManager_speedofCORE0InLoopCyclesSec_get()));
        oled_fld_nv_198500841.setValue(_gtv27);
        oled_fld_nv_123085538.setValue(_gtv8);
        oled_156902651_chip.pool(oled_156902651.getEn());
        oled_156902651.displayOn(&oled_156902651_chip);
        //========================================================================================================================================
        //++++ Конец тела дисплея OLED SH1107 MONO (I2C0)  ++++
        //========================================================================================================================================
    }
    //Плата:2
    //Наименование:Вывод параметров проекта на консоль
    //Комментарии:Вывод blink на Led.25
    if (RT_HW_Base.shed.fast.num == 1)
    {
        if (RT_HW_console.dev.first && (!(0)))
        {
            if (RT_HW_console.getHead())
            {
                RT_HW_console.clrHead();
                RT_HW_console.outCR(1);
                RT_HW_console.outHeadMain();
                RT_HW_console.outHeadMainAdd();
                RT_HW_console.outHeadSheduler();
                RT_HW_console.outHeadPins();
                RT_HW_console.outHeadLink();
                RT_HW_console.outHeadTestPins();
                RT_HW_console.outHeadTestUART();
                RT_HW_console.outHeadETH();
                RT_HW_console.PLC_outXXX(0);
                RT_HW_console.PLC_outUART();
                RT_HW_console.PLC_outPinXXX();
                RT_HW_console.outHeadTestAdd();
                RT_HW_console.outHeadScanI2C();
                RT_HW_console.outLine('-', 80);
                RT_HW_console.outCR(1);
            }
        }
        ConsoleBoardBlock15_enOut = (!(0)) & ((bool)RT_HW_console.dev.ok);
        _gtv20 = ConsoleBoardBlock15_enOut;
        _gtv58 = (flprog::ipToString((SysPar_22886449_wizNet_ip_get())));
        _gtv59 = (flprog::ipToString((SysPar_22886449_wizNet_subnet_get())));
        _gtv60 = (flprog::ipToString((SysPar_22886449_wizNet_gateway_get())));
        _gtv61 = (flprog::ipToString((SysPar_22886449_wizNet_dns_get())));
        // System channels: remaining RT_HW console parameters.
        static uint32_t webConsolePublishedAt = 0;
        if ((uint32_t)(millis() - webConsolePublishedAt) >= 1000) {
            webConsolePublishedAt = millis();
            FLProgWebUiRuntime::publishBool(29, RT_HW_console.dev.ok);
            FLProgWebUiRuntime::publishText(31, String(RT_HW_Base.getCoreName()).c_str());
            FLProgWebUiRuntime::publishText(32, String(RT_HW_Base.getArchName()).c_str());
            FLProgWebUiRuntime::publishText(33, String(RT_HW_Base.getIDE_CoreVerName()).c_str());
            FLProgWebUiRuntime::publishInt(34, RT_HW_Base.getFCPU());
            FLProgWebUiRuntime::publishInt(35, RT_HW_Base.getVcc());
            FLProgWebUiRuntime::publishText(37, String(String(RT_HW_Base.getBoardID())).c_str());
            FLProgWebUiRuntime::publishText(38, String(String(RT_HW_BASE_VER_NAME)).c_str());
            FLProgWebUiRuntime::publishText(39, String(String(RT_HW_CONSOLE_VER_NAME)).c_str());
            FLProgWebUiRuntime::publishInt(40, SysPar_192055330_taskManager_speedofCORE0InLoopCyclesSec_get());
            FLProgWebUiRuntime::publishText(41, String(String("quick=")+RT_HW_Base.shed.quick.qnt+" fast="+RT_HW_Base.shed.fast.qnt+" slow="+RT_HW_Base.shed.slow.qnt+" back="+RT_HW_Base.shed.back.qnt+" frdm="+RT_HW_Base.shed.frdm.qnt).c_str());
        }
        consoleVarBlock_17_Task.extEN = 1;
        if (consoleVarBlock_17_Task.custom == 0)
        {
            RT_HW_Base.setTaskID(consoleVarBlock_17_Task, 'C', 1000, 1000);
            consoleVarBlock_17_Task.periodLimit = 0;
        }
        RT_HW_Base.directTask(consoleVarBlock_17_Task);
        if ((consoleVarBlock_17_Task.run == 1) || (consoleVarBlock_17_Task.run == 2))
        {
            if (consoleVarBlock_17_valueArray[0] != ((flprog::ipToString((SysPar_22886449_wizNet_ip_get())))))
            {
                consoleVarBlock_17_valueArray[0] = ((flprog::ipToString((SysPar_22886449_wizNet_ip_get()))));
                consoleVarBlock_17_ok = 1;
            }
            if (consoleVarBlock_17_valueArray[1] != ((flprog::ipToString((SysPar_22886449_wizNet_subnet_get())))))
            {
                consoleVarBlock_17_valueArray[1] = ((flprog::ipToString((SysPar_22886449_wizNet_subnet_get()))));
                consoleVarBlock_17_ok = 1;
            }
            if (consoleVarBlock_17_valueArray[2] != ((flprog::ipToString((SysPar_22886449_wizNet_gateway_get())))))
            {
                consoleVarBlock_17_valueArray[2] = ((flprog::ipToString((SysPar_22886449_wizNet_gateway_get()))));
                consoleVarBlock_17_ok = 1;
            }
            if (consoleVarBlock_17_valueArray[3] != ((flprog::ipToString((SysPar_22886449_wizNet_dns_get())))))
            {
                consoleVarBlock_17_valueArray[3] = ((flprog::ipToString((SysPar_22886449_wizNet_dns_get()))));
                consoleVarBlock_17_ok = 1;
            }
            if ((consoleVarBlock_17_Task.run == 1) || ((consoleVarBlock_17_Task.run == 2) && (consoleVarBlock_17_ok)))
            {
                consoleVarBlock_17_ok = 0;
                consoleVarBlock_17_Task.run = 5;
                consoleVarBlock_17_run = 1;
            }
        }
        if (consoleVarBlock_17_run)
        {
            if (RT_HW_console.getOk())
            {
                RT_HW_console.outVar(String(F("Eth1:")), '~', 0);
                RT_HW_console.outArr(consoleVarBlock_17_valueArray, 4, 'E', 0, 'L');
                consoleVarBlock_17_run = 0;
            }
        }
        _gtv62 = ((SysPar_22886449_wizNet_status_get()));
        _gtv63 = ((SysPar_22886449_wizNet_error_get()));
        consoleVarBlock_22_Task.extEN = 1;
        if (consoleVarBlock_22_Task.custom == 0)
        {
            RT_HW_Base.setTaskID(consoleVarBlock_22_Task, 'C', 1000, 1000);
            consoleVarBlock_22_Task.periodLimit = 0;
        }
        RT_HW_Base.directTask(consoleVarBlock_22_Task);
        if ((consoleVarBlock_22_Task.run == 1) || (consoleVarBlock_22_Task.run == 2))
        {
            if (consoleVarBlock_22_valueArray[0] != (((SysPar_22886449_wizNet_status_get()))))
            {
                consoleVarBlock_22_valueArray[0] = (((SysPar_22886449_wizNet_status_get())));
                consoleVarBlock_22_ok = 1;
            }
            if (consoleVarBlock_22_valueArray[1] != (((SysPar_22886449_wizNet_error_get()))))
            {
                consoleVarBlock_22_valueArray[1] = (((SysPar_22886449_wizNet_error_get())));
                consoleVarBlock_22_ok = 1;
            }
            if ((consoleVarBlock_22_Task.run == 1) || ((consoleVarBlock_22_Task.run == 2) && (consoleVarBlock_22_ok)))
            {
                consoleVarBlock_22_ok = 0;
                consoleVarBlock_22_Task.run = 5;
                consoleVarBlock_22_run = 1;
            }
        }
        if (consoleVarBlock_22_run)
        {
            if (RT_HW_console.getOk())
            {
                RT_HW_console.outVar(String(F("Eth1: ready,status,err")), '=', 0);
                RT_HW_console.outArr(consoleVarBlock_22_valueArray, 2, 'E', 0, 'Z');
                consoleVarBlock_22_run = 0;
            }
        }
        _gtv64 = ((SysPar_22886449_wizNet_redy_get()));
    }
    //Плата:3
    //Наименование:Выбор алгоритма работы программы
    //Комментарии:1.User, 2.Modbus, 3.Test
    if (RT_HW_Base.shed.fast.num == 1)
    {
        if ((((((ExternalEEPROM_252608257.readByte(4))) == 3)) && ((_gtv8) == (0))))
        {
            if (_tim40I)
            {
                if (flprog::isTimer(_tim40P, 1000)) { _tim40O = 1; }
            }
            else
            {
                _tim40I = 1;
                _tim40P = millis();
            }
        }
        else
        {
            _tim40O = 0;
            _tim40I = 0;
        }
        _gtv23 = _tim40O;
        _gtv31 = (((ExternalEEPROM_252608257.readByte(4))) == 2);
        _gtv51 = (((ExternalEEPROM_252608257.readByte(4))) == 1);
    }
    //Плата:4
    //Наименование:Настройка и Управление устройством
    //Комментарии:Настройка экранов
    if (RT_HW_Base.shed.quick.num == 1)
    {
        DI_block_42_outValue = (FLProgBTN5.button1);
        DI_block_43_outValue = (FLProgBTN5.button2);
        DI_block_44_outValue = (FLProgBTN5.button3);
        DI_block_45_outValue = (FLProgBTN5.button4);
        DI_block_46_outValue = (FLProgBTN5.button5);
        //=================================================================================================
        //			Клавиатура: управление, декодирование в параметры объекта
        //=================================================================================================
        // clang-format off
{	auto& base=RT_HW_Base;	(void)base;
	auto& kc=RT_HW_keyControl;   (void)kc;
	auto& id=keyControl_194900649; (void)id;
	uint8_t vEN=1;  uint8_t num=0;
//--------------------------------------------------------------------------------------------------
			num=kc.pool_BTN(id, vEN, (DI_block_42_outValue), (DI_block_43_outValue), (DI_block_44_outValue), (DI_block_45_outValue), (DI_block_46_outValue));	//--Основной экранный автомат BTN5;
//--------------------------------------------------------------------------------------------------
//                                  3. Настройка общая
//--------------------------------------------------------------------------------------------------
		if(!id.custom){if(vEN){if(kc.checkNum(num)){
				kc.setScreenControl(num,1); //--0: проект; 1: клавиатура LEFT/RIGHT;
				kc.setScreenSetForce(num,0);      //--0: soft; 1: force;
				kc.setTimeScreenStart(num,3000);	//--Время отображения стартового экрана, мс;
				kc.setTimeStartEdit(num,1000);	//--Время удержания SET для входа в редактирование, мс;;
				kc.setTimeOutEdit(num,10000);		//--//--Тайм-аут выхода из редактирования; 0-отключён, мс;
				kc.setTimeOutReturnScreenDefault(num,20000);	//--Тайм-аут возврата на экран по умолчанию; 0-отключён, мс;
				kc.setScreenDefault (num,1);	 //--Экран.table по умолчанию для возврата после тайм-аута;
				kc.setScreenStart(num,0);	 //--Стартовый экран.table; значение 255 отключает стартовый экран;;
		id.custom=1;}}}
//--------------------------------------------------------------------------------------------------
		kc.setScreenQnt(num,(6));	//--Количество экранов (ext);
		kc.setScreenBlink(num,base.getShedBlink500());		//--blink 500 ms;
//--------------------------------------------------------------------------------------------------
		kc.pool_Screen(num,vEN);	//--Основной автомат управления;
//--------------------------------------------------------------------------------------------------
		Out_4830120_194900649= kc.getScreenBlink(num);		//--Вывод blink;
		Out_133968906_194900649 = kc.getScreen(num);	//-- Вывод номера текущего экрана;
		Out_131944527_194900649 = num;	//--Вывод логического номера;
}
        // clang-format on
        //==================================================================================================
        _gtv25 = Out_131944527_194900649;
        _gtv8 = Out_133968906_194900649;
        _gtv26 = Out_4830120_194900649;
        //==================================================================================================
        //                                  KEY CONTROL: screen.Control
        //==================================================================================================
        //  Назначение:
        //    Управление отдельным экраном. Блок задает количество редактируемых полей конкретного экрана
        //    и выдает состояние этого экрана: текущий экран, режим редактирования, номер поля, blink/focus.
        //--------------------------------------------------------------------------------------------------
        //  Входы:
        //    IN_NUM       - логический номер устройства от main-блока;
        //    IN_EN        - разрешение этого экрана;
        //    IN_SCREEN    - номер экрана;
        //    IN_FIELD_QNT - количество редактируемых полей на экране. Если 0, вход в edit невозможен.
        //==================================================================================================
        // clang-format off
{ auto& kc=RT_HW_keyControl;             (void)kc;
	uint8_t vEN=1; uint8_t num=(_gtv25); uint8_t scr=(5);
//--------------------------------------------------------------------------------------------------
 	kc.setScreenParamField((_gtv25),vEN,(5),(1));	//--//--Legacy-форма: параметры экрана, не смена текущего экрана;
//--------------------------------------------------------------------------------------------------
		Out_46217284_55922712=scr;
	Out_115940838_55922712=kc.getScreenField(num,scr);	//--0 — поле не выбрано, либо активен другой экран; 1..fieldQnt — номер активного редактируемого поля;
} 
// clang-format on          
//==================================================================================================
_gtv56 = Out_115940838_55922712;
_gtv21 = Out_46217284_55922712;
//==================================================================================================
//                                  KEY CONTROL: screen.Control
//==================================================================================================
//  Назначение:
//    Управление отдельным экраном. Блок задает количество редактируемых полей конкретного экрана
//    и выдает состояние этого экрана: текущий экран, режим редактирования, номер поля, blink/focus.
//--------------------------------------------------------------------------------------------------
//  Входы:
//    IN_NUM       - логический номер устройства от main-блока;
//    IN_EN        - разрешение этого экрана;
//    IN_SCREEN    - номер экрана;
//    IN_FIELD_QNT - количество редактируемых полей на экране. Если 0, вход в edit невозможен.
//==================================================================================================
// clang-format off
{ auto& kc=RT_HW_keyControl;             (void)kc;
	uint8_t vEN=1; uint8_t num=(_gtv25); uint8_t scr=(6);
//--------------------------------------------------------------------------------------------------
 	kc.setScreenParamField((_gtv25),vEN,(6),(9));	//--//--Legacy-форма: параметры экрана, не смена текущего экрана;
//--------------------------------------------------------------------------------------------------
		Out_46217284_81497009=scr;
	Out_115940838_81497009=kc.getScreenField(num,scr);	//--0 — поле не выбрано, либо активен другой экран; 1..fieldQnt — номер активного редактируемого поля;
} 
// clang-format on          
//==================================================================================================
_gtv27 = Out_115940838_81497009;
_gtv52 = Out_46217284_81497009;
//=================================================================================================
//						 			Управление звуком кнопок панели 
//=================================================================================================
            // clang-format off
{  auto& kc=RT_HW_keyControl;  (void)kc;
   auto& id=keyControlBright_113718779;  (void)id;
   auto& custom=custom_113718779; (void)custom;
   uint8_t num=(_gtv25);  (void)num; uint8_t wake=0; (void)wake;   
	if(!custom){
  		kc.setBrightnessEnable(id,  1);	 //--Управление яркостью 0: постоянная; 1: автоматическое уменьшение;
  		kc.setBrightnessLevelMain(id,100);
  		kc.setBrightnessLevelMin(id,20);
  		kc.setBrightnessTimeStart(id, 300);
  		kc.setBrightnessTimeStage(id,250);
		custom=1;}
  	kc.pool_Brightness(id,(_gtv25),wake);	//--Автомат яркости;
	Out_36333439_113718779=id.levelOut;
 }
        // clang-format on
        //==================================================================================================
        _gtv33 = Out_36333439_113718779;
        //=================================================================================================
        //						 			KEY PWM STM32 PA12,PC1
        //=================================================================================================
        RT_HW_keyControl.setPWM_PA12((Out_36333439_113718779)); //--key PWM STM32:PA12;
        //==================================================================================================
        //=================================================================================================
        //						 			Управление звуком кнопок панели
        //=================================================================================================
        // clang-format off
{  auto& kc=RT_HW_keyControl;  (void)kc;
   auto& id=keyControlSound_105013246;  (void)id;
   uint8_t num=(_gtv25); 
	if(!id.custom){
		kc.setSoundPermit(id,1);		
		kc.setSoundPermitKey(id,1);
		kc.setSoundPermitTest(id,0);
	id.custom=1;}
	kc.setSoundLevel(id,90); //--Уровень звука с панели табличный;
	kc.setSoundDuration(id,150); //--Длительность звука с панели табличный;
	kc.pool_Sound (id,num); //--Автомат звука;
	Out_36333439_105013246=id.valueOut;  	 //--Level 0..100;
 }
        // clang-format on
        //==================================================================================================
        _gtv36 = Out_36333439_105013246;
        //=================================================================================================
        //						 			KEY PWM STM32 PA12,PC1
        //=================================================================================================
        RT_HW_keyControl.setPWM_PC1((Out_36333439_105013246)); //--key PWM STM32:PC1;
        //==================================================================================================
    }
    //Плата:5
    //Наименование:Управление экраном 5 "Управление проектом"
    if (RT_HW_Base.shed.fast.num == 1)
    {
        //=================================================================================================
        //						 			Редактирование переменной
        //=================================================================================================
        // clang-format off
{  auto& kc=RT_HW_keyControl;             (void)kc;
   auto& id=keyControlEditNumber_132403258;    (void)id; 
   uint8_t vEN=1; uint8_t num=(_gtv25);
//=================================================================================================
//						 			Настройка параметров и режимов
//=================================================================================================
	if(!id.custom){
		kc.setParamEdit_RangeMode(id,1);	//--Уcтановка РЕЖИМА КОНТРОЛЯ ГРАНИЦ  ;
		kc.setParamEdit_Range(id, (1), (4));	//--ГРАНИЦЫ MIN/MAX;
		kc.setParamEdit_Default(id, 22);	//--ЗНАЧЕНИЕ ПО УМОЛЧАНИЮ
		kc.setParamEdit_WorkMode(id, 1);	//--РЕЖИМ РАБОТЫ DIRECT/FIELD;
		kc.setParamEdit_NumberMode(id, 2);	//--РЕЖИМ ЦИФРОВОГО ВВОДА (с клавиатуры);
		kc.setParamEdit_ClrMode(id, 2);	//--РЕЖИМ ОЧИСТКИ;
		kc.setParamEdit_MaxDigits(id,3);	//--МАКСИМАЛЬНОЕ КОЛИЧЕСТВО ЦИФР;
		kc.setParamEdit_InputMode(id,3);	//--ИСТОЧНИК ИЗМЕНЕНИЯ ПАРАМЕТРОВ;
		kc.setScreenEditNumber(id,(5), (1));	//--ПРИВЯЗКА К ЭКРАННОМУ ПОЛЮ;
		id.custom=1; 
	}	
//=================================================================================================
//						 			Редактирование переменной 
//=================================================================================================
	kc.pool_EditNumber(id,num,vEN,(((ExternalEEPROM_252608257.readByte(4)))));
	Out_620703_132403258 = id.value;
//=================================================================================================
//						 			ВЫВОД ПЕРЕМЕННЫХ
//=================================================================================================
	Out_94223944_132403258=id.set;
	Out_251185179_132403258  = id.select;
	Out_123807481_132403258 = id.blink;
}
        // clang-format on
        //==================================================================================================
        _gtv55 = Out_123807481_132403258;
        _gtv12 = Out_251185179_132403258;
        if (Out_94223944_132403258)
        {
            ExternalEEPROM_252608257.saveByte(4, ((Out_620703_132403258)));
        }
    }
    //Плата:6
    //Наименование:Тесты
    if (RT_HW_Base.shed.quick.num == 4)
    {
        E_Counter_73.top = 4095;
        E_Counter_73.step = 50;
        if (E_Counter_73.reset)
        {
            RT_HW_Base.counterSetParam(E_Counter_73, 4095, 0, 50, 0);
        }
        else
        {
            _tempVariable_bool = RT_HW_Base.generatorChangeEN(E_Counter_73_agoEn, 'C', (((SysPar_192055330_taskManager_meander100ms_get()))));
            RT_HW_Base.counterT(E_Counter_73, _tempVariable_bool);
        }
        _gtv53 = (E_Counter_73.cnt);
        _gtv57 = (4095) - ((E_Counter_73.cnt));
        if ((14) != FLProgTestGen_70.qnt)
        {
            FLProgTestGen_70.custom = 0;
            FLProgTestGen_70.dir = 0;
        }
        Out_108382167_158375559 = (uint16_t)(((FLProgTestGen_70.vr)) & 0xFFFF);
        Out_253334638_158375559 = (uint16_t)((((FLProgTestGen_70.vr)) >> 16) & 0xFFFF);
        _gtv24 = Out_253334638_158375559;
        _gtv50 = Out_108382167_158375559;
    }
    //Плата:7
    //Наименование:Управление экраном 6
    if (RT_HW_Base.shed.quick.num == 2)
    {
        //==================================================================================================
        //                                  KEY CONTROL: Корректировка RTC
        //--------------------------------------------------------------------------------------------------
        //  Упрощенный вариант: параметры времени занимают шесть последовательных редактируемых полей.
        //  firstField+0 - часы; firstField+1 - минуты; firstField+2 - секунды;
        //  firstField+3 - день; firstField+4 - месяц; firstField+5 - год.
        //  Перед вызовом этого блока экран должен быть зарегистрирован как редактируемый экран:
        //    kc.setScreenParamField(num,1,screenNum,fieldQnt);
        //  fieldQnt должен быть не меньше firstField+5.
        //==================================================================================================
        // clang-format off
{ auto& kc=RT_HW_keyControl; (void)kc;
  auto& id=id_24418774; (void)id;
  auto& ed=ed_24418774; (void)ed;
  uint8_t vEN=1;
//--------------------------------------------------------------------------------------------------
//                                  1. ВХОДНЫЕ ПАРАМЕТРЫ
//--------------------------------------------------------------------------------------------------
	uint8_t num=(_gtv25); 
//--------------------------------------------------------------------------------------------------
//                                  2. КОРРЕКТИРОВКА ВРЕМЕНИ
//--------------------------------------------------------------------------------------------------
	kc.pool_TimeCorrectRTC(id, FLProgWatch, RT_HW_Base.unixID,  num, vEN, (6), (1));
	Out_114685876_24418774=id.select;
//--------------------------------------------------------------------------------------------------
//                                  5.  Мигающие выходы активного параметра
//--------------------------------------------------------------------------------------------------
	Out_82050884_24418774 = bitRead(id.timeBlinkBitEdit,0);
	Out_215745335_24418774 = bitRead(id.timeBlinkBitEdit,1);
	Out_187138713_24418774 = bitRead(id.timeBlinkBitEdit,2);
	Out_117321672_24418774 = bitRead(id.timeBlinkBitEdit,3);
	Out_208344287_24418774 = bitRead(id.timeBlinkBitEdit,4);
	Out_3085716_24418774 = bitRead(id.timeBlinkBitEdit,5);
}
        // clang-format on
        //==================================================================================================
        _gtv6 = Out_3085716_24418774;
        _gtv5 = Out_208344287_24418774;
        _gtv4 = Out_117321672_24418774;
        _gtv3 = Out_187138713_24418774;
        _gtv2 = Out_215745335_24418774;
        _gtv1 = Out_82050884_24418774;
        _gtv19 = Out_114685876_24418774;
        //=================================================================================================
        //						 			Редактирование переменной
        //=================================================================================================
        // clang-format off
{  auto& kc=RT_HW_keyControl;             (void)kc;
   auto& id=keyControlEditNumber_239206608;    (void)id; 
   uint8_t vEN=1; uint8_t num=(_gtv25);
//=================================================================================================
//						 			Настройка параметров и режимов
//=================================================================================================
	if(!id.custom){
		kc.setParamEdit_RangeMode(id,1);	//--Уcтановка РЕЖИМА КОНТРОЛЯ ГРАНИЦ  ;
		kc.setParamEdit_Range(id,40,100);	//--ГРАНИЦЫ MIN/MAX;
		kc.setParamEdit_Default(id, 22);	//--ЗНАЧЕНИЕ ПО УМОЛЧАНИЮ
		kc.setParamEdit_WorkMode(id, 1);	//--РЕЖИМ РАБОТЫ DIRECT/FIELD;
		kc.setParamEdit_NumberMode(id, 2);	//--РЕЖИМ ЦИФРОВОГО ВВОДА (с клавиатуры);
		kc.setParamEdit_ClrMode(id, 2);	//--РЕЖИМ ОЧИСТКИ;
		kc.setParamEdit_MaxDigits(id,3);	//--МАКСИМАЛЬНОЕ КОЛИЧЕСТВО ЦИФР;
		kc.setParamEdit_InputMode(id,3);	//--ИСТОЧНИК ИЗМЕНЕНИЯ ПАРАМЕТРОВ;
		kc.setScreenEditNumber(id,(6), (7));	//--ПРИВЯЗКА К ЭКРАННОМУ ПОЛЮ;
		id.custom=1; 
	}	
//=================================================================================================
//						 			Редактирование переменной 
//=================================================================================================
	kc.pool_EditNumber(id,num,vEN,(((ExternalEEPROM_252608257.readByte(2)))));
	Out_620703_239206608 = id.value;
//=================================================================================================
//						 			ВЫВОД ПЕРЕМЕННЫХ
//=================================================================================================
	Out_94223944_239206608=id.set;
	Out_251185179_239206608  = id.select;
	Out_123807481_239206608 = id.blink;
}
        // clang-format on
        //==================================================================================================
        _gtv10 = Out_123807481_239206608;
        _gtv7 = Out_251185179_239206608;
        if (Out_94223944_239206608)
        {
            ExternalEEPROM_252608257.saveByte(2, ((Out_620703_239206608)));
        }
        //=================================================================================================
        //						 			Редактирование переменной
        //=================================================================================================
        // clang-format off
{  auto& kc=RT_HW_keyControl;             (void)kc;
   auto& id=keyControlEditNumber_242622828;    (void)id; 
   uint8_t vEN=1; uint8_t num=(_gtv25);
//=================================================================================================
//						 			Настройка параметров и режимов
//=================================================================================================
	if(!id.custom){
		kc.setParamEdit_RangeMode(id,1);	//--Уcтановка РЕЖИМА КОНТРОЛЯ ГРАНИЦ  ;
		kc.setParamEdit_Range(id,50,250);	//--ГРАНИЦЫ MIN/MAX;
		kc.setParamEdit_Default(id, 22);	//--ЗНАЧЕНИЕ ПО УМОЛЧАНИЮ
		kc.setParamEdit_WorkMode(id, 1);	//--РЕЖИМ РАБОТЫ DIRECT/FIELD;
		kc.setParamEdit_NumberMode(id, 2);	//--РЕЖИМ ЦИФРОВОГО ВВОДА (с клавиатуры);
		kc.setParamEdit_ClrMode(id, 2);	//--РЕЖИМ ОЧИСТКИ;
		kc.setParamEdit_MaxDigits(id,3);	//--МАКСИМАЛЬНОЕ КОЛИЧЕСТВО ЦИФР;
		kc.setParamEdit_InputMode(id,3);	//--ИСТОЧНИК ИЗМЕНЕНИЯ ПАРАМЕТРОВ;
		kc.setScreenEditNumber(id,(6), (9));	//--ПРИВЯЗКА К ЭКРАННОМУ ПОЛЮ;
		id.custom=1; 
	}	
//=================================================================================================
//						 			Редактирование переменной 
//=================================================================================================
	kc.pool_EditNumber(id,num,vEN,(((ExternalEEPROM_252608257.readByte(1)))));
	Out_620703_242622828 = id.value;
//=================================================================================================
//						 			ВЫВОД ПЕРЕМЕННЫХ
//=================================================================================================
	Out_94223944_242622828=id.set;
	Out_251185179_242622828  = id.select;
	Out_123807481_242622828 = id.blink;
}
        // clang-format on
        //==================================================================================================
        _gtv16 = Out_123807481_242622828;
        _gtv15 = Out_251185179_242622828;
        if (Out_94223944_242622828)
        {
            ExternalEEPROM_252608257.saveByte(1, ((Out_620703_242622828)));
        }
        //=================================================================================================
        //						 			Редактирование переменной
        //=================================================================================================
        // clang-format off
{  auto& kc=RT_HW_keyControl;             (void)kc;
   auto& id=keyControlEditNumber_56845173;    (void)id; 
   uint8_t vEN=1; uint8_t num=(_gtv25);
//=================================================================================================
//						 			Настройка параметров и режимов
//=================================================================================================
	if(!id.custom){
		kc.setParamEdit_RangeMode(id,1);	//--Уcтановка РЕЖИМА КОНТРОЛЯ ГРАНИЦ  ;
		kc.setParamEdit_Range(id,25,100);	//--ГРАНИЦЫ MIN/MAX;
		kc.setParamEdit_Default(id, 22);	//--ЗНАЧЕНИЕ ПО УМОЛЧАНИЮ
		kc.setParamEdit_WorkMode(id, 1);	//--РЕЖИМ РАБОТЫ DIRECT/FIELD;
		kc.setParamEdit_NumberMode(id, 2);	//--РЕЖИМ ЦИФРОВОГО ВВОДА (с клавиатуры);
		kc.setParamEdit_ClrMode(id, 2);	//--РЕЖИМ ОЧИСТКИ;
		kc.setParamEdit_MaxDigits(id,3);	//--МАКСИМАЛЬНОЕ КОЛИЧЕСТВО ЦИФР;
		kc.setParamEdit_InputMode(id,3);	//--ИСТОЧНИК ИЗМЕНЕНИЯ ПАРАМЕТРОВ;
		kc.setScreenEditNumber(id,(6), (8));	//--ПРИВЯЗКА К ЭКРАННОМУ ПОЛЮ;
		id.custom=1; 
	}	
//=================================================================================================
//						 			Редактирование переменной 
//=================================================================================================
	kc.pool_EditNumber(id,num,vEN,(((ExternalEEPROM_252608257.readByte(3)))));
	Out_620703_56845173 = id.value;
//=================================================================================================
//						 			ВЫВОД ПЕРЕМЕННЫХ
//=================================================================================================
	Out_94223944_56845173=id.set;
	Out_251185179_56845173  = id.select;
	Out_123807481_56845173 = id.blink;
}
        // clang-format on
        //==================================================================================================
        _gtv13 = Out_123807481_56845173;
        _gtv11 = Out_251185179_56845173;
        if (Out_94223944_56845173)
        {
            ExternalEEPROM_252608257.saveByte(3, ((Out_620703_56845173)));
        }
    }
    //Плата:8
    //Наименование:Корректировка RTC через Modbus
    if (RT_HW_Base.shed.fast.num == 1)
    {
        //=================================================================================================
        //						 			Корректировка RTC через ModBus
        //=================================================================================================
        RT_HW_Base.correctClock(correctClock_212663958, ((Modbus_144774688.readIntegerByIndex(4, 39))), 60000);
        Out_188021688_212663958 = correctClock_212663958.copy; //--Разрешение копирование времени из часов;
        Out_222744586_212663958 = correctClock_212663958.set; //--Строб записи часов;
        Out_620703_212663958 = correctClock_212663958.reset ? 0 : ((Modbus_144774688.readIntegerByIndex(4, 39))); //--Управление регистром корректировки ModBus;
        //==================================================================================================
        if (Out_222744586_212663958)
        {
            if (!SetDataTimeWatchBlock_113_OES)
            {
                SetDataTimeWatchBlock_113_OES = 1;
                FLProgWatch.checkDigitalTime(((Modbus_144774688.readIntegerByIndex(4, 32))), ((Modbus_144774688.readIntegerByIndex(4, 33))), ((Modbus_144774688.readIntegerByIndex(4, 34))), ((Modbus_144774688.readIntegerByIndex(4, 35))), ((Modbus_144774688.readIntegerByIndex(4, 36))), ((Modbus_144774688.readIntegerByIndex(4, 37))));
            }
        }
        else
        {
            SetDataTimeWatchBlock_113_OES = 0;
        }
        _tempVariable_uint32_t = (FLProgWatch.timeUNIX);
        Modbus_144774688.saveUnsignedLongByIndex(_tempVariable_uint32_t, 4, 4);
        if (Out_188021688_212663958)
        {
            _tempVariable_int16_t = (FLProgWatch.weekDay);
            Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 38);
        }
        if (Out_188021688_212663958)
        {
            _tempVariable_int16_t = (FLProgWatch.year4);
            Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 37);
        }
        if (Out_188021688_212663958)
        {
            _tempVariable_int16_t = (FLProgWatch.month);
            Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 36);
        }
        if (Out_188021688_212663958)
        {
            _tempVariable_int16_t = (FLProgWatch.day);
            Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 35);
        }
        if (Out_188021688_212663958)
        {
            _tempVariable_int16_t = (FLProgWatch.hours);
            Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 32);
        }
        if (Out_188021688_212663958)
        {
            _tempVariable_int16_t = (FLProgWatch.minutes);
            Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 33);
        }
        if (Out_188021688_212663958)
        {
            _tempVariable_int16_t = (FLProgWatch.seconds);
            Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 34);
        }
        _tempVariable_int16_t = Out_620703_212663958;
        Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 39);
    }
    //Плата:9
    //Наименование:Регистры modbus (W/R): часть 1
    if (0)
    {
        _tempVariable_uint32_t = ((SysPar_46186475_watch_currentTimeUNIX_get()));
        Modbus_144774688.saveUnsignedLongByIndex(_tempVariable_uint32_t, 4, 4);
        _tempVariable_uint32_t = ((SysPar_192055330_taskManager_workTime_get()));
        Modbus_144774688.saveUnsignedLongByIndex(_tempVariable_uint32_t, 4, 2);
        _tempVariable_uint32_t = ((SysPar_192055330_taskManager_speedofCORE0InLoopCyclesSec_get()));
        Modbus_144774688.saveUnsignedLongByIndex(_tempVariable_uint32_t, 4, 0);
        _tempVariable_int16_t = ((ExternalEEPROM_252608257.readByte(2)));
        if (_tempVariable_int16_t != (MbVar_73391362_block_135_oldVal))
        {
            MbVar_73391362_block_135_oldVal = _tempVariable_int16_t;
            Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 44);
        }
        _tempVariable_int16_t = ((ExternalEEPROM_252608257.readByte(3)));
        if (_tempVariable_int16_t != (MbVar_34069315_block_131_oldVal))
        {
            MbVar_34069315_block_131_oldVal = _tempVariable_int16_t;
            Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 47);
        }
        _tempVariable_int16_t = ((ExternalEEPROM_252608257.readByte(1)));
        if (_tempVariable_int16_t != (MbVar_175017727_block_132_oldVal))
        {
            MbVar_175017727_block_132_oldVal = _tempVariable_int16_t;
            Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 48);
        }
        _tempVariable_int16_t = ((ExternalEEPROM_252608257.readByte(3)));
        if (_tempVariable_int16_t != (MbVar_69511086_block_130_oldVal))
        {
            MbVar_69511086_block_130_oldVal = _tempVariable_int16_t;
            Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 49);
        }
    }
    //Плата:10
    if (RT_HW_Base.shed.quick.num == 3)
    {
        // Consume and discard commands while disabled; no deferred replay.
        bool webModeRequest = false;
        if (FLProgWebUiRuntime::takeBool(137, webModeRequest)) {
            profileWebOutputEnabled = webModeRequest && WiznetInterface_165513604.isReady();
            profileWebDoMask = 0; profileWebAo[0] = profileWebAo[1] = 0;
        }
        bool webDoRequest = false; int32_t webAoRequest = 0;
        if (FLProgWebUiRuntime::takeBool(121, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 0);
            else profileWebDoMask &= (uint16_t)~(1U << 0);
        }
        if (FLProgWebUiRuntime::takeBool(122, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 1);
            else profileWebDoMask &= (uint16_t)~(1U << 1);
        }
        if (FLProgWebUiRuntime::takeBool(123, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 2);
            else profileWebDoMask &= (uint16_t)~(1U << 2);
        }
        if (FLProgWebUiRuntime::takeBool(124, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 3);
            else profileWebDoMask &= (uint16_t)~(1U << 3);
        }
        if (FLProgWebUiRuntime::takeBool(125, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 4);
            else profileWebDoMask &= (uint16_t)~(1U << 4);
        }
        if (FLProgWebUiRuntime::takeBool(126, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 5);
            else profileWebDoMask &= (uint16_t)~(1U << 5);
        }
        if (FLProgWebUiRuntime::takeBool(127, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 6);
            else profileWebDoMask &= (uint16_t)~(1U << 6);
        }
        if (FLProgWebUiRuntime::takeBool(128, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 7);
            else profileWebDoMask &= (uint16_t)~(1U << 7);
        }
        if (FLProgWebUiRuntime::takeBool(129, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 8);
            else profileWebDoMask &= (uint16_t)~(1U << 8);
        }
        if (FLProgWebUiRuntime::takeBool(130, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 9);
            else profileWebDoMask &= (uint16_t)~(1U << 9);
        }
        if (FLProgWebUiRuntime::takeBool(131, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 10);
            else profileWebDoMask &= (uint16_t)~(1U << 10);
        }
        if (FLProgWebUiRuntime::takeBool(132, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 11);
            else profileWebDoMask &= (uint16_t)~(1U << 11);
        }
        if (FLProgWebUiRuntime::takeBool(133, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 12);
            else profileWebDoMask &= (uint16_t)~(1U << 12);
        }
        if (FLProgWebUiRuntime::takeBool(134, webDoRequest) && profileWebOutputEnabled) {
            if (webDoRequest) profileWebDoMask |= (uint16_t)(1U << 13);
            else profileWebDoMask &= (uint16_t)~(1U << 13);
        }
        if (FLProgWebUiRuntime::takeInt(135, webAoRequest) && profileWebOutputEnabled && webAoRequest >= 0 && webAoRequest <= 10000)
            profileWebAo[0] = (uint16_t)webAoRequest;
        if (FLProgWebUiRuntime::takeInt(136, webAoRequest) && profileWebOutputEnabled && webAoRequest >= 0 && webAoRequest <= 10000)
            profileWebAo[1] = (uint16_t)webAoRequest;
        FLProgWebUiRuntime::publishBool(137, profileWebOutputEnabled);
        FLProgWebUiRuntime::publishBool(42, profileWebOutputEnabled && WiznetInterface_165513604.isReady());
        FLProgWebUiRuntime::publishText(43, profileWebOutputEnabled ? "Веб" : "Логика ПЛК");
        AI_block_137_outValue = (FLProgADC.AD[0].valueDevRAM);
        _gtv41 = AI_block_137_outValue;
        AI_block_144_outValue = (FLProgADC.AD[1].valueDevRAM);
        _gtv42 = AI_block_144_outValue;
        FLProgPin_PC2.digitalWrite(((SysPar_192055330_taskManager_meander500ms_get())));
        AI_block_145_outValue = (FLProgADC.AD[2].valueDevRAM);
        _gtv43 = AI_block_145_outValue;
        AI_block_146_outValue = (FLProgADC.AD[3].valueDevRAM);
        _gtv44 = AI_block_146_outValue;
        FLProgDAC.DA[0].setValueSystem((_gtv48)); //--Установка значения DA0;
        _tempVariable_int16_t = _gtv48;
        Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 30);
        _gtv45 = 0;
        FLProgDAC.DA[1].setValueSystem((_gtv49)); //--Установка значения DA1;
        _tempVariable_int16_t = _gtv49;
        Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 31);
        _gtv46 = 0;
        _tempVariable_int16_t = _gtv14;
        Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 14);
        _tempVariable_uint16_t = _gtv14;
        _VarToBit_149_1 = (_tempVariable_uint16_t) & 0x1;
        _VarToBit_149_2 = (_tempVariable_uint16_t >> 1) & 0x1;
        _VarToBit_149_3 = (_tempVariable_uint16_t >> 2) & 0x1;
        _VarToBit_149_4 = (_tempVariable_uint16_t >> 3) & 0x1;
        _VarToBit_149_5 = (_tempVariable_uint16_t >> 4) & 0x1;
        _VarToBit_149_6 = (_tempVariable_uint16_t >> 5) & 0x1;
        _VarToBit_149_7 = (_tempVariable_uint16_t >> 6) & 0x1;
        _VarToBit_149_8 = (_tempVariable_uint16_t >> 7) & 0x1;
        _VarToBit_149_9 = (_tempVariable_uint16_t >> 8) & 0x1;
        _VarToBit_149_10 = (_tempVariable_uint16_t >> 9) & 0x1;
        _VarToBit_149_11 = (_tempVariable_uint16_t >> 10) & 0x1;
        _VarToBit_149_12 = (_tempVariable_uint16_t >> 11) & 0x1;
        _VarToBit_149_13 = (_tempVariable_uint16_t >> 12) & 0x1;
        _VarToBit_149_14 = (_tempVariable_uint16_t >> 13) & 0x1;
        _VarToBit_149_15 = (_tempVariable_uint16_t >> 14) & 0x1;
        _VarToBit_149_16 = (_tempVariable_uint16_t >> 15) & 0x1;
        FLProgPin_PE8.digitalWrite(_VarToBit_149_14);
        FLProgPin_PE7.digitalWrite(_VarToBit_149_13);
        FLProgPin_PE6.digitalWrite(_VarToBit_149_12);
        FLProgPin_PE5.digitalWrite(_VarToBit_149_11);
        FLProgPin_PB1.digitalWrite(_VarToBit_149_10);
        FLProgPin_PB0.digitalWrite(_VarToBit_149_9);
        FLProgPin_PA11.digitalWrite(_VarToBit_149_8);
        FLProgPin_PA8.digitalWrite(_VarToBit_149_7);
        FLProgPin_PA7.digitalWrite(_VarToBit_149_6);
        FLProgPin_PA6.digitalWrite(_VarToBit_149_5);
        FLProgPin_PA3.digitalWrite(_VarToBit_149_4);
        FLProgPin_PA2.digitalWrite(_VarToBit_149_3);
        FLProgPin_PA1.digitalWrite(_VarToBit_149_2);
        FLProgPin_PA0.digitalWrite(_VarToBit_149_1);
        DI_block_165_outValue = (FLProgPin_PD3.digitalRead());
        DI_block_166_outValue = (FLProgPin_PD4.digitalRead());
        DI_block_167_outValue = (FLProgPin_PD7.digitalRead());
        DI_block_168_outValue = (FLProgPin_PD10.digitalRead());
        DI_block_169_outValue = (FLProgPin_PD11.digitalRead());
        DI_block_170_outValue = (FLProgPin_PD12.digitalRead());
        DI_block_171_outValue = (FLProgPin_PD13.digitalRead());
        DI_block_172_outValue = (FLProgPin_PD14.digitalRead());
        DI_block_173_outValue = (FLProgPin_PC8.digitalRead());
        DI_block_174_outValue = (FLProgPin_PC9.digitalRead());
        DI_block_175_outValue = (FLProgPin_PC13.digitalRead());
        DI_block_176_outValue = (FLProgPin_PE0.digitalRead());
        DI_block_177_outValue = (FLProgPin_PE1.digitalRead());
        DI_block_178_outValue = (FLProgPin_PE2.digitalRead());
        DI_block_179_outValue = (FLProgPin_PE3.digitalRead());
        DI_block_180_outValue = (FLProgPin_PE4.digitalRead());
        _BitsToVar148 = 0;
        if (DI_block_165_outValue) { _BitsToVar148 = _BitsToVar148 | 0x1; }
        if (DI_block_166_outValue) { _BitsToVar148 = _BitsToVar148 | 0x2; }
        if (DI_block_167_outValue) { _BitsToVar148 = _BitsToVar148 | 0x4; }
        if (DI_block_168_outValue) { _BitsToVar148 = _BitsToVar148 | 0x8; }
        if (DI_block_169_outValue) { _BitsToVar148 = _BitsToVar148 | 0x10; }
        if (DI_block_170_outValue) { _BitsToVar148 = _BitsToVar148 | 0x20; }
        if (DI_block_171_outValue) { _BitsToVar148 = _BitsToVar148 | 0x40; }
        if (DI_block_172_outValue) { _BitsToVar148 = _BitsToVar148 | 0x80; }
        if (DI_block_173_outValue) { _BitsToVar148 = _BitsToVar148 | 0x100; }
        if (DI_block_174_outValue) { _BitsToVar148 = _BitsToVar148 | 0x200; }
        if (DI_block_175_outValue) { _BitsToVar148 = _BitsToVar148 | 0x400; }
        if (DI_block_176_outValue) { _BitsToVar148 = _BitsToVar148 | 0x800; }
        if (DI_block_177_outValue) { _BitsToVar148 = _BitsToVar148 | 0x1000; }
        if (DI_block_178_outValue) { _BitsToVar148 = _BitsToVar148 | 0x2000; }
        if (DI_block_179_outValue) { _BitsToVar148 = _BitsToVar148 | 0x4000; }
        if (DI_block_180_outValue) { _BitsToVar148 = _BitsToVar148 | 0x8000; }
        _tempVariable_int16_t = _BitsToVar148;
        Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 12);
        _gtv39 = _BitsToVar148;
        _tempVariable_int16_t = _gtv40;
        Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 13);
        _tempVariable_int16_t = _gtv38;
        Modbus_144774688.saveIntegerByIndex(_tempVariable_int16_t, 4, 15);
        DI_block_181_outValue = (FLProgPin_PA15.digitalRead());
        _gtv47 = DI_block_181_outValue;
        // Web UI I/O readback after the normal I/O task.
        FLProgWebUiRuntime::publishBool(101, DI_block_165_outValue);
        FLProgWebUiRuntime::publishBool(102, DI_block_166_outValue);
        FLProgWebUiRuntime::publishBool(103, DI_block_167_outValue);
        FLProgWebUiRuntime::publishBool(104, DI_block_168_outValue);
        FLProgWebUiRuntime::publishBool(105, DI_block_169_outValue);
        FLProgWebUiRuntime::publishBool(106, DI_block_170_outValue);
        FLProgWebUiRuntime::publishBool(107, DI_block_171_outValue);
        FLProgWebUiRuntime::publishBool(108, DI_block_172_outValue);
        FLProgWebUiRuntime::publishBool(109, DI_block_173_outValue);
        FLProgWebUiRuntime::publishBool(110, DI_block_174_outValue);
        FLProgWebUiRuntime::publishBool(111, DI_block_175_outValue);
        FLProgWebUiRuntime::publishBool(112, DI_block_176_outValue);
        FLProgWebUiRuntime::publishBool(113, DI_block_177_outValue);
        FLProgWebUiRuntime::publishBool(114, DI_block_178_outValue);
        FLProgWebUiRuntime::publishBool(115, DI_block_179_outValue);
        FLProgWebUiRuntime::publishBool(116, DI_block_180_outValue);
        FLProgWebUiRuntime::publishInt(117, _gtv41);
        FLProgWebUiRuntime::publishInt(118, _gtv42);
        FLProgWebUiRuntime::publishInt(119, _gtv43);
        FLProgWebUiRuntime::publishInt(120, _gtv44);
        FLProgWebUiRuntime::publishBool(121, _VarToBit_149_1);
        FLProgWebUiRuntime::publishBool(122, _VarToBit_149_2);
        FLProgWebUiRuntime::publishBool(123, _VarToBit_149_3);
        FLProgWebUiRuntime::publishBool(124, _VarToBit_149_4);
        FLProgWebUiRuntime::publishBool(125, _VarToBit_149_5);
        FLProgWebUiRuntime::publishBool(126, _VarToBit_149_6);
        FLProgWebUiRuntime::publishBool(127, _VarToBit_149_7);
        FLProgWebUiRuntime::publishBool(128, _VarToBit_149_8);
        FLProgWebUiRuntime::publishBool(129, _VarToBit_149_9);
        FLProgWebUiRuntime::publishBool(130, _VarToBit_149_10);
        FLProgWebUiRuntime::publishBool(131, _VarToBit_149_11);
        FLProgWebUiRuntime::publishBool(132, _VarToBit_149_12);
        FLProgWebUiRuntime::publishBool(133, _VarToBit_149_13);
        FLProgWebUiRuntime::publishBool(134, _VarToBit_149_14);
        FLProgWebUiRuntime::publishInt(135, _gtv48);
        FLProgWebUiRuntime::publishInt(136, _gtv49);
    }
    //Плата:11
    //Наименование:Прикладная программа
    if (RT_HW_Base.shed.quick.num == 3)
    {
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 0) { _mux201 = 0; }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 1) { _mux201 = 0; }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 2) { _mux201 = (Modbus_144774688.readIntegerByIndex(4, 11)); }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 3) { _mux201 = _gtv24; }
        _gtv38 = _mux201;
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 0) { _mux199 = 0; }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 1) { _mux199 = 0; }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 2) { _mux199 = (Modbus_144774688.readIntegerByIndex(4, 10)); }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 3) { _mux199 = _gtv50; }
        _gtv14 = _mux199;
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 0) { _mux206 = 0; }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 1) { _mux206 = 0; }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 2) { _mux206 = (Modbus_144774688.readIntegerByIndex(4, 29)); }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 3) { _mux206 = _gtv57; }
        _gtv49 = _mux206;
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 0) { _mux205 = 0x5; }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 1) { _mux205 = 0x50; }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 2) { _mux205 = (Modbus_144774688.readIntegerByIndex(4, 28)); }
        if ((((ExternalEEPROM_252608257.readByte(4)))) == 3) { _mux205 = _gtv53; }
        _gtv48 = _mux205;
        if (profileWebOutputEnabled) {
            _gtv14 = profileWebDoMask & 0x3FFF;
            _gtv48 = profileWebAo[0];
            _gtv49 = profileWebAo[1];
        }
    }
    //Плата:12
    if (RT_HW_Base.shed.frdm.num == 1)
    {
        EN = !(0);
        NET_NUM = 1;
        PASSWORD = String("");
        flprogOtaUniversal.control(EN, (int32_t)NET_NUM, PASSWORD, String("1.0.4-PROFILE"));
        SUPPORTED = flprogOtaUniversal.supported();
        READY = flprogOtaUniversal.ready();
        BUSY = flprogOtaUniversal.busy();
        STATE = flprogOtaUniversal.state();
        ERR = flprogOtaUniversal.error();
        RX_BYTES = flprogOtaUniversal.receivedBytes();
        FAULT = (ERR != 0) || !SUPPORTED;
    }
}
bool SysPar_54877633_modbusMaster_isEnable_get()
{
    return Modbus_83290452.getEnable();
}
void SysPar_54877633_modbusMaster_isEnable_set(bool value)
{
    Modbus_83290452.setEnable(value);
}
bool SysPar_56202579_rasterDisplay_canWork_get()
{
    return oled_156902651.getEn();
}
void SysPar_56202579_rasterDisplay_canWork_set(bool value)
{
    oled_156902651.setEn(value);
}
uint32_t SysPar_22886449_wizNet_ip_get()
{
    return WiznetInterface_165513604.localIP();
}
void SysPar_22886449_wizNet_ip_set(uint32_t value)
{
    WiznetInterface_165513604.localIP(value);
}
uint32_t SysPar_22886449_wizNet_subnet_get()
{
    return WiznetInterface_165513604.subnet();
}
void SysPar_22886449_wizNet_subnet_set(uint32_t value)
{
    WiznetInterface_165513604.subnet(value);
}
uint32_t SysPar_22886449_wizNet_gateway_get()
{
    return WiznetInterface_165513604.gateway();
}
void SysPar_22886449_wizNet_gateway_set(uint32_t value)
{
    WiznetInterface_165513604.gateway(value);
}
uint32_t SysPar_22886449_wizNet_dns_get()
{
    return WiznetInterface_165513604.dns();
}
void SysPar_22886449_wizNet_dns_set(uint32_t value)
{
    WiznetInterface_165513604.dns(value);
}
int16_t SysPar_22886449_wizNet_status_get()
{
    return WiznetInterface_165513604.getStatus();
}
int16_t SysPar_22886449_wizNet_error_get()
{
    return WiznetInterface_165513604.getError();
}
bool SysPar_22886449_wizNet_redy_get()
{
    return WiznetInterface_165513604.isReady();
}
bool SysPar_192055330_taskManager_meander100ms_get()
{
    return (RT_HW_Base.shed.blink100);
}
uint32_t SysPar_192055330_taskManager_speedofCORE0InLoopCyclesSec_get()
{
    return TaskManager_Filter.vr;
}
uint32_t SysPar_192055330_taskManager_workTime_get()
{
    return (RT_HW_Base.shed.cntSec);
}
uint32_t SysPar_46186475_watch_currentTimeUNIX_get()
{
    return (FLProgWatch.timeUNIX);
}
void SysPar_46186475_watch_currentTimeUNIX_set(uint32_t value)
{
    FLProgWatch.checkUnixTime(value, 1);
}
bool SysPar_192055330_taskManager_meander500ms_get()
{
    return (RT_HW_Base.shed.blink500);
}
uint8_t SysPar_46186475_watch_currentDate_get()
{
    return (FLProgWatch.day);
}
void SysPar_46186475_watch_currentDate_set(uint8_t value)
{
    FLProgWatch.checkDigitalTime(FLProgWatch.hours, FLProgWatch.minutes, FLProgWatch.seconds, value, FLProgWatch.month, FLProgWatch.year);
}
uint8_t SysPar_46186475_watch_currentMonth_get()
{
    return (FLProgWatch.month);
}
void SysPar_46186475_watch_currentMonth_set(uint8_t value)
{
    FLProgWatch.checkDigitalTime(FLProgWatch.hours, FLProgWatch.minutes, FLProgWatch.seconds, FLProgWatch.day, value, FLProgWatch.year);
}
uint8_t SysPar_46186475_watch_currentYear2_get()
{
    return (FLProgWatch.year);
}
void SysPar_46186475_watch_currentYear2_set(uint8_t value)
{
    FLProgWatch.checkDigitalTime(FLProgWatch.hours, FLProgWatch.minutes, FLProgWatch.seconds, FLProgWatch.day, FLProgWatch.month, value);
}
uint8_t SysPar_46186475_watch_currentSec_get()
{
    return (FLProgWatch.seconds);
}
void SysPar_46186475_watch_currentSec_set(uint8_t value)
{
    FLProgWatch.checkDigitalTime(FLProgWatch.hours, FLProgWatch.minutes, value, FLProgWatch.day, FLProgWatch.month, FLProgWatch.year);
}
uint8_t SysPar_46186475_watch_currentMin_get()
{
    return (FLProgWatch.minutes);
}
void SysPar_46186475_watch_currentMin_set(uint8_t value)
{
    FLProgWatch.checkDigitalTime(FLProgWatch.hours, value, FLProgWatch.seconds, FLProgWatch.day, FLProgWatch.month, FLProgWatch.year);
}
uint8_t SysPar_46186475_watch_currentHour_get()
{
    return (FLProgWatch.hours);
}
void SysPar_46186475_watch_currentHour_set(uint8_t value)
{
    FLProgWatch.checkDigitalTime(value, FLProgWatch.minutes, FLProgWatch.seconds, FLProgWatch.day, FLProgWatch.month, FLProgWatch.year);
}
// clang-format off
//========================================================================================================================================
//++++ Начало функций отладки дисплея TFT ST7735 RGB (SPI1) ++++
//========================================================================================================================================
//----Код до инициализации устройства----
void oled_138862728_firstDebug(){
  auto &display = oled_138862728; (void) display;
  auto &d = oled_138862728_chip._device; (void)d;
  auto &bus = *d.bus; (void)bus;
  uint8_t num = oled_138862728_chip.getNum(); (void)num;
  // --- Начало отладочного кода
  
}
//----Код после инициализации устройства----
void oled_138862728_secondDebug(){
  auto &display = oled_138862728; (void) display;
  auto &d = oled_138862728_chip._device; (void)d;
  auto &bus = *d.bus; (void)bus;
  uint8_t num = oled_138862728_chip.getNum(); (void)num;
  // --- Начало отладочного кода
  
}
//========================================================================================================================================
//++++ Конец функций отладки дисплея TFT ST7735 RGB (SPI1)  ++++
//========================================================================================================================================
// clang-format on
// clang-format off
//========================================================================================================================================
//++++ Начало функций отладки дисплея OLED SH1107 MONO (I2C0) ++++
//========================================================================================================================================
//----Код до инициализации устройства----
void oled_156902651_firstDebug(){
  auto &display = oled_156902651; (void) display;
  auto &d = oled_156902651_chip._device; (void)d;
  auto &bus = *d.bus; (void)bus;
  uint8_t num = oled_156902651_chip.getNum(); (void)num;
  // --- Начало отладочного кода
  
}
//----Код после инициализации устройства----
void oled_156902651_secondDebug(){
  auto &display = oled_156902651; (void) display;
  auto &d = oled_156902651_chip._device; (void)d;
  auto &bus = *d.bus; (void)bus;
  uint8_t num = oled_156902651_chip.getNum(); (void)num;
  // --- Начало отладочного кода
  
}
//========================================================================================================================================
//++++ Конец функций отладки дисплея OLED SH1107 MONO (I2C0)  ++++
//========================================================================================================================================
// clang-format on
