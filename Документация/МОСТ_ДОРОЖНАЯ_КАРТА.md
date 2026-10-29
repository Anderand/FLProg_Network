# Мосты и менеджер прошивок — план

28.10.2026. [Архитектура](docs/ARCHITECTURE_RU.md), [проверки](CHECKS_RU.md).

| Этап | Состояние |
|---|---|
| Самостоятельный PC COM ↔ HTTP Bridge | 0.3.0: полный веб из Flash ПЛК, проверен без Ethernet и без локальной папки сайта |
| Общий ограниченный UART-протокол и диспетчер служб | C++/Python проверены, контрольная F407 сборка прошла |
| WebUI каналы, типы, команды и политика записи | Ограниченный batch, подтверждения, DO1/AO0 проверены регистрами; AO 0–10000, отдельный режим управления |
| Менеджер прошивок вместо названия OTA-менеджер | 0.8.0-preview.4: выбор COM/скорости, запуск моста, первичная ROM UART-запись; профиль из проекта4, DHCP, 1.0.8 |
| Запуск отдельного моста редактором и менеджером | Проверен из обоих EXE |
| Полный макет редактора через мост | Сделано локально: экспорт, ID/API/SHA-256, неизменяемые ресурсы на PC; 4 страницы на FLE4D |
| UART-блоки Basic и Professional | v0.2: автопривязка из экспорта, общий ID Web UI Start и вариант UART Project Pro. XML/код/протокол/F407 проверены; живой импорт и аппаратный блок ещё впереди |
| Первичная STM32 ROM-прошивка по COM | Реализована в менеджере; 8 программных тестов и GUI пройдены, аппаратная UART-запись не испытывалась; F407 требует USART1/3 |
| FLE4D: реальный COM, RAM, restart | 1.0.8: Flash350724/RAM51628; OTA, новый сеанс после reset за1.203с, без повтора команд; загрузчик сохранён |
| FLE4D: полный веб без кабеля Ethernet | Проверено: Ethernet отключён физически, 4 страницы, RAM-команда, чтения без ошибок; пользовательские DO/AO не менялись |
| FLE4D: длительная нагрузка, кабель, сравнение цикла | Запланировано; текущий счётчик около56 тыс. циклов/с, сравнительного замера нет |
| ESP32 Wi-Fi ↔ UART | Universal0.10 установлена на отдельную ESP32; сеть/настройки проверены. Физический UART кFLE4D ещё не подключён. Кандидат0.11 Web+MQTT проверен программно, не прошит |
| ESP32 HTTP без PC Bridge | Universal0.8/0.9: основная панель Wi-Fi/LAN, автономный8081, общий UART сTCP; программные проверки, аппаратная проверка впереди |
| ESP32: полный веб изFlash ПЛК | Полный пакет/SHA/gzip,4страницы, чтение и команды проверены программно; Wi-Fi/LAN, аппаратная проверка впереди |
| ESP8266 | После ESP32; отдельно проверить память и UART |
| Modbus | Прототип службы2 и TCP502: функции1/2/3/4/5/6/15/16, native/реальныйlocalhostTCP/ARM+ESP32compile PASS; Universal0.9: интеграция в основную GUI проверена программно; аппаратная проверка впереди |
| MQTT через ESP | Кандидат: штатный MQTT-клиент ПЛК + Core/Publish/Subscribe Basic/Professional, NET_KIND3, все настройки вПЛК; nativeMQTT/переподключение/7подписок проверены. Живой импорт и UART впереди |
| Новые способы прошивки COM/USB/через мост, новые MCU | Отдельные адаптеры менеджера, не объявлять готовыми заранее |

Текущая программа не требует редактора и не выбирает COM сама. Контроллер
объявляет только реализованные службы; зарезервированный ID не означает поддержку.
Ветка моста остаётся локальной. Общийr17 сNTP опубликован отдельно; новые мосты в него не включены.

## 28.10.2026: веб из Flash

