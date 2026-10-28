# Исходники MQTT v0.3

`build_mqtt_blocks.py --output <Basic>` создаёт три базовых UBI.
`build_mqtt_professional_blocks.py --basic <Basic> --output <Professional>`
создаёт три профессиональных UBI из тех же определений. Нужен Python 3 и
соседний `Исходники/WebUI/tools/build_start_block.py` из общего комплекта.

`test_mqtt.py --library <FLProg_Network> --output <рабочая папка> --compiler <zig.exe>`
компилирует полный класс MQTT со стендом времени/транспорта/отказа RAM.
performance_tests.cpp должен оставаться рядом. tests.cpp/tests.exe создаются
в output; отчёт — рядом. Zig устанавливается отдельно. Сгенерированный C++11
можно собрать другим компилятором. Проверка не обращается к ПЛК или брокеру.

mqtt_gate.ino и mqtt_professional_gate.ino — контрольные скетчи извлечённого
кода UBI. EN=false, только компиляция. Положите каждый в одноимённую папку.
Professional проверяет два Publish и два Subscribe с отдельным состоянием.
Это не готовые прошивки профиля. Сеть и SPI контрольные скетчи не настраивают.
