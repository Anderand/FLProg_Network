/*
 * FLProg_Network — flprogSpiBackend.h
 * Назначение: Платформенно-зависимый SPI backend для Wiznet/W5500.
 *
 * Архитектурные заметки:
 * - Выбирает SPI/SPI1/HSPI и проверяет доступность пользовательских пинов.
 * - RP2040 core-ы различаются: setSCK/setRX/setTX разрешены только если API реально существует.
 * - beginTransaction/endTransaction обязаны держать CS и SPI transaction симметрично.
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

#include <Arduino.h>
#include <SPI.h>

// -----------------------------------------------------------------------------
// FLProg_Network v0.4.5 - абстракция SPI backend.
//
// Политика владения и аппаратное выполнение намеренно разделены:
//   FLProgSpiArbiter -> владение / неблокирующее откладывание / статистика
//   FLProgSpiBackend -> физические операции begin/CS/transfer/end
//
// Стандартный Arduino backend сохраняет FLProg_Network самостоятельной. Адаптер
// RT_HW_Base шаблонный и не создаёт зависимости, пока пользователь сам не
// создаст его с RT_HW_Base и RT_HW_STRUCT_SPI_DEV.
// -----------------------------------------------------------------------------

#ifndef FLPROG_SPI_STATUS_OK
#define FLPROG_SPI_STATUS_OK          0
#define FLPROG_SPI_STATUS_BUSY        1
#define FLPROG_SPI_STATUS_UNAVAILABLE 2
#define FLPROG_SPI_STATUS_PIN_ERROR   3
#endif

#define FLPROG_SPI_BACKEND_ARDUINO 0
#define FLPROG_SPI_BACKEND_RT_HW   1
#define FLPROG_SPI_BACKEND_CUSTOM  2

typedef bool (*FLProgSpiBusyProbeCallback)(uint8_t bus, void *context);

class FLProgSpiBackend
{
public:
    virtual ~FLProgSpiBackend() {}

    virtual void configure(
        uint8_t requestedBus,
        int requestedCs,
        uint32_t speed) = 0;

    virtual bool begin() = 0;

    // beginTransaction() отвечает и за настройку SPI-транзакции, и за установку CS.
    // endTransaction() отвечает за снятие CS и завершение транзакции.
    virtual bool beginTransaction() = 0;
    virtual void endTransaction() = 0;
    virtual uint8_t transfer(uint8_t value) = 0;

    virtual uint8_t bus() const = 0;
    virtual int cs() const = 0;
    virtual bool busAvailable() const = 0;
    virtual bool pinsSupported() const = 0;
    virtual uint8_t kind() const = 0;
    virtual uint8_t status() const = 0;
};

class FLProgArduinoSpiBackend : public FLProgSpiBackend
{
public:
    FLProgArduinoSpiBackend();

    virtual void configure(
        uint8_t requestedBus,
        int requestedCs,
        uint32_t speed);

    virtual bool begin();
    virtual bool beginTransaction();
    virtual void endTransaction();
    virtual uint8_t transfer(uint8_t value);

    virtual uint8_t bus() const { return _bus; }
    virtual int cs() const { return _cs; }
    virtual bool busAvailable() const;
    virtual bool pinsSupported() const;
    virtual uint8_t kind() const { return FLPROG_SPI_BACKEND_ARDUINO; }
    virtual uint8_t status() const { return _status; }

    void setSpiObject(SPIClass *object) { _spiObject = object; }
    void clearSpiObject() { _spiObject = nullptr; }
    SPIClass *spiObject();
    bool hasExplicitSpiObject() const { return _spiObject != nullptr; }

    void setPins(int sck, int miso, int mosi);
    void clearPins();
    bool customPins() const { return _customPins; }

private:
    SPIClass *resolveSpiObject();

    uint8_t _bus = 0;
    int _cs = -1;
    uint32_t _speed = 14000000UL;
    uint8_t _status = FLPROG_SPI_STATUS_OK;

    SPIClass *_spiObject = nullptr;
    int _sck = -1;
    int _miso = -1;
    int _mosi = -1;
    bool _customPins = false;
    bool _transactionOpen = false;
};

// -----------------------------------------------------------------------------
// Адаптер RT_HW_Base.
//
// Класс намеренно НЕ подключает заголовки RT_HW_Base. TRtHwBase и
// TDevice — шаблонные типы, поэтому адаптер создаётся только в
// проектах, где RT_HW_Base уже доступна.
//
// Требуемый API RT_HW_Base (подтверждён в Flprog_Ethernet):
//   getBusETH0(), getCsETH0()
//   spiInitDevice(device)
//   spiSetBusy(bus), spiClearBusy(bus)
//   spiBeginTransaction(device), spiEndTransaction(device)
//   spiBeginCS(device), spiEndCS(device)
//   spiTransfer(value, bus)
//
// В этих вызовах Flprog_Ethernet не показывает читаемой проверки Busy.
// Поэтому предусмотрен необязательный callback проверки Busy. Если в RT_HW_Base появится
// spiIsBusy()/spiTryLock(), его можно привязать здесь, и FLProg_Network отложит
// транзакцию, если шина занята внешним устройством.
// -----------------------------------------------------------------------------

template <typename TRtHwBase, typename TDevice>
class FLProgRtHwSpiBackend : public FLProgSpiBackend {
public:
    explicit FLProgRtHwSpiBackend(TRtHwBase &base) : _base(&base) {}
//=================================================================================================
//                         1.Пассивная настройка, без GPIO/SPI-действий
// custom=1 нужен прежнему spiInitDevice(). Частота передаётся библиотекой сети.
// Fallback относится к первому ETH-профилю; другим интерфейсам передавать bus/CS явно.
// Горячее переназначение bus/CS исключено; частоту можно менять между сессиями.
//=================================================================================================
    void configure(uint8_t requestedBus,int requestedCs,uint32_t speed) override{
        if(!_base){_status=FLPROG_SPI_STATUS_UNAVAILABLE; return;}
        uint8_t bus=(requestedBus==255) ? _base->getETH_bus(0) : requestedBus;
        //-----------------------------------------------------------------------------------------
        //                         Доработка EIS 05.11.2026 v.02
        // Внешняя virtual-сигнатура int сохранена для всех прежних реализаций FLProgSpiBackend.
        // Только на этой границе принимаем старое -1 и принятое в RT_HW значение 255:
        // оба означают «CS не задан явно, взять из первого Ethernet-профиля».
        // Другие отрицательные значения и числа >254 не являются номерами пинов RT_HW.
        // Сначала проверяем int, затем сужаем: 256 не должен превратиться в реальный пин 0.
        //-----------------------------------------------------------------------------------------
        int resolvedCs=(requestedCs==-1 || requestedCs==255) ? _base->getETH_cs(0) : requestedCs;
        if(resolvedCs<0 || resolvedCs>=255){
            _status=FLPROG_SPI_STATUS_PIN_ERROR; return;
        }
        uint8_t cs=uint8_t(resolvedCs);           //--Внутренний формат RT_HW: пин 0..254;
        if(!_base->checkPinDOT(cs)){
            _status=FLPROG_SPI_STATUS_PIN_ERROR; return;
        }
        if(!_base->spiCheckBus(bus)){_status=FLPROG_SPI_STATUS_UNAVAILABLE; return;}
        if(_device.sessionOpen){_status=FLPROG_SPI_STATUS_BUSY; return;}
        if(_device.status==1 && (_device.bus!=bus || _device.cs!=cs)){
            _status=FLPROG_SPI_STATUS_UNAVAILABLE; return; //--Маршрут после запуска не меняем;
        }
        _device.bus=bus; _device.cs=cs; _device.speed=speed;
        _device.custom=1;                         //--Только поля прежнего дескриптора RT_HW;
        _status=FLPROG_SPI_STATUS_OK;
    }
//=================================================================================================
//                         2.Инициализация существующим методом RT_HW
// Прежний backend возвращал успех без проверки результата spiInitDevice().
// status/err/codeErr принадлежат RT_HW; собственного признака begun не добавляем.
//=================================================================================================
    bool begin() override{
        //--Не терять отказ последнего configure(): иначе можно запустить прежний маршрут.
        if(_status==FLPROG_SPI_STATUS_PIN_ERROR || _status==FLPROG_SPI_STATUS_UNAVAILABLE){return false;}
        if(!_base || !_device.custom || !_base->spiCheckBus(_device.bus)){
            _status=FLPROG_SPI_STATUS_UNAVAILABLE; return false;
        }
        if(!_base->checkPinDOT(_device.cs)){_status=FLPROG_SPI_STATUS_PIN_ERROR; return false;}
        if(_base->spiGetBusy(_device.bus)){_status=FLPROG_SPI_STATUS_BUSY; return false;}
        _base->spiInitDevice(_device);            //--Физическую настройку выполняет RT_HW;
        if(_device.status!=1 || _device.err || _device.codeErr){
            _status=(_device.codeErr==152) ? FLPROG_SPI_STATUS_PIN_ERROR : FLPROG_SPI_STATUS_UNAVAILABLE;
            return false;
        }
        _status=FLPROG_SPI_STATUS_OK; return true;
    }
//=================================================================================================
//                         3.Готовая сессия вместо ручного lock/CS/transaction
// Возврат прежнего RT_HW spiBeginSession(): 1=открыто, 0=не открыто.
// После проверки устройства/шины отказ открытия означает занятый ресурс.
// _status — только прежний результат API сети, не копия SPI-состояния.
//=================================================================================================
    bool beginTransaction() override{
        if(!_base || !_device.custom || _device.status!=1 || !_base->spiCheckBus(_device.bus)){
            _status=FLPROG_SPI_STATUS_UNAVAILABLE; return false;
        }
        //--Сохранённый callback прежнего API: внешняя проверка занятости, не управление SPI.
        if(_busyProbe && _busyProbe(_device.bus,_busyProbeContext)){
            _status=FLPROG_SPI_STATUS_BUSY; return false;
        }
        uint8_t opened=_base->spiBeginSession(_device);
        _status=opened ? FLPROG_SPI_STATUS_OK : FLPROG_SPI_STATUS_BUSY;
        return opened!=0;
    }
    void endTransaction() override{
        if(_base){_base->spiEndSession(_device);} //--RT_HW закрывает CS/transaction и освобождает шину;
    }
    uint8_t transfer(uint8_t value) override{
        if(!_base || !_device.sessionOpen){_status=FLPROG_SPI_STATUS_UNAVAILABLE; return 0xff;}
        return _base->spiLL_Transfer(_device,value); //--Не device-overload с повторным lock;
    }
//=================================================================================================
//                         4.Прежний интерфейс совместимости
// Сигнатуры bool заданы FLProgSpiBackend, а тип callback — прежним typedef.
// Имена device()/setBusyProbe() сохраняются для уже написанных проектов.
// _busyHeld и _transactionOpen удалены: sessionOpen уже есть в RT_HW-устройстве.
//=================================================================================================
    uint8_t bus() const override {return _device.bus;}
    // На выходе прежнего virtual int API сохраняем -1: старые потребители проверяют cs()<0.
    // Дескриптор RT_HW при этом хранит uint8_t; второй копии состояния CS здесь нет.
    int cs() const override {return _device.custom ? int(_device.cs) : -1;}
    bool busAvailable() const override {return _base && _device.custom && _base->spiCheckBus(_device.bus);}
    bool pinsSupported() const override {return _base && _device.custom && _base->checkPinDOT(_device.cs);}
    uint8_t kind() const override {return FLPROG_SPI_BACKEND_RT_HW;}
    uint8_t status() const override {return _status;}
    TDevice &device(){return _device;}
    const TDevice &device() const {return _device;}
    void setBusyProbe(FLProgSpiBusyProbeCallback callback,void *context=nullptr){
        _busyProbe=callback; _busyProbeContext=context;
    }
private:
    TRtHwBase *_base=nullptr;
    TDevice _device{};
    FLProgSpiBusyProbeCallback _busyProbe=nullptr;
    void *_busyProbeContext=nullptr;
    uint8_t _status=FLPROG_SPI_STATUS_UNAVAILABLE; //--Результат совместимого сетевого API;
};

// Удобный макрос для Arduino-проектов C++11.
#define FLPROG_DECLARE_RT_HW_SPI_BACKEND(name, baseObject, deviceType) \
    FLProgRtHwSpiBackend<decltype(baseObject), deviceType> name(baseObject)