Сделано: служба4, порционная передача, SHA-256, кеш и смена пакета. FLE4D 1.0.9 проверен без Ethernet с пустым кешем. Следующий дефект: признак готовности Ethernet при потере линка с сохранённой DHCP-арендой. См. docs/FLASH_WEB_RU.md.

28.10.2026: кандидат1.0.10-BRIDGE-LINK — устранено восстановление readiness от одной DHCP-аренды. Негативная проверка старого кода воспроизводит дефект; исправленная функция проходит сценарии линка/DHCP/SPI/millis. Сборка и аппаратная проверка выполняются в _work/ethernet_link_20261028. См. docs/ETHERNET_LINK_RU.md.

28.10.2026: исправление DHCP/link завершено аппаратно на1.0.10: off40/40false, возвратtrueбезreset, четыреHTTPстраницы/OTA/UARTresourcesPASS. См. docs/ETHERNET_LINK_RU.md.

## UART-блоки v0.1

Один блок транспорта для Basic и Professional. Пины берутся из проекта, UART/BAUD/BUDGET/EN — входы. READY/CONNECTED/ERR и счётчики — выходы. Привязка к настроенному Server через FLPROG_BRIDGE_SERVER; автоматический выбор проекта по ID пока не реализован. Следующий шаг — автоматическое связывание в экспорте и проверка импорта блоков FLProg. См. docs/UART_BLOCKS_RU.md. Текущий ПЛК1.0.10 не прошивался.


UARTv0.1: сборкаF407 завершена, Flash366932 (+376),RAM51672 (+28), BIN367440 SHAc5bc4d4541932eb24fb3172daddd1eb18a1b6512937877383307700ab811e17b. _work/uart_blocks_20261028/CHECKS.json. Контрольная1.0.11непрошита, ПЛК1.0.10. Basic/ProXMLиэквивалентныйкод/нативныевызовыPASS;3resourceтестаPASS. Живойимпорт/аппаратныйблокиавтосвязкапроектаещёвпереди. Git/EXE/архивынеменялись.

## 29.10.2026

АвтопривязкаID завершена программно и собрана: docs/AUTO_BINDING_RU.md. Сразу реализован прототипESP32 TCP/UART: docs/ESP32_TCP_UART_RU.md. Пользователь просил без прошивкиESP. Следующий шаг по мосту: проверить на отдельнойESP32 Wi-Fi/UART и обрывы, затем автономный HTTPнаESP. Modbus/MQTTслужбы ещё не реализованы. ПЛК1.0.10 не менялся, Gitнеобновлён.


## Универсальная прошивка ESP

Уточнение пользователя: ESP — только прозрачный мост, прошивка не зависит от проекта ПЛК. Реализованы настройки Wi-Fi/GPIO/UART/TCP/таймаута через защищённую страницу и NVS, без пересборки под сеть/контроллер. Аппаратная проверка ещё впереди; тип платы ESP32/ESP8266 остаётся выбором отдельной аппаратной сборки. См. docs/ESP32_UNIVERSAL_RU.md.


29.10.2026: ESP32 Universal0.2 собрана, Flash931864/RAM47504. config120байт/валидацияPASS, boundedrelayPASS. Проверена независимость исходников отID/проектаПЛК. Комплект E:\SAI\FLProg_Network\_work\esp32_universal_20261029\ESP32_Bridge_Universal_0.2 содержит application932016байт (SHAf04edd2c1093b98a0a29ef4bd1943864a4ecd74335bad256e68a4b1cdb41b1dd), полный4MBобразпервичнойустановки, исходники ирусскуюинструкцию. ПолнаязаписьможетсброситьNVS; приложениеобновляетсяпотекущейразметке, неSTM32загрузчик. Этоcompile-only, физическаяESP/AP/NVSнеиспытывались; ничего непрошивали. Старые прототипы/архивы/EXE/Git неизменны.

