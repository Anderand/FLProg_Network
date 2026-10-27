# API для интеграции — r15

[Индекс](ИНДЕКС.md) · [API редактора](API_РЕДАКТОРА.md).
MANIFEST_API.json связывает каждую копию заголовка с оригиналом и SHA-256.
Полные реализации Network находятся в ../Библиотека/FLProg_Network/src,
генератор и редактор — ../Исходники/WebUI. Копии заголовков не отдельная библиотека.

MQTT: setSubscriptionLimit(size_t), subscriptionLimit(), subscriptionCount(),
subscriptionMemoryBytes(), clearSubscriptions(); новые ошибки 17/18.
Подписки динамические; end/begin сохраняют их, destructor освобождает.
[Полный контракт](Справка/MQTT_RU.md).

Веб: bundle CSS/JS из Flash, каталог виджетов страницы. /item?page=N сообщает
widgetCatalog=true, /item?widgets=ID возвращает {page,items:[[index,widget],...]};
старый /item?index=N сохранён. Каналы, маршруты и интерфейсы Start/OTA прежние.
[Ресурсы](Справка/FLASH_BUNDLE_RU.md) · [каталоги](Справка/WIDGET_CATALOG_RU.md).
