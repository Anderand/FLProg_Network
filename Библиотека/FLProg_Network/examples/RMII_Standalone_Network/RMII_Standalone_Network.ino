// FLProg_Network — отдельный RMII-интерфейс. Только демонстрация API.
// Для физической работы требуется MCU с Ethernet MAC и поддерживаемый PHY.
// Для ESP32 проверьте поддержку EMAC выбранной SoC, распиновку платы и тактирование.
// STM32Ethernet использует поддерживаемую core/variant конфигурацию PHY.
#include <flprogNetwork.h>

FLProgRmiiInterface RmiiNetwork;

void setup()
{
    // NET NUM = 3. Номер уникален для всей программы FLProg.
    flprogNetworkDevices.registerDevice(3, RmiiNetwork);

    RmiiNetwork.setPhyAddress(0);
    RmiiNetwork.setMdcPin(23);
    RmiiNetwork.setMdioPin(18);
    RmiiNetwork.setPowerPin(-1); // отсутствует, для платы с отдельным EN укажите его
    RmiiNetwork.setResetPin(-1); // отсутствует, для платы с отдельным RESET укажите его
    RmiiNetwork.setClockMode(FLPROG_RMII_CLOCK_GPIO0_IN);
    RmiiNetwork.setHostname("flprog-rmii");
    RmiiNetwork.setDhcp();

    // В других блоках: FLProgNetworkInterface* base =
    //     flprogNetworkDevices.getDevice(3);
    // Либо строго RMII: flprogNetworkDevices.getRmii(3);
}

void loop()
{
    RmiiNetwork.pool();
}