## 29.10.2026: запуск ESP из менеджера
Менеджер 0.8.0-preview.9: на вкладке COM / UART добавлены адрес ESP:порт и отдельная кнопка «Открыть через ESP». Общий launcher принимает явный --tcp, запрещает сочетание с COM, проверяет URL до запуска процесса; UART-скорость не передаётся, запись не разрешается автоматически. 14 тестов менеджера PASS. EXE собран в _work/manager_tcp_20261029/Manager_ESP_TCP_preview9 вместе с Bridge0.4 и прежним проверенным профилем1.0.10. SHA256.json содержит2076файлов. Проверка живого GUI/Wi-Fi/ESP ещё впереди. ПЛК/ESP не прошивались, Git и готовые релизы не менялись.

29.10.2026: По явной команде пользователя Universal0.2 установлена на отдельную ESP32 WROOM/COM3, ESP32-D0WD-V3 rev3.1 MAC08:d1:f9:e2:a7:c8 Flash4MB. Esptool hash verified, USB-консоль подтвердила запуск и AP FLProgBridge-f9d108. COM закрыт. Пароль AP не записан в отчёт. FLE4D подключат позже и выберут UART; Wi-Fi HTTP/сквозной UART пока не проверены. HARDWARE_COM3.json. .116/.117 не использовались, Git неизменён.

29.10.2026: По команде пользователя отдельная ESP32 COM3 MAC08:d1:f9:e2:a7:c8 обновлена Universal0.3 (application0x10000, bootloader не меняли). Добавлена смена AP-пароля8..63байта через страницу; индивидуальный пароль не зашит в BIN. Пользовательскую сеть настроили отдельно в NVS; временные CSV/blob/NVS с реквизитами удалены после проверки. DHCP192.168.100.14, TCP3234 доступен. USB подтвердил выбранный AP-пароль и возврат STA после reset. Flash932536/RAM47504; HARDWARE_WIFI.json в _work/esp32_setup_20261029. FLE4D/UART пока не подключали и не проверяли; defaults16/17/115200не являются согласованным подключением. COM3 закрыт; .116/.117 и Git не трогали.

29.10.2026: Universal0.4 установлена только application0x10000 на ESP32COM3 MAC08:d1:f9:e2:a7:c8; NVS/bootloader не стирались. Настройки в STA доступны http://192.168.100.14:8080 с входом паролем настроекESP; cookieHttpOnly/SameSiteStrict и токен сохраняемой формы, пароли не эхо. TCP3234 прежний;8080зарезервирован. Нативные config/relay PASS. Реальный HARDWARE_LAN.json: wrongpassword/unauth/CSRF/порт8080отклоняются, saveс пустым Wi-Fiпаролем сохраняет сеть/UART и возвращается в <configured Wi-Fi>, TCPдоступен. Браузерная проверка входа/формы PASS; вкладка оставлена пользователю. Программа Bridge0.4 открыта, поле адреса заполнено tcp://192.168.100.14:3234, подключение к ПЛК не запускали. Папка _work/esp32_lan_20261029, ESP_SETTINGS.png/BRIDGE_ADDRESS.png. FLE4D/UARTнепроверены, COM3свободен, Gitнеизменён.

## 29.10.2026: проверка без соединения ESP с ПЛК
По просьбе пользователя продолжать без аппаратного UART реализован PC Bridge0.4.1-preview.1: кнопка/CLI --demo-tcp, localhost-only DemoTcpServer, виртуальные каналы10/101/102, режим«ПЛК молчит» и«Обрыв демо». Настоящий TCP с дроблением ответов17байт, не эмулятор всей прошивкиESP/радио/UART. Команды не ставятся в очередь и не повторяются после восстановления. TCP-timeout теперь отличает отсутствие ответаПЛК; фраза про неизвестный результат оставлена для команды записи. 4новых+20протокольных(пересобранныйтекущийC++peer)+3TCPтеста PASS. FrozenEXE чтение/default403/явнаявиртуальнаязаписьPASS. GUIиIAB: read25, mute→нетответаПЛК,unmute→новыйсеанс/read25PASS. Открыты новыйEXE(окно234621484) и http://127.0.0.1:61888/ дляпользователя. Старыеокнанезакрывались. Пакет _work/bridge_demo_tcp_20261029/FLProg_Bridge_0.4.1_TCP_Demo, SHA256.json; CHECKS.json/EXE_SMOKE.json/DEMO_READY.png/DEMO_NO_PLC.png. РеальнаяESPUniversal0.4/ПЛК/UART/Git/общийr17неизменены. Следующее аппаратное испытаниеESP↔UART↔FLE4D отложено до физического подключения; Modbus/MQTTчерезмостещёневыполнены. docs/TCP_DEMO_RU.md.


