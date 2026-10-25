/*
 * FLE4D-30MT W5500 + DHCP + STM32 OTA diagnostic test.
 *
 * Build only with the FLProg FLE4D_30MT_OTA profile. The application must be
 * linked at 0x08010000; install the matching bootloader at 0x08000000 via SWD.
 * UART6: TX=PC6, RX=PC7, 115200 baud.
 */
#include <RT_HW_BASE.h>
#include <flprogUtilites.h>
#include <flprogNetwork.h>
#include <new>
#include <malloc.h>
#include <malloc.h>
#include <malloc.h>
#include "baseline_context.h"
#include "fle4d_webui_test_descriptor.h"
#include <adapters/FLProgWebUiFlprogNetworkPagedHttp.h>
#include <flprogOtaUniversalBlock.h>

#define TEST_FIRMWARE_VERSION "1.0.10-LOAD"

#ifndef FLPROG_W5500_SPI_BUS
#define FLPROG_W5500_SPI_BUS 0
#endif
#ifndef FLPROG_W5500_SCK_PIN
#define FLPROG_W5500_SCK_PIN PB13
#endif
#ifndef FLPROG_W5500_MISO_PIN
#define FLPROG_W5500_MISO_PIN PB14
#endif
#ifndef FLPROG_W5500_MOSI_PIN
#define FLPROG_W5500_MOSI_PIN PB15
#endif
#ifndef FLPROG_W5500_CS_PIN
#define FLPROG_W5500_CS_PIN PB12
#endif

// Empty password intentionally checks that the OTA service accepts no key.
static const char kOtaPassword[] = "";
static const uint16_t kOtaPort = 3233;
static const uint32_t kReportPeriodMs = 1000UL;

// Construct network services only after UART6 is ready. If initialization
// faults, the serial log will show whether setup() and the constructors ran.
alignas(FLProgNetworkInterface) static uint8_t networkStorage[sizeof(FLProgNetworkInterface)];
FLProgOtaUniversalBlock flprogOtaUniversal;
bool EN=true, SUPPORTED=false, READY=false, BUSY=false, FAULT=false;
int NET_NUM=1;
String PASSWORD="", VERSION="1.0.10-LOAD";
long STATE=0, ERR=0, RX_BYTES=0;
static FLProgNetworkInterface *network = nullptr;
#define FLPROG_WIZNET_INTERFACE1 (*network)
static uint32_t lastReportAt = 0;
static uint32_t sequence = 0;


static void printStatus()
{
    Serial6.print(F(TEST_FIRMWARE_VERSION " #")); Serial6.print(sequence++);
    Serial6.print(F(" ms=")); Serial6.print(millis());
    Serial6.print(F(" hw=")); Serial6.print(network->hardwareStatus());
    Serial6.print(F(" spi=")); Serial6.print(network->spiStatus());
    Serial6.print(F(" spiTx=")); Serial6.print(network->spiTransactionCount());
    Serial6.print(F(" link=")); Serial6.print(network->linkStatus());
    Serial6.print(F(" dhcp=")); Serial6.print(network->dhcpState());
    Serial6.print('/'); Serial6.print(network->dhcpError());
    Serial6.print(F(" dhcpServer=")); Serial6.print(network->dhcpServer());
    Serial6.print(F(" ethReady=")); Serial6.print(network->wiznetIsReady() ? 1 : 0);
    Serial6.print(F(" ip=")); Serial6.print(network->wiznetIP());
    Serial6.print(F(" net=")); Serial6.print(network->getStatus());
    Serial6.print('/'); Serial6.print(network->getError());
    Serial6.print(F(" SUPPORTED=")); Serial6.print(SUPPORTED);
    Serial6.print(F(" READY=")); Serial6.print(READY);
    Serial6.print(F(" BUSY=")); Serial6.print(BUSY);
    Serial6.print(F(" FAULT=")); Serial6.print(FAULT);
    Serial6.print(F(" STATE=")); Serial6.print(STATE);
    Serial6.print(F(" ERR=")); Serial6.print(ERR);
    Serial6.print(F(" RX_BYTES=")); Serial6.print(RX_BYTES);
    const struct mallinfo heap = mallinfo();
    Serial6.print(F(" HEAP_USED=")); Serial6.print(heap.uordblks);
    Serial6.print(F(" HEAP_ARENA_FREE=")); Serial6.print(heap.fordblks);
    Serial6.print(F(" HEAP_FREE_BLOCKS=")); Serial6.println(heap.ordblks);

}

