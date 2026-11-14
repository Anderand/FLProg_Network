//==================================================================================================
//                                  Доработка EIS 05.11.2026 v.04                                   
//==================================================================================================
/*
 * FLProg_Network — flprogEthernet.h
 * Назначение: Основной Ethernet-header, RT_HW-интеграция и legacy TCP/UDP-адаптеры.
 *
 * Архитектурные заметки:
 * - Старый проект может по-прежнему подключать только <flprogEthernet.h>.
 * - Внутри экспортируются новые FLProg_Network типы и тонкие legacy-адаптеры.
 * - Старая raw-socket архитектура здесь не восстанавливается.
 *
 * Комментарии описывают контракт и причины решений; рабочую логику файла не дублируют.
 * Расширенный контракт сопровождения:
 * - Это публичная или межмодульная декларация: комментарии описывают владельца состояния и допустимый порядок вызовов.
 * - Конфигурация применяется до начала работы; runtime-методы обслуживаются из общего network.pool().
 * - При изменении API учитывать legacy generated-код и frozen API level 10006.
 * Extended maintenance contract:
 * - This declaration defines a public or cross-module boundary; document state ownership and call order here.
 * - Apply configuration before start; service runtime through the shared network.pool() lifecycle.
 * - Any API change must account for legacy generated code and frozen API level 10006.
 */
#pragma once

//==================================================================================================
//                                  Доработка EIS 05.11.2026 v.04
// ОСНОВНОЙ ЗАГОЛОВОК Ethernet: #include <flprogEthernet.h> (кавычки также допустимы).
// Весь бывший фасад flprogRtHwEthernet.h теперь находится НИЖЕ В ЭТОМ ФАЙЛЕ.
// Нет цикла header -> optional-header -> header и нет зависимости от порядка include.
// RT_HW подключён явно. Автопривязка выполняется первым pool, не во время include/setup.
// RT_HW — основной путь этого контроллерного варианта. Для прежнего Arduino SPI можно
// явно вызвать useArduinoWiznetSpiBackend() у нужного объекта до первого pool.
// FLPROG_NETWORK_RT_HW_AUTO=0 отключает регистрацию в соответствующем TU; для отключения
// во всём приложении макрос должен задаваться всем TU. Явный выбор backend надёжнее.
//==================================================================================================
#ifndef FLPROG_NETWORK_RT_HW_AUTO
  #define FLPROG_NETWORK_RT_HW_AUTO 1
#endif

// FLProg_Ethernet source-compatibility umbrella for FLProg_Network.
// Existing generated projects may keep: #include <flprogEthernet.h>
// All networking is implemented by FLProg_Network/A3; the legacy raw socket
// implementation is not restored.

#include <Arduino.h>
// RT_HW exists only in FLProg builds with the RT_HW package. The generic
// Wi-Fi / Arduino SPI profiles must not depend on its headers.
#ifndef FLPROG_NETWORK_HAS_RT_HW_BASE
# if defined(__has_include)
#  if __has_include(<RT_HW_BASE.h>)
#   define FLPROG_NETWORK_HAS_RT_HW_BASE 1
#  else
#   define FLPROG_NETWORK_HAS_RT_HW_BASE 0
#  endif
# else
#  define FLPROG_NETWORK_HAS_RT_HW_BASE 0
# endif
#endif
#if FLPROG_NETWORK_HAS_RT_HW_BASE
#include <RT_HW_BASE.h>
#endif
// EIS v.04: прямой include Utilities из umbrella убран как избыточный.
#include "flprogUtilites.h"
// Пока библиотека ещё нужна legacy TCP/UDP-адаптерам (константы совместимости).
// Удаление этой строки НЕ означает устранения зависимости всего FLProg_Network.
#include "flprogNetwork.h"
#include "abstract/flprogAbstractTcpInterface.h"
#include "tcp/flprogEthernetClient.h"
#include "tcp/flprogEthernetServer.h"
#include "udp/flprogUdp.h"
#include "udp/flprogDns.h"

inline uint8_t ethBindRtHw(uint8_t num,FLProgWiznetInterface &net,FLProgSpiBackend &backend){
    if(net.networkMode()!=FLPROG_NETWORK_MODE_ETHERNET || !net.wiznetMode() || net.rmiiMode()
       || backend.kind()!=FLPROG_SPI_BACKEND_RT_HW){return 0;}
    if(net.wiznetHardware().isInit()){return 0;} //--Не переключать backend работающего чипа;
    auto result=flprogNetworkDevices.registerDevice(num,net);
    if(result!=FLPROG_NETWORK_DEVICE_OK && result!=FLPROG_NETWORK_DEVICE_ALREADY_REGISTERED){return 0;}
    if(net.wiznetHardware().spiBackend()!=&backend){net.setWiznetSpiBackend(&backend);}
    return 1;
}
//=================================================================================================
//                         2.Частота по num, только для отдельного SPI Ethernet
// Реестр общий; RMII/Wi-Fi и комбинированные режимы не получают фиктивный Wiznet.
// Одного networkMode()==ETHERNET недостаточно: проверяются wiznetMode()/rmiiMode().
// Вызывать из loop между pool(). Нет очереди для ISR/RTOS/DMA-контекстов.
//=================================================================================================
inline uint8_t ethSetSpiSpeed(uint8_t num,uint32_t hz){
    auto *net=flprogNetworkDevices.getDevice(num);
    if(!net || net->networkMode()!=FLPROG_NETWORK_MODE_ETHERNET || !net->wiznetMode() || net->rmiiMode()){return 0;}
    return net->wiznetHardware().setSpiSpeedRuntime(hz);
}
//=================================================================================================
//                         3.Выдержка запуска по num, до первого pool()/init()
// Без GPIO RESET работает существующая RC-цепь модуля; время задаёт профиль.
//=================================================================================================
inline uint8_t ethSetStartupDelay(uint8_t num,uint32_t ms){
    auto *net=flprogNetworkDevices.getDevice(num);
    if(!net || net->networkMode()!=FLPROG_NETWORK_MODE_ETHERNET || !net->wiznetMode() || net->rmiiMode()){return 0;}
    return net->wiznetHardware().setStartupDelayMs(ms);
}