## 29.10.2026: автономный HTTP, этап B1
Кандидат Universal0.5: /plc на8080, чтение каналов безPCBridge, толькоHELLO/read/meta. Сеть/NVSсхема1 прежние. Один UART-владелец, кооперативный клиент64байта RX/TX,1500мс,безповторов. Протокол и реальные HTTP-callbacks выполнены на нативном адаптере, браузерный предпросмотр повторно читает101=25/отказ102/пустойномер. ESP32compile PASS Flash947976/RAM47912 (+11432/+376к0.4). Не прошит, физическийUARTнеиспытан. Документ docs/ESP32_HTTP_READ_RU.md. Следующий этап B2 — полныймакетизFlash, затем полноценные команды/API.


## 29.10.2026: B2 — полный веб через ESP без PC Bridge
Реализован Universal0.6: порт8081, пакет из службы4 порциями224байта, SHA/ID/API и gzip в браузере, полный макет и batch-чтение. В ESP BIN нет проекта и сетевых реквизитов, файловая система не пишется. Нативный стенд с реальными C++ обработчиками передал15438байт/69порций, открыл4страницы; повреждение и другойID блокируют запуск. Управление ещё закрыто. Сначала аппаратное подключение и измерение heap/скорости, затем команды с подтверждением. Без прошивки устройств/Git. См. docs/ESP32_FULL_WEB_RU.md.


## 29.10.2026: B3 — команды ESP, программный стенд
Universal0.7: типизированная запись WebUI с явным включением для сеанса, requestId против повторов, CSRF/UART-владение, валидация и окончательная WritePolicy наПЛК. AO1234/DO1 и подтверждение данными проверены в браузере на модели. LostACK: одна принятаякоманда,timeout,безповторапослеHELLO. По умолчанию чтение, физические выходы/heap/Wi-Fi/UARTещёнеиспытаны. Следующее: аппаратное подключение по отдельной команде; затем нагрузка/восстановление, полные службыModbus/MQTT. docs/ESP32_COMMANDS_RU.md. Gitнеизменён.


## 29.10.2026: B4 — нагрузка и восстановление без аппаратуры
1000ускоренныхциклов/полныхпакетов/команд,100сбросовпосредитрансфера,1000offline/TCP/duplicateпроверок PASS. СменаIDотклоняетстарыйпакет;возвратпроекта/read-onlyPASS. NativePrivateUsage стабильна200–1000циклов;ESPheapнеизмерен. Кодпрошивки0.7неизменён,Гитнеобновлён. См.docs/ESP32_STABILITY_RU.md. Следующаяобязательнаяпроверка—физическийUART/Wi-Fi/многочасовойheapпослеподключения; программные Modbus/MQTTслужбы ещё впереди.


## 29.10.2026: Modbus и LAN-пример
ЯдроPLCслужбы2 и ModbusTCP↔BridgeUART проверены программно, defaultRO/WritePolicy/limits/timeout/no replay. ESP32пример использует FLProg_Networkr17: Wi-Fi, Wiznet W5100/W5100S/W5200/W5500(auto), RMII LAN8720. РежимыNVS: rawBridge3234 либо Modbus502; DHCP, проверкаGPIO. Это отдельныйпример: основнаяформа0.7 и автономныйweb8081 черезLAN ещё не интегрированы. ПрототипсобранESPcore3.3.11:Flash1083872/RAM57000, privateR17sourceverified. МодельWeb+ModbusнаодномUART/nativeTCP/ядроF407compilePASS, аппаратныеSPI/RMII/UART/heapнеиспытаны. Пакет _work/modbus_lan_bridge_20261029/FLProg_Bridge_Modbus_LAN_Prototype.ZIP167SHA/CRC+packagedTCPsmokePASS. Git/устройстванеменялись. docs/MODBUS_LAN_RU.md.

