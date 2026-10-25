# coding: utf-8
from pathlib import Path
import json,hashlib,shutil,statistics,struct
B=Path(r'E:\SAI\FLProg_Network');W=B/'_work/load_fle4d';S=Path(r'E:\FLP\Flprog_network\flprog_webui_next');P=B/'Прошивки_для_проверки/FLE4D_LOAD_1.0.10';assert not P.exists();P.mkdir(parents=True)
shutil.copy2(W/'build/FLE4D_NOTICES.ino.bin',P/'FLE4D_LOAD_1_0_10.bin');data=(P/'FLE4D_LOAD_1_0_10.bin').read_bytes();stack,reset=struct.unpack_from('<II',data);assert 0x20000000<=stack<=0x20020000;assert reset&1 and 0x08010000<=reset<0x08080000
for name in ['FLProg_Network','FLProg_WebUI']:shutil.copytree(W/'libraries'/name,P/'libraries'/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(W/'FLE4D_NOTICES',P/'FLE4D_LOAD_source');shutil.copytree(S/'tools',P/'tools',ignore=shutil.ignore_patterns('__pycache__','*.pyc'));shutil.copytree(S/'runtime/FLProg_WebUI/web_assets',P/'web_assets')
for p in W.iterdir():
 if p.is_file() and p.suffix in {'.json','.log','.png','.py'} and p.name not in {'prepare_checks.py','add_hash_test.py','extra_test.py','prepare_host.py','add_timing.py','rebuild.py'}:shutil.copy2(p,P/p.name)
rollback=B/'releases/FLProg_Network_2026-10-25_r11/Примеры/FLE4D_1.0.9_NOTICES/FLE4D_NOTICES_1_0_9.bin';shutil.copy2(rollback,P/'ROLLBACK_1_0_9_NOTICES.bin')
heap=json.loads((W/'HEAP_VERIFICATION.json').read_text());timing=json.loads((W/'BROWSER_TIMINGS.json').read_text());warm=timing['warm_ms']+timing['warm_after_stress_ms'];digest=hashlib.sha256(data).hexdigest()
report=f'''# Загрузка WebUI: прогресс, повторы GET и кеширование

25.10.2026. Проверено по OTA на FLE4D-30MT / STM32F407VG / W5500, IP 192.168.100.8. Установлена **1.0.10-LOAD**. Сеть, пины SPI и адрес приложения прежние. Загрузчик не менялся; физические выходы не переключались. Git/GitHub, общий релиз r12 и EXE редактора не изменялись.

## Изменения

- Страница показывает процент и номер загружаемого скрипта, затем «100%. Чтение данных ПЛК…».
- Сняты фиксированные паузы 80 мс между 17 скриптами. Скрипты и CSS читаются последовательно через fetch, полностью до выполнения. После ошибки тело не исполняется; повтор не дублирует выполнение.
- Только GET: максимум 3 попытки, таймаут полного чтения 2500 мс на попытку, паузы 150/300 мс. Повторы при транспортной ошибке, 408/429/5xx; обычные 4xx завершаются сразу. Отправка POST-команд по-прежнему без автоматического повтора. Новые HTTP-запросы состояния сериализуются как прежде.
- Версия URL — хеш содержимого всего набора ресурсов. Генератор обновляет её автоматически; тест проверяет изменение при правке ресурса и детерминизм повторной генерации.
- Только точное совпадение v с текущим хешем получает `Cache-Control: public, max-age=31536000, immutable`. HTML, versionless и неправильная версия получают no-store. Данные ПЛК читаются с fetch cache:no-store, статические ресурсы — cache:default. Полный refresh/очистка кеша и политика конкретного браузера могут потребовать повторной передачи.
- Network sendStreamProgmem получил необязательный bool cacheImmutable=false. Курсор, буферы и 14 HTTP-маршрутов не увеличены. На старой Network-библиотеке helper сохраняет совместимый stream/bounded fallback без обещания кеш-заголовков; для полного эффекта нужны обе приложенные библиотеки.
- В UART добавлен mallinfo: занятая куча и свободное место внутри выделенной malloc-арены. Это не вся свободная RAM и не максимальный доступный блок.

## Проверки на устройстве

| Проверка | Результат |
|---|---|
| OTA и автоперезапуск | Версия 1.0.10-LOAD подтверждена identity и UART |
| 20 ресурсов | Распакованные байты совпали с исходниками; gzip и Content-Length корректны |
| HTTP cache | Точный v — immutable; HTML, отсутствующий и неверный v — no-store |
| Первое открытие браузера | {timing['cold_ms']/1000:.3f} с |
| 15 повторных открытий | {min(warm)/1000:.3f}–{max(warm)/1000:.3f} с, медиана {statistics.median(warm)/1000:.3f} с |
| После серии нагрузки | Ещё 10 обновлений без ошибки, данные 30.5 и счётчик 1 сохранены |
| Чтение ресурсов | 20 циклов × 20 = 400 чтений, без ошибок |
| Уставка | 25 → 30.5, принято и подтверждено данными |
| Команда | Подтверждение → busy=true/result=false → busy=false/result=true; счётчик 0→1 |
| Повторные загрузки | Команда повторно не отправлена, счётчик остался 1 |
| JS console | Ошибок не обнаружено в рабочей вкладке |
| Куча UART | {heap['samples']} замеров, HEAP_USED={heap['used_min']}…{heap['used_max']} байт, в конце {heap['used_last']} |
| Тесты ПК | 28 тестов; bootstrap retries/timeout/403/one execution/cache version; реальные C++ server methods с частичными/нулевыми записями, HEAD и cache headers; verify_release OK |

Время браузера измерено от начала inline bootstrap до чтения описаний и первого state, без TCP-навигации до HTML. Старый замер 2.50–3.55 с относится к прямому чтению набора ресурсов, а не полному браузерному открытию: напрямую сравнивать как «ускорение в X раз» нельзя. Удалено гарантированное ожидание 1.36 с, повторная загрузка использует кеш по хешу.

Ограничение одного HTTP-клиента остаётся. Одна навигация сразу после параллельной аппаратной проверки вернула отказ TCP; через чистую вкладку сервер работал. Повторы внутри bootstrap помогают только после получения HTML, а не при первоначальном отказе соединения до него. Таймаут graceful close W5500 5000 мс сохранён, так как раннее закрытие обрывало большие медленные ответы. Имитация транспортного отказа/зависшего тела проверена в автоматическом тесте JS; физический кабель в этой серии не отключался.

По этой серии роста занятой кучи нет. Это проверка нескольких минут работы и сотен запросов, не доказательство отсутствия любой утечки во всех сценариях. HEAP_ARENA_FREE в конце {heap['arena_free_last']} байт; поле FREE_BLOCKS у минимального allocator информативность не гарантирует.

## Память и BIN

| Показатель | 1.0.9-NOTICES | 1.0.10-LOAD |
|---|---:|---:|
| Flash по компилятору | 133840 | 135140 |
| Static RAM | 16112 | 16152 |
| BIN | 134324 | {len(data)} |

+40 байт static RAM — символ `__malloc_current_mallinfo` размером 0x28, подключённый диагностикой кучи. Буферы HTTP не расширены; ClientContext по-прежнему 6120 (static_assert). Flash +1300 байт, включая загрузчик страницы/кеш и mallinfo.

BIN: `FLE4D_LOAD_1_0_10.bin`, приложение **0x08010000**. SHA-256 `{digest}`. Начальные векторы проверены: SP={stack:#010x}, reset={reset:#010x}. Это OTA-приложение для данного профиля, не образ загрузчика по 0x08000000. Есть предыдущий ROLLBACK_1_0_9_NOTICES.bin.

## Пересборка

Штатные RT_HW_00_BASE и Flprog_Utilites брать из IDE; в комплекте их нет. Приложены две изменённые проектные библиотеки и скетч с descriptor. Пины/сеть тестового скетча соответствуют FLE4D; в пользовательском FLProg-проекте берите их из проекта.

Редактируемые bootstrap-исходники: `web_assets/index.html`, `web_assets/loader.js`. Рабочая версия также в runtime/FLProg_WebUI/web_assets. После изменения: `tools/sync_loader_assets.py`, затем `tools/build_gzip_assets.py`, `tools/verify_release.py`, тесты и пересборка. Для уведомлений sync_notice_assets.py также запускать перед генератором gzip. Генератор и check_http_assets поддерживают новые helper calls.

Команда конкретной компиляции сохранена в command.json (локальные абсолютные пути требуют адаптации). Нужен FLE4D_30MT_OTA, build.flash_offset=0x10000, FLPROG_WEBUI_GZIP_ASSETS=1. Имя исходной папки скетча исторически FLE4D_NOTICES — версия в ней уже 1.0.10-LOAD. EXE редактора и общий архив обновлять отдельной командой после этой проверки.
'''
(P/'README.md').write_text(report,encoding='utf-8');(S/'LOAD_RU.md').write_text(report,encoding='utf-8')
p=S/'README_RU.md';s=p.read_text(encoding='utf-8');s=s.replace('# FLProg Web UI 1.0\n','# FLProg Web UI 1.0\n\n[Загрузка: прогресс, повторы чтения и кеширование; FLE4D 1.0.10](LOAD_RU.md).\n',1);p.write_text(s,encoding='utf-8')
p=S/'ROADMAP_RU.md';s=p.read_text(encoding='utf-8');s+='\n\n## Проверено 25.10.2026: загрузка и кеш\n\n1.0.10-LOAD: прогресс, ограниченные повторы GET без повторов команд, hash-version immutable cache, HTML/data no-store. На FLE4D проверены 400 чтений, 15 повторных открытий, команды и стабильная куча. Ограничение одного HTTP-клиента и первоначального TCP connect остаётся. Отчёт LOAD_RU.md; общий r12, EXE и Git пока не менялись.\n';p.write_text(s,encoding='utf-8')
for p in [B/'AGENTS.md',Path(r'E:\SAI\Правила для Codex\Проекты\FLProg_Network.md')]:
 with p.open('a',encoding='utf-8') as f:f.write('\n\n1.0.10-LOAD установлена и проверена на FLE4D: прогресс, bounded GET retry, хеш-версия статических ресурсов/immutable, HTML и данные no-store. 28 тестов, 20 ресурсов/14 маршрутов, 400 чтений и 15 browser reloads, heap_used7108 стабильно293samples. Flash135140/staticRAM16152 (+40 malloc diagnostics). Исходный WebUI в flprog_webui_next; новая Network/cache-policy только в _work/load_fle4d и Прошивки_для_проверки/FLE4D_LOAD_1.0.10. EXE/общий r12/Git не менялись. В следующем комплекте взять обе библиотеки из proof; сохранить таймаут close5000.\n')
entries={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in P.rglob('*')if p.is_file()};(P/'MANIFEST_SHA256.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'proof':str(P),'bin_sha256':digest,'files':len(entries)+1,'flash':135140,'static_ram':16152}))
