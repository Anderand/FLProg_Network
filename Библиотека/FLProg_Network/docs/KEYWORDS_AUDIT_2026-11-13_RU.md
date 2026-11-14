# FLProg_Network — аудит `keywords.txt` (13.11.2026)

**База:** сохранённый исходный эталон `libraries_исходный_эталон_2026-11-10.zip` (`libraries/FLProg_Network/keywords.txt`).  
**Кандидат:** `FLProg_Network_dev20_EIS162_TypedExists_ESP8266_IPAddress_FULL_2026-11-13.zip` + ТОЛЬКО корректировка индекса ключевых слов и документация/тесты.

## Что было обнаружено

- Исходный `keywords.txt`: 440 записей, включая повторения и некорректно разделённые строки.
- Две последние записи `transportIdentityForRoute` и `transportByIdentity` содержали текстовые символы `\t` вместо фактической табуляции. Первая не распознавалась Arduino как keyword; вторая одновременно дублировала ранее существующий идентификатор.
- `setKeepAlive`, `setReconnectBackoff`, `transportByIdentity` присутствовали по два раза (последний дубликат учтён после исправления символов-разделителей).
- Отсутствовали метки новых методов типизированного реестра, констант ошибок, EIS-функций SPI/RESET и версионных макросов.

## Что исправлено

- Исправлены две записи с текстовым `\t`, повторения удалены с сохранением первых записей и их категорий.
- Добавлено **53 ранее отсутствовавших идентификатора**. Новые разделы: версии и feature macros; безопасный поиск по типам; RT_HW/Wiznet SPI/RESET.
- Финальное состояние: **490 уникальных записей** (`KEYWORD1`, `KEYWORD2`, `LITERAL1`), настоящий TAB между именем и типом, кодировка UTF-8, окончания CRLF.
- Проверено, что **каждый из 490 идентификаторов реально присутствует в исходном коде**, а не только в документации; имена не перепутаны по регистру. Внутренние вспомогательные функции намеренно не индексируются.
- Добавлен `tests/check_keywords.py`: проверка разделителей, допустимых групп, отсутствия повторов, связи с исходниками и обязательного актуального API.

## Что появилось для редактора Arduino

- Реестр: `FLProgNetworkDeviceKind`, `FLProgNetworkDeviceRegistryResult`, `getWiznet`, `getWifi`, `existsWiznet`, `existsWifi`, `deviceKind`, статистика/диагностика, `FLPROG_NETWORK_DEVICE_INVALID`, `FLPROG_NETWORK_DEVICE_TYPE_MISMATCH` и прочие коды/типы.
- Wiznet и RT_HW: `setPinRST`, `setSpeedSPI`, `pinRST`, `poolConfigurationStatus`, `setWiznetPoolFactory`, `setSpiSpeedRuntime`, `setStartupDelayMs`, `setResetMode`, `ethBindRtHw`, `ethSetSpiSpeed`, `ethSetStartupDelay`, `ethSetReset` и режимы сброса.
- Условная компиляция: `FLPROG_NETWORK_API_LEVEL`, `FLPROG_NETWORK_HAS_TYPED_DEVICE_LOOKUP`, `FLPROG_NETWORK_HAS_TYPED_DEVICE_EXISTS`, `FLPROG_NETWORK_RT_HW_AUTO`, `FLPROG_NETWORK_HAS_RT_HW_BASE`.

## Проверка

```shell
python3 tests/check_keywords.py
# KEYWORDS PASS: 490 unique entries ...
```

**Важно:** `keywords.txt` используется для подсветки в редакторах Arduino. Он не влияет на вызовы функций, типы или машинный код прошивки. Изменять `library.properties` или C++ API ради подсветки не требуется.