## 29.10.2026: основная ESP Universal 0.8 — выбор Wi-Fi/LAN и веб 8081
Выбор Wi-Fi/Wiznet SPI/RMII LAN8720 встроен в основную панель 8080. Автономный веб 8081 использует выбранную сеть, включая LAN без Wi-Fi. GPIO/PSRAM проверяются, старые Wi-Fi настройки сохраняются; NVS schema2/config2 с миграцией старой записи только в RAM. Нативные настройки/HTTP/полный Flash-трансфер всех трёх моделей и регрессии PASS; браузер Wiznet/RMII save/reboot/полный веб PASS. ESP32 core3.3.11 compile: Flash1186204/staticRAM63008; не прошито. Это закрывает программную интеграцию LAN, ранее отмеченную выше как будущую. Отдельный Modbus502-пример не объединён. Следующее: аппаратные SPI/RMII/UART/DHCP/heap. Устройства, Git и общий r17 не менялись. См. docs/ESP32_LAN_WEB_RU.md; _work/esp32_lan_web_20261029.

## 29.10.2026: Universal 0.9 — Modbus в основной панели
Встроен выбор TCP-службы raw3234 / Modbus502, независимо от Wi-Fi/Wiznet/RMII. Основной runtime использует отдельный типизированный клиент и общий UART с WebUI; один TCP-владелец, веб-job/lease имеют приоритет до начала TCP. После смены владельца новый HELLO; очереди и повторов записи нет. NVS schema2/144 байта сохранена, defaults raw. Нативные настройки всех3сетей/runtime/8FC/lostACK и настоящий localhost TCP (0/22 виртуальные записи) PASS; GUI LAN+Modbus/save/reboot PASS. Полныйвеб3моделей/SHA/69порций и регрессии PASS. docs/ESP32_MODBUS_WEB_RU.md, _work/esp32_modbus_web_20261029. Аппаратный UART/SPI/RMII/heap ещё не проверен, PLCservice2 нужна в будущей прошивкеПЛК. Никакие устройства/COM/Гит/общийr17 не менялись. Следующее программное направление — роли и ограничения MQTT через мост; аппаратная проверка отложена по пользователю.

Universal0.9: ESP32 core3.3.11 compile PASS, Flash1190084/staticRAM63912 (+3880/+904 к0.8). Заголовки SDK совпадают с исходниками, privateNetworkr17 dependency проверена. Пакет _work/esp32_modbus_web_20261029/ESP32_Universal_0.9_Modbus_Web_Prototype.zip:205файлов SHA/CRC PASS, SHA74564bd0352a9b4a134e3593250a79916f260c1fe90606e21531c6127373610e. CHECKS/TCP_CHECKS/LAN_TRANSFER_CHECKS/BUILD/PACKAGE_VERIFIED. Панель программного стенда http://127.0.0.1:55114/ (session93528), полныйвеб55115; GUIпроверяетформу/виртуальныйNVS, отдельныйlocalhostTCPтест проверяеттотжеproductionModbusRuntime+виртуальныйПЛК. Не аппаратныйстенд! РеальнаяESP0.4/.14/COM3/ПЛК/Git/общийr17 неизменены.

