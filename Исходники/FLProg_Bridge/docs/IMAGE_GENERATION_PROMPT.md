# Полное задание генератору

Инструмент: встроенный image_gen. Режим: новая непрозрачная картинка.

```text
Use case: infographic-diagram. Create a premium, exceptionally legible Russian-language technical architecture presentation graphic for "FLProg Network". Landscape 16:9, large 2560-ish canvas, restrained dark navy background matching industrial WebUI, ivory typography, cyan and teal accents, thin orthogonal connector lines, rounded cards with tasteful depth, consistent minimalist device icons. It must look like a professionally designed product architecture slide, not a screenshot or generic flowchart. Generous spacing. Exact, correctly spelled Russian labels. Title at top: "FLProg Network". Subtitle: "Единая система прошивки и связи с контроллерами". Small badge "Концепция развития".

Structure with 3 clean columns and bottom service row:
Left column heading "ПРОГРАММЫ НА КОМПЬЮТЕРЕ". Two compact cards at top: "Веб-редактор", smaller "Проект и интерфейс"; "Менеджер прошивок", smaller "Сборка BIN и загрузчиков · OTA · SWD". Thin arrows labelled "Запуск" from BOTH cards to central PC bridge card. Separate left lower card "Браузер", smaller "Наш или сторонний интерфейс".
Middle column heading "МОСТЫ СВЯЗИ". Prominent cyan card "FLProg Bridge", smaller "Самостоятельная программа", then "COM / USB-UART", badge "Первый этап". Browser to this card arrow labelled "Локальный HTTP API". Below it a dashed violet card "ESP32 / ESP8266", smaller "Wi-Fi ↔ UART", badge "Следующий этап". Browser also connects to ESP card with Wi-Fi label. Both bridge cards connect separately to right controller card with UART labels. Avoid crossing wires.
Right column heading "КОНТРОЛЛЕР". Large elegant stylized PLC device icon, generic not claiming exact hardware image, label "STM32 / FLE4D", smaller "Единый протокол моста". A conceptual service hub inside or below controller fans out to 3 service pills: "WebUI" cyan with subtext "Каналы · команды · диагностика"; "Modbus" muted violet with badge "В дальнейшем"; "MQTT и другие" muted violet with badge "В дальнейшем". CLEAR that future Modbus/MQTT are separate services over same transport, not currently implemented.
Bottom footer elegant divider: "Один транспорт — разные службы" and smaller "Мост работает без редактора. Управление и данные остаются в ПЛК."
No code, no tiny dense text, no claims of completed hardware testing, no watermark. Ensure all connectors are technically unambiguous and text readable. Blue means first development stage, muted violet dashed means planned. Do not mark bridge as finished.
```
