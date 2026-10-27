# API FLProg Network — r14, для интеграции Сергею

Это справочный срез, не четвёртая устанавливаемая библиотека. Реализация
находится в трёх папках Библиотека. Сетевой интерфейс и SPI задаёт FLProg.

[Индекс C++ и источников](ИНДЕКС.md) · [HTTP и команды](HTTP_И_КОМАНДЫ.md) ·
[Каналы FBD](Справка/CHANNEL_CONTRACT_RU.md) · [Совместимость](Справка/BUILD_COMPATIBILITY_RU.md).

## Локальный API редактора

POST /api/compatibility принимает документ .flpui и возвращает kind=export,
checks[{status,message,path}], summary{errors,warnings}, ok. Он не пишет файлы.
POST /api/build принимает {document,allowWarnings}; валидирует макет и
совместимость до записи. При ошибке совместимости HTTP422 и compatibility
с подробностями. Успех создаёт пакет с WEBUI_COMPATIBILITY.json и runtime
рядом. POST /api/contract возвращает таблицу каналов/Markdown без записи.
Прочие маршруты: /api/save, /api/validate, /api/preview, /api/demo-preview.
Это localhost API редактора, а не HTTP API ПЛК.

Канонический проверяющий модуль:
[build_compatibility.py](../Исходники/WebUI/tools/build_compatibility.py).
Паспорт schema=flprog.webui.build/1.0, projectId, descriptorApi=1, files
с SHA256 двух заголовков. Runtime содержит FLPROG_WEBUI_DESCRIPTOR_API=1;
строка версии библиотеки не заменяет этот контракт. Дубли отображаются,
препроцессор проверяет фактически выбранный runtime. Это не подпись образа.
Старые пакеты требуют явной регенерации; ID/FBD-связи сохраняются.

[Карта](../Исходники/WebUI/ROADMAP_RU.md) · [Все исходники WebUI](../Исходники/WebUI).
Внутренние заголовки перечислены для полноты и не обещают стабильного API.


[Расширенная справка локального API редактора](API_РЕДАКТОРА.md). Прежние справки gzip, потоковой выдачи, уведомлений и сетевого API сохранены в индексе вместе с актуальными заголовками.