## 29.10.2026: TCP-клиент ПЛК через ESP, Universal0.10
По уточнению пользователя MQTT-настройки/логика только вПЛК, ESPтолько транспорт. Добавлены PLCservice5 pullNEXT/RESULT, кооперативный FLProgBridgeTcpClient(RX/TX220), ESPBridgeTcpProxy и режимTCPклиента в панели безbroker/topics/passwordполей. Одинсокет; режимпока занимаетUARTцеликом, вебПЛК/Modbusприостановлены,настройкиESP8080доступны. СуществующиеMQTT-блокиавтоматическинепереключены: следующийэтап—адаптерexistingMQTTтранспортаиBasic/Pro. NativeMQTTнастоящийlocalhost:CONNECT/auth/SUBSCRIBE/SUBACK/PUBLISH400/incoming/closePASS; partialwrites7/partialUART7. Bounds/busy/lostRESULTACK/no replay/deadline/reset/link/milliswrapPASS; PLC480/ESPproxy1088байтnative. CortexM4C++11objectcompilePASS;7регрессийPASS. docs/PLC_TCP_CLIENT_RU.md. ПользовательразрешилпрошитьТОЛЬКОESP, FLE4Dнепрошивать; COM3поканедоступен(толькоCOM1), попросилиподключитьUSB, вответпопросилоткрытьменеджер—открыт0.8.0-preview.9PID2580window53282364. СборкаESPв_work/esp32_tcp_client_20261029идёт, Гитне трогать.

Universal0.10 завершён программно: SDKcore3.3.11 Flash1206548/staticRAM68544 (+16464/+4632 к0.9), SDKheaders+objectmtime/privateR17проверены. Пакет ESP32_Universal_0.10_PLC_TCP_Prototype.zip209файлов SHA/CRC PASS; SHAd728a01289fa23ca17ce0126705ac01f4028b161beea601dde31b7c8b5de3a22. CHECKS/MQTT_CHECKS/BUILD/PACKAGE_VERIFIED. GUI save/rebootмоделиPASS, previewhttp://127.0.0.1:61111/session91281. Менеджер0.8.0-preview.9 открытпо просьбе. АвторизацияпрошивкиТОЛЬКОESPсохраняется,ноCOM3отсутствует,толькоCOM1;ESPНЕпрошита,FLE4DНЕтрогали,Гит/r17неизменены. НеобъявлятьготовойинтеграциюстарыхMQTTблоков:проверенновыйPLCstreamAPI+MQTTфреймингнаPLс-стенде;следующееадаптерштатногоMQTTиBasic/Pro,затемобщийдиспетчердляодновременногоWeb/TCP.

29.10.2026: пользователь сообщилCOM3есть; esptool подтвердил прежнююESP32-D0WD-V3MAC08:d1:f9:e2:a7:c8. Universal0.10 application1206704байт записанаТОЛЬКО0x10000, SHAисходногоBINсверенсmanifest, esptoolhashverified; NVS/bootloader/partitionнеписались. USBBOOT_COM3.log подтвердилuniversal0.10/IP192.168.100.14. HTTP8080login/configPASS: Wi-Fi,сохранённыйпароль,UARTrx16tx17,rawmode0сохранились;новыйвыборTCPклиентаприсутствует. COM3закрыт,FLE4Dнепрошит,физическийUART/MQTTнепроверен,Гит/r17неизменены. HARDWARE_COM3.json/FLASH_COM3.log,rootBUILD/CHECKSобновлены. ZIP0.10покаисторическийcompile-only;неутверждатьчтоегоотчётвключаетаппаратнуюпроверку. docs/PLC_TCP_CLIENT_RU.mdобновлён.


## 29.10.2026: MQTT-блоки ПЛК подключены к TCP-мосту
Сменный TCP-транспорт beginExternal в штатномMQTT, FLProgMqttBridgeTransport и NET_KIND3/NET_NUM1..8 вCore. Basic/Professional6UBI: реальныйC++исходникMQTT+извлечённыйкод обоихформатов черезservice5/ESPproxy/localhostbrokerPASS. Auth/connect/sub/pub400/incoming/DISCONNECT, reconnect/resubscribe/noPublishReplay, отказCONNACK,7подписок,ошибка19/nativefallbackPASS. ВсеMQTTнастройкивПЛК,ESPнеизменена. Кандидатизолированв_work/mqtt_blocks_bridge_20261029, installedlibs/r17/Git/FLE4Dнеизменены. docs/MQTT_BLOCKS_BRIDGE_RU.md. Следующее:живойимпорт/аппаратныйUARTпослесогласования, общийWeb+MQTTдиспетчер.