namespace ui = flprog_webui_fle4d_webui_test;
static bool testRunning = false;
static uint32_t commandAt = 0;
static int32_t commandCount = 0;
static uint8_t slot(const char *id) { return (uint8_t)ui::model.indexOf(id); }
static void testCommands() {
    float number;
    char text[64];
    bool run;
    if (ui::model.takeFloat(slot("setpoint"), number)) {
        ui::model.publishFloat(slot("actual"), number);
        Serial6.print(F("WEB command: setpoint=")); Serial6.println(number);
    }
    if (ui::model.takeText(slot("title"), text, sizeof(text))) {
        Serial6.print(F("WEB command: title=")); Serial6.println(text);
    }
    if (ui::model.takeBool(slot("run"), run) && run && !commandAt) {
        commandAt = millis();
        ui::model.publishBool(slot("busy"), true);
        ui::model.publishBool(slot("result"), false);
        Serial6.println(F("WEB command: start RAM-only test, 5 seconds"));
    }
    if (commandAt && millis() - commandAt >= 5000) {
        commandAt = 0; testRunning = !testRunning;
        ui::model.publishBool(slot("running"), testRunning);
        ui::model.publishBool(slot("busy"), false);
        ui::model.publishBool(slot("result"), true);
        ui::model.publishInt(slot("commands"), ++commandCount);
        Serial6.println(F("WEB command: completed; no physical outputs changed"));
    }
    ui::model.publishInt(slot("uptime"), (int32_t)(millis()/1000));
}

void setup()
{
    RT_HW_Base.uartSetPins(PC7, PC6, 6);
    Serial6.setTx(PC6);
    Serial6.setRx(PC7);
    Serial6.begin(115200);
    delay(200);
    Serial6.println();
    Serial6.println(F("FLE4D W5500 + DHCP + OTA test"));
    Serial6.println(F("FIRMWARE VERSION: " TEST_FIRMWARE_VERSION));
    Serial6.println(F("SPI0: SCK=PB13 MISO=PB14 MOSI=PB15 CS=PB12"));
    Serial6.println(F("UART6: TX=PC6 RX=PC7 115200; OTA TCP port=3233; password=empty"));
    Serial6.println(F("BOOT 1: UART ready; before network constructors"));

    network = new (networkStorage) FLProgNetworkInterface();

    Serial6.println(F("BOOT 2: network constructors complete"));


    // Match the physical PLC pin routing used by the working pr4 diagnostic.
    RT_HW_Base.spiSetPins(FLPROG_W5500_SCK_PIN,
                          FLPROG_W5500_MISO_PIN,
                          FLPROG_W5500_MOSI_PIN,
                          FLPROG_W5500_SPI_BUS);
    RT_HW_Base.spiBegin(FLPROG_W5500_SPI_BUS);

    network->networkMode(FLPROG_NETWORK_MODE_ETHERNET);
    network->wiznetMode(true);
    network->rmiiMode(false);
    network->setSpiBus(FLPROG_W5500_SPI_BUS);
    network->setPinCs(FLPROG_W5500_CS_PIN);
    network->setSpiPins(FLPROG_W5500_SCK_PIN,
                       FLPROG_W5500_MISO_PIN,
                       FLPROG_W5500_MOSI_PIN);
    network->mac(0x78, 0xAC, 0xC0, 0x40, 0xA3, 0x3C);
    network->dhcpMode(true);
    network->workMode(true);

    // Exact setup code from the v0.4 user block.
#if defined(ARDUINO_ARCH_STM32)
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
    Serial6.println(F("MODEL: " FLPROG_OTA_MODEL));
    Serial6.println(F("OTA block v0.4; auto restart enabled"));
    ui::configure();
    ui::model.publishFloat(slot("setpoint"), 25.0f);
    ui::model.publishFloat(slot("actual"), 25.0f);
    ui::model.publishText(slot("title"), "FLE4D test");
    static FLProgWebUiFlprogNetworkPagedHttp web(ui::model, ui::widgets, ui::widgetCount, ui::pages, ui::pageCount, ui::theme);
    Serial6.print(F("WEB begin=")); Serial6.println(web.begin(*network, 80));
    Serial6.println(F("WebUI 1.7.0 HTTP=80; RAM-only demo, no output control"));
    network->connect();
}

void loop()
{
    network->pool();
    testCommands();
    // Exact loop code from the v0.4 user block.
flprogOtaUniversal.control(EN, (int32_t)NET_NUM, PASSWORD, VERSION);
SUPPORTED = flprogOtaUniversal.supported();
READY = flprogOtaUniversal.ready();
BUSY = flprogOtaUniversal.busy();
STATE = flprogOtaUniversal.state();
ERR = flprogOtaUniversal.error();
RX_BYTES = flprogOtaUniversal.receivedBytes();
FAULT = (ERR != 0) || !SUPPORTED;

    const uint32_t now = millis();
    if (now - lastReportAt >= kReportPeriodMs)
    {
        lastReportAt = now;
        printStatus();
    }
}
