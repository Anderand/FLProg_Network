# Исходники проверок MQTT

build_mqtt_blocks.py --output <папка> воспроизводит три UBI (Python 3).
test_mqtt.py --library <FLProg_Network> --output <рабочая папка> --compiler <zig.exe>
компилирует реальный класс MQTT со стендом часов/транспорта/отказа выделения RAM.
В output создаются tests.cpp/tests.exe и отчёт рядом. Zig надо установить отдельно.
Для другого C++ компилятора используйте сгенерированный tests.cpp как C++11.

mqtt_gate.ino — compile-only пример всех трёх блоков, EN=false, сеть не настраивает.
Поместите в папку mqtt_gate и соберите для FLE4D-30MT с библиотекой этого выпуска.
Это проверка компиляции, не готовая прошивка профиля и не аппаратный MQTT-тест.
run_fix33_host_tests.py / fix33_host_harness.cpp.in — 26 сетевых регрессий.