29.10.2026: штатные MQTT Core/Publish/Subscribe подключены к ESPservice5 в изолированном кандидате _work/mqtt_blocks_bridge_20261029. beginExternal/FLProgMqttTransport в полном MQTT-клиенте, FLProgMqttBridgeTransport (отложенныйconnect и подтверждённыйwrite), NET_KIND3/NET_NUM1..8 вBasic/Professional. Извлечённыйкод6UBI+полныйactualMQTT.cpp сArduino/nativeTCPdoubles черезactualESPproxy/реальныйlocalhost PASS: auth/connect/sub/pub400/incoming/DISCONNECT, reconnect/resubscribe/noPublishReplay обоихформатов,refusedCONNACK10 обоих,7подписок,нетtransport→ERR19,обычныйnativepathсохранён. StopPLCTCPтеперьставитCLOSEсразу,неждётбудущегоpoolпослеend/сменытранспорта. ВсенастройкиMQTTтолькоПЛК. КонтрольныйскетчGenericBlackF407VG/core3.0.0 compilePASS Flash59736/RAM12672,неOTAпрофиль/непрошивался. CandidateNetworkотbaselineR17 отличаетсяровно7разрешённымифайлами,installed/stocklibs/r17неизменены. SDKиспользовалprivatecandidate. Пакет FLProg_MQTT_ESP_Transport_Prototype.zip186SHA/CRC PASS SHAa87f810ac2bc691544c1ec8c4922deeea0cc8b8acb76544a367e2f1304c87e3e. docs/MQTT_BLOCKS_BRIDGE_RU.md/ROADMAPобновлены,sourceoverlay flprog_bridge/integration/mqtt,генераторыtoolsupdated,tests/mqtt_transportfixtures. FLE4D/ESP/COM/Гитне трогали. ESP0.10остаётсядостаточной,перепрошивканенужна. ЖивойимпортFLProg/физическийUARTнепроверены; mode2по-прежнемувладеетUARTэксклюзивно. Следующее—аппаратнаяпроверкапослекоманды/подключенияилиобщийWeb+MQTTдиспетчер.

## 29.10.2026: Universal0.11 — общий WebUI/MQTT UART
Общийnonce/sequence/owner дляWeb96иTCPproxy288, раздельные результаты; резервация20мсдляожидающегоклиента истекаетбезочередиданным. HELLOвдействующемsharedсеансевозвращаетidentityбезresetTCP; послеинвалидацииfreshHELLOзакрываетстарыйTCP. mainmode2обслуживаетwebjobиproxy,viewerleaseнеблокируетMQTT. Браузерчитаетпри409доticket:30*10мс,записинеавторетраятся. Nativecontextwrap/cancel/timeout/sequenceoverflowPASS. ActualServer Web+TCP100writes/201read+chunk224/resultisolation/HELLOreuse/new-sessionclosePASS. FullactualMQTT+Basic/Professional+реальныйlocalhostbroker:208Webread+69chunksполногоgzip15438byteequal,1TCPopen;reconnect2opens/resub/noPublishReplayPASS;7subs/refusedPASS.7legacyC++suitesиactualJSbusy/noWriteRetry/lostResponsePASS. SDKESP32core3.3.11 Flash1207924/staticRAM68608 (+1376/+64к0.10), finalSDKheaders/objmtime/privateR17PASS. Пакет _work/shared_uart_20261029/ESP32_Universal_0.11_Shared_Web_MQTT_Prototype.zip224SHA/CRC PASS, SHA51b45c34a17a420f85a1b5b200512e2320c23f10b651c59a8fbe1986918211e9. PLCMQTTcandidateAPI/service5неизменены;ESPbaselineSDKr17иhostPLCcandidateвпакетеразличаютсянамеренно. docs/SHARED_WEB_MQTT_RU.md. РеальнаяESPостаётся0.10на.14, FLE4D/COM/NVS/Гит/общийr17НЕтрогали. Живойбраузер+аппаратныйUART/WiFi/LAN/heapнепроверен,толькопрограммныеRPC/ресурсы. Следующее—аппаратнаяпроверкапослеотдельнойкоманды/подключения.