//=================================================================================================
//                         4.Запись RESET через существующий GPIO API RT_HW
// Writer вызывается лишь дважды при старте. Локальный GPIO-дескриптор не требует
// отдельного реестра или времени жизни после вызова; настройка/запись остаются в RT_HW.
// uint8_t=1 пин настроен, 0 ошибка. Никаких прямых digitalWrite/pinMode в этом мосте.
//=================================================================================================
// Новый callback использует uint8_t/255 на всём пути до GPIO API RT_HW.
// 255 — отсутствие пина, поэтому до pinDigitalWrite он никогда не доходит.
#if FLPROG_NETWORK_HAS_RT_HW_BASE
inline uint8_t ethRtHwResetWrite(uint8_t pin,uint8_t level){
    if(pin==255 || !RT_HW_Base.checkPinDOT(pin)){return 0;}
    RT_HW_PIN_DIR_ID id{};
    id.mode='N';
    RT_HW_Base.pinDigitalWrite(id,pin,level);
    return id.dir>=1 && id.dir<=4;
}
//=================================================================================================
//                         5.Владелец RESET по num, только до первого pool()
// MANAGED: GPIO будет управляться библиотекой через RT_HW.
// EXTERNAL/NONE: пин не настраивается и не переключается.
//=================================================================================================
// Единое правило новых аппаратных API: пин uint8_t, отсутствие пина 255.
// NONE/EXTERNAL можно вызвать без pin. MANAGED без назначенного пина вернёт 0.
// Не передавать произвольный int через неявное сужение: например, 256 станет 0 ещё
// ДО входа в эту функцию. Проверять диапазон внешних данных до приведения к uint8_t.
inline uint8_t ethSetReset(uint8_t num,uint8_t mode,uint8_t pin=255,
                           uint8_t activeLevel=0,uint32_t holdUs=2000){
    auto *net=flprogNetworkDevices.getDevice(num);
    if(!net || net->networkMode()!=FLPROG_NETWORK_MODE_ETHERNET || !net->wiznetMode() || net->rmiiMode()){return 0;}
    if(mode==FLPROG_ETH_RESET_MANAGED &&
       (pin==255 || !RT_HW_Base.checkPinDOT(pin))){return 0;}
    return net->wiznetHardware().setResetMode(mode,pin,activeLevel,holdUs,
        mode==FLPROG_ETH_RESET_MANAGED ? ethRtHwResetWrite : nullptr);
}

#endif // FLPROG_NETWORK_HAS_RT_HW_BASE

//==================================================================================================
//                                  Доработка EIS 05.11.2026 v.04
// Основной flprogEthernet.h содержит автоматическую RT_HW-интеграцию для SPI Wiznet.
// В скетче больше нет backend-объекта, bind и configOk. Явный Arduino/custom backend
// уважается; RMII/Wi-Fi не получают фиктивный SPI. Явный useArduinoWiznetSpiBackend сохраняет Arduino-путь.
//==================================================================================================
#if FLPROG_NETWORK_COMPILE_WIRED && !FLPROG_NETWORK_PROFILE_WIFI_ONLY && FLPROG_NETWORK_RT_HW_AUTO && FLPROG_NETWORK_HAS_RT_HW_BASE
#include <new>
inline FLProgSpiBackend *flprogRtHwBackendForPool(){
    using Backend=FLProgRtHwSpiBackend<decltype(RT_HW_Base),RT_HW_STRUCT_SPI_DEV>;
    // Фиксированное место для существующих backend, без heap и отдельного реестра владельцев.
    // Каждый первый pool получает свой объект. Указатель хранит сам сетевой объект.
    // Placement new только конструирует backend в выровненной статической памяти;
    // GPIO/SPI не запускаются. SPI-сессия по-прежнему принадлежит RT_HW_STRUCT_SPI_DEV.
    alignas(Backend) static uint8_t memory[FLPROG_NETWORK_MAX_DEVICES][sizeof(Backend)];
    static uint8_t used=0;
    if(used>=FLPROG_NETWORK_MAX_DEVICES){return nullptr;}
    auto *backend=new (memory[used]) Backend(RT_HW_Base);
    ++used; return backend;
    // Объекты сети должны жить всё приложение. Слоты намеренно не переиспользуются после
    // удаления/копирования объектов; горячее создание интерфейсов — отдельная будущая задача.
}
inline uint8_t flprogRtHwRegisterPoolFactory(){
    return FLProgNetworkInterface::setWiznetPoolFactory(flprogRtHwBackendForPool,ethRtHwResetWrite);
}
namespace {
    // Только регистрация функций до setup. Backend создаётся не здесь, а первым pool.
    // Повторное включение header в другой TU регистрирует ту же inline-функцию идемпотентно.
    const uint8_t flprogRtHwPoolFactoryRegistered=flprogRtHwRegisterPoolFactory();
}
#endif

