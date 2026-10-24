# KC868-A16 RMII hardware gate

Минимальная аппаратная проверка `FLProg_Network` на KinCony KC868-A16 с
встроенным PHY LAN8720. Тест намеренно не включает Wi‑Fi, W5500, OTA или
логику реле: так локализуется именно RMII transport и HTTP поверх него.

## Настройки платы

- Плата Arduino IDE: `ESP32 Dev Module`.
- Монитор порта: `115200 бод`.
- Подключите кабель Ethernet к сети с DHCP до включения питания.
- Питание контроллера — штатное для KC868-A16.

Используемая распиновка KC868-A16:

| LAN8720 параметр | Значение |
| --- | --- |
| PHY address | 0 |
| MDC | GPIO23 |
| MDIO | GPIO18 |
| 50 MHz clock | GPIO17 output |
| DHCP | включён |

Эта конфигурация соответствует опубликованным KinCony параметрам KC868-A16:
[форум KinCony](https://www.kincony.com/forum/printthread.php?tid=1666) и
[официальный пример конфигурации](https://github.com/hzkincony/kc868-a16/blob/main/kc868-a16.yaml).

## Критерий первого PASS

1. В Serial Monitor появляется строка `RMII ready=1 link=1 ip=A.B.C.D error=0`.
2. По указанному IP открывается `http://A.B.C.D/`.
3. `http://A.B.C.D/api/status` возвращает JSON с `ready:true`, `link:true` и
   действующим IP.
4. После отключения кабеля `link` становится `0`, после возврата кабеля —
   снова `1`; HTTP снова открывается.

Пришлите лог от старта до получения IP и результат открытия страницы. После
этого перейдём к TCP/UDP, HTTP-нагрузке и совместной работе RMII + Wi‑Fi.