## 29.10.2026: нагрузка Web/MQTT и исправление TCP EOF
Ускоренный software-стенд actualMQTT+Professional/Core/Pub/Sub+sharedESPproxy+localhost:201pub(400+200seq/ack),9brokerобрывов/10соединений,0replay,2070webread/690chunks/10gzipпакетов15438byteequalPASS. NativePrivateUsage40→200циклов1146880→1118208,10точекбезроста;неESPheap/несуточныйтест. НайденреальныйEOFдефект:финальныеданные+FIN приводиликreconnectMQTTдопарсингаRX(первыйпрогон ack19потерян). ИсправленыPLC FLProgBridgeTcpClient:connected=trueпокаестьRX,ошибканестираетRX,canWriteотдельно;MqttBridgeTransportwriteguardиспользуетcanWrite,чтобыRXнеподтверждалошибочнуюTX. Повтор200/9PASS.7UARTfaultcasesNEXTrequest/response/RESULT/ACK/CRC/link0или1write/noReplay/reopen/webrecoveryPASS;EOFpartialdrain/stopPASS. Basic7subs+fullwebPASS. Кандидат _work/shared_stress_20261029 отличаетсяотпредыдущегоMQTTcandidateровно2headers,stock/r17неизменены. GenericF407VGcore3.0.0SDK compilePASS Flash59768/RAM12672 (+32/+0),неOTAпрофиль/непрошит. Пакет FLProg_MQTT_Bridge_Stability_Prototype.zip197SHA/CRC PASS SHAd0ea379774a9d6ecd15ba9fd351de9605c1a71d8f817a161ae70b8d4b7260f0e. docs/SHARED_STRESS_RU.md/CHECKS/STRESS_CHECKS/F407_BUILD/PACKAGE_VERIFIED. ESP0.11binaryнеизменён,реальнаяESP0.10/.14/FLE4D/COM/GitНЕтрогались. Следующее—аппаратныйUART/WiFi/LAN/heapпослекомандыиподключения,живойимпортUBIещёвпереди.

## 29.10.2026: большие TCP-потоки и медленный получатель
Программный тест tcp_backpressure_test.cpp передал 65536 байт в каждом направлении через реальные PLC stream/Server/ESP proxy: короткие записи по 7 байт, каждый пятый write возвращает 0, UART по 3 байта, медленный PLC-получатель, переход millis через UINT32_MAX. Побайтовое сравнение PASS; непрочитанная порция 220 байт сохраняется и останавливает дальнейшее чтение. Найдено переполнение: ESP proxy приводил available() к uint16 до ограничения wanted, поэтому 65536 превращалось в 0. Исправлено сравнение до приведения, без новых полей или буферов. 7 fault-сценариев и TCP EOF повторно PASS. Это исправление исходников после BIN0.11: новый ESP BIN ещё не собран, на устройстве остаётся0.10. Не аппаратная проверка и не измерение ESP heap. Отчёт: _work/tcp_backpressure_20261029. Гит/релизы/устройства не менялись.


## 30.10.2026: Universal0.12 собрана и установлена только на ESP
Полная ESP32core3.3.11 сборка: Flash1207924/staticRAM68608, application1208080 SHA018c2b6b939e21bff571d5d250d4acd3126d6f0c6b56f123e2a206aa2141a7e6. SDKheaders после#line/objectmtime/imageinfo PASS. ОбщийUART/Web/MQTT, PLC EOF и ESP available>65535 исправлены; повторныйstress201pub/9disconnect/10gzip и64KiBbothdirections/fault7/6regressionPASS. По команде пользователя толькоESP COM3 MAC08:d1:f9:e2:a7:c8 прошита application0x10000, esptoolhashverified. USBbanner0.12/IP.14, HTTP8080login, configдо/послеточновсовпали,TCP3234PASS,COMзакрыт. NVS/bootloader/partitionнеписали. FLE4Dнепрошивался,physicalUART/MQTT/LAN/heapещёнепроверены. _work/esp32_final_20261029. ПубликацияGitHub разрешена пользователем; отдельный prerelease esp-bridge-v0.12,общийr17неперезаписывать.
