# Локальный API редактора

Источник: [server.py](../Исходники/WebUI/editor/server.py). Сервер слушает только 127.0.0.1, по умолчанию порт 8766. Это API разработки на ПК; он не доступен по IP ПЛК.

| Метод и маршрут | Вход / результат |
|---|---|
| GET `/api/demo-preview` | Проект демо уставки и busy/result |
| GET `/api/demo` | Проект базового демо |
| GET `/api/network-api` | Машинный каталог сетевого API |
| POST `/api/validate` | JSON проекта → отчёт summary и проблемы с адресами виджетов |
| POST `/api/preview` | JSON проекта → объект html для sandbox-предпросмотра |
| POST `/api/save` | JSON проекта → ok и file; сохраняет .flpui |
| POST `/api/build` | JSON проекта либо {document: проект, allowWarnings: true} → ok, project, package, installed |

JSON-проект использует schema `flprog.webui/1.0`; примеры находятся в [projects](../Исходники/WebUI/projects). Для POST передавайте Content-Type: application/json. Сборка с ошибками возвращает 422, с неподтверждёнными предупреждениями 409, неверные данные 400; unknown API — 404. Проверка /validate сама по себе возвращает 200 и отчёт, поэтому проверяйте summary.errors.

/build имеет побочный эффект: сохраняет проект, создаёт пакет и при настроенной доступной папке FLPROG_LIBRARIES копирует сгенерированную библиотеку. Для безопасной предварительной проверки вызывайте /validate и /preview. Не публикуйте локальный сервер в интернет. Статический интерфейс и этот контракт развиваются совместно, версионной гарантии для сторонних клиентов пока нет.


## r14: совместимость и внешние файлы

POST /api/compatibility принимает .flpui и возвращает checks, summary,
ok без записи. POST /api/build выполняет проверку перед записью; при
несовместимости отвечает422 с compatibility. Успех включает путь libraries,
пакет с WEBUI_COMPATIBILITY.json и подходящий runtime. Старые пакеты требуют
регенерации. projectFolder задаёт внешний проект, installToIde включается
только явно. POST /api/contract возвращает таблицу каналов и Markdown.
[Текущие контракты](README.md) · [Совместимость](Справка/BUILD_COMPATIBILITY_RU.md).
