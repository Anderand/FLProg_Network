#!/usr/bin/env python3
"""Build the Russian FLProg Web UI Editor quick-start and FLProg guide."""
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle, KeepTogether)


NAVY = colors.HexColor("#10213a")
BLUE = colors.HexColor("#1769aa")
CYAN = colors.HexColor("#087e8b")
INK = colors.HexColor("#17243a")
MUTED = colors.HexColor("#52657c")
PALE = colors.HexColor("#edf4fa")
PALE_CYAN = colors.HexColor("#e7f5f5")
LINE = colors.HexColor("#c9d6e3")
WHITE = colors.white


def register_fonts():
    regular = Path(r"C:\Windows\Fonts\arial.ttf")
    bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if not regular.exists() or not bold.exists():
        raise SystemExit("Не найдены Arial fonts; PDF build requires Cyrillic TTF fonts")
    pdfmetrics.registerFont(TTFont("Guide", str(regular)))
    pdfmetrics.registerFont(TTFont("Guide-Bold", str(bold)))


def styles():
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle("Cover", parent=base["Title"], fontName="Guide-Bold", fontSize=25,
                                leading=31, textColor=WHITE, alignment=TA_LEFT, spaceAfter=8),
        "cover_sub": ParagraphStyle("CoverSub", fontName="Guide", fontSize=12, leading=18,
                                     textColor=colors.HexColor("#dceafa"), spaceAfter=8),
        "h1": ParagraphStyle("H1x", fontName="Guide-Bold", fontSize=18, leading=23,
                             textColor=NAVY, spaceBefore=3, spaceAfter=9),
        "h2": ParagraphStyle("H2x", fontName="Guide-Bold", fontSize=12, leading=16,
                             textColor=BLUE, spaceBefore=7, spaceAfter=5),
        "body": ParagraphStyle("Bodyx", fontName="Guide", fontSize=9.4, leading=13.2,
                               textColor=INK, spaceAfter=5),
        "small": ParagraphStyle("Smallx", fontName="Guide", fontSize=8.2, leading=11,
                                textColor=MUTED, spaceAfter=3),
        "cell": ParagraphStyle("Cellx", fontName="Guide", fontSize=8.1, leading=10.5,
                               textColor=INK, spaceAfter=0),
        "cell_b": ParagraphStyle("CellBx", fontName="Guide-Bold", fontSize=8.2, leading=10.5,
                                 textColor=NAVY, spaceAfter=0),
        "callout": ParagraphStyle("Calloutx", fontName="Guide-Bold", fontSize=10, leading=14,
                                   textColor=NAVY, spaceAfter=1),
        "mono": ParagraphStyle("Monox", fontName="Guide-Bold", fontSize=9, leading=13,
                               textColor=CYAN, leftIndent=8, spaceAfter=2),
        "center": ParagraphStyle("Centerx", fontName="Guide-Bold", fontSize=10, leading=13,
                                  textColor=NAVY, alignment=TA_CENTER),
    }


class GuideDoc(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                         topMargin=19*mm, bottomMargin=18*mm, **kwargs)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="main")
        self.addPageTemplates([PageTemplate(id="guide", frames=frame, onPage=self.draw_page)])

    def draw_page(self, canvas, doc):
        canvas.saveState()
        width, height = A4
        canvas.setFillColor(NAVY)
        canvas.rect(0, height-11*mm, width, 11*mm, stroke=0, fill=1)
        canvas.setFillColor(WHITE)
        canvas.setFont("Guide-Bold", 8)
        canvas.drawString(18*mm, height-7.2*mm, "FLProg Web UI  |  ПРАКТИЧЕСКАЯ ИНСТРУКЦИЯ")
        canvas.setStrokeColor(LINE)
        canvas.line(18*mm, 13*mm, width-18*mm, 13*mm)
        canvas.setFillColor(MUTED)
        canvas.setFont("Guide", 7.5)
        canvas.drawString(18*mm, 8.5*mm, "Редактор, блоки FBD, генерация скетча и прошивка")
        canvas.drawRightString(width-18*mm, 8.5*mm, "Страница %d" % doc.page)
        canvas.restoreState()


def P(text, style):
    return Paragraph(text, style)


def bullet(text, s):
    return Paragraph("•&nbsp;&nbsp;" + text, s["body"])


def card(content, bg=PALE, border=LINE, padding=9):
    t = Table([[content]], colWidths=[174*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.7, border),
        ("LEFTPADDING", (0, 0), (-1, -1), padding),
        ("RIGHTPADDING", (0, 0), (-1, -1), padding),
        ("TOPPADDING", (0, 0), (-1, -1), padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
    ]))
    return t


def grid_table(rows, widths, header=True):
    converted = []
    for r, row in enumerate(rows):
        style = "cell_b" if header and r == 0 else "cell"
        converted.append([Paragraph(str(cell), S[style]) for cell in row])
    t = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    rules = [
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        rules.extend([("BACKGROUND", (0, 0), (-1, 0), PALE),
                      ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#f8fafc")])])
    t.setStyle(TableStyle(rules))
    return t


def step(num, title, body, s):
    left = Table([[P(str(num), s["center"])]], colWidths=[10*mm], rowHeights=[10*mm])
    left.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CYAN),
                              ("BOX", (0, 0), (-1, -1), 0, CYAN),
                              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("TEXTCOLOR", (0, 0), (-1, -1), WHITE)]))
    body_cell = [P("<b>%s</b><br/>%s" % (title, body), s["body"])]
    table = Table([[left, body_cell]], colWidths=[13*mm, 161*mm])
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                               ("TOPPADDING", (0, 0), (-1, -1), 2),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return table


def build(path):
    register_fonts()
    global S
    S = styles()
    doc = GuideDoc(str(path), title="FLProg Web UI - инструкция по запуску и подключению",
                   author="FLProg Web UI")
    story = []

    # Page 1: portable editor and project package.
    hero = Table([[P("FLProg Web UI<br/>Запуск и подключение к FLProg", S["cover"])],
                  [P("От редактора проекта до работающей страницы на контроллере", S["cover_sub"])]],
                 colWidths=[174*mm])
    hero.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY),
                              ("LEFTPADDING", (0, 0), (-1, -1), 13),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 13),
                              ("TOPPADDING", (0, 0), (-1, -1), 11),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
    story += [Spacer(1, 12*mm), hero, Spacer(1, 8*mm),
              P("Короткий ответ: какой блок добавить?", S["h1"]),
              card(P("В FBD-проект добавьте <b>FLProg Web UI Configure &lt;ID&gt;</b> из сгенерированной библиотеки проекта. Это единственный обязательный блок запуска Web UI; разместите его <b>ровно один раз</b>. Для передачи значений между веб-страницей и логикой FBD используйте отдельные канальные блоки Publish/Command.", S["callout"]), PALE_CYAN, CYAN),
              Spacer(1, 6*mm), P("Что создаёт редактор", S["h2"]),
              grid_table([
                  ["Артефакт", "Зачем нужен", "Импортировать в FLProg"],
                  ["FLProg_WebUI_Project_&lt;ID&gt;", "Arduino package с descriptor и конфигуратором проекта", "Появляется после «Собрать и установить»"],
                  ["FLProg_WebUI_Configure_&lt;ID&gt;.ubi", "Подключает проектный descriptor и HTTP runtime к сетевому интерфейсу", "Да, один раз на проект"],
                  ["Универсальный комплект блоков (.ubl)", "Папка из 8 универсальных блоков каналов Publish/Command", "Да, один раз на FLProg"],
                  [".flpui", "Исходный дизайн конкретного проекта", "Открывается редактором, в FBD не импортируется"],
              ], [52*mm, 77*mm, 45*mm]),
              Spacer(1, 5*mm),
              P("Дизайн остаётся отдельным файлом проекта. Изменение подписей и раскладки не требует создавать блоки каналов заново.", S["small"]),
              PageBreak()]

    # Page 2: exact installation layout and data locations.
    story += [P("Где разместить редактор и где искать файлы", S["h1"]),
              P("Редактор — отдельная программа, а не часть FLProg_Network. Для передачи или установки копируйте всю папку редактора целиком.", S["body"]),
              grid_table([
                  ["Что", "Точный путь / правило"],
                  ["Папка поставки редактора", "E:\\smirnov\\FLProg_WebUI_Editor\\"],
                  ["Что запускать", "E:\\smirnov\\FLProg_WebUI_Editor\\Start_Editor.bat"],
                  ["Сам EXE", "E:\\smirnov\\FLProg_WebUI_Editor\\portable\\FLProg_WebUI_Editor\\FLProg_WebUI_Editor.exe"],
                  ["Обязательная папка рядом с EXE", "E:\\smirnov\\FLProg_WebUI_Editor\\portable\\FLProg_WebUI_Editor\\_internal\\"],
                  ["Файлы проекта редактора", "E:\\smirnov\\FLProg_WebUI_Editor\\portable\\FLProg_WebUI_Editor\\projects\\<ID>.flpui"],
                  ["Собранные project package", "E:\\smirnov\\FLProg_WebUI_Editor\\portable\\FLProg_WebUI_Editor\\project_packages\\FLProg_WebUI_Project_<ID>\\"],
                  ["Готовые библиотеки Андрея", "E:\\smirnov\\libraries\\FLProg_Network\\ и соседние папки библиотек"],
              ], [49*mm, 125*mm]),
              Spacer(1, 4*mm),
              card(P("Переносить нужно всю папку <b>FLProg_WebUI_Editor</b>, а не один EXE. Внутри папки EXE оставьте рядом <b>_internal</b>. Папки <b>projects</b> и <b>project_packages</b> создаются/используются редактором и содержат пользовательские данные — включайте их в резервную копию.", S["callout"]), PALE_CYAN, CYAN),
              Spacer(1, 4*mm), P("Куда редактор устанавливает пакет для FLProg", S["h2"]),
              P("При нажатии «Собрать и установить» редактор пытается скопировать проектную библиотеку в sketchbook FLProg. В текущей поставке путь по умолчанию:", S["body"]),
              P("C:\\FL\\FLProg_9.8.1_Windows_Portable\\ideV8\\portable\\sketchbook\\libraries\\", S["mono"]),
              P("После сборки там должна появиться папка <b>FLProg_WebUI_Project_&lt;ID&gt;</b>. Если FLProg установлен в другое место, готовый пакет берите из папки <b>project_packages</b> выше и копируйте целиком в папку <b>sketchbook\\libraries</b> фактически используемой portable-установки FLProg. Не кладите проектные данные в FLProg_Network.", S["body"]),
              P("В ту же папку sketchbook\\libraries должны быть установлены библиотеки <b>FLProg_WebUI</b> и <b>FLProg_Network</b>. Готовая копия библиотек для Андрея находится в <b>E:\\smirnov\\libraries\\</b>; копируйте библиотечные папки целиком, не объединяйте вручную с одноимённой старой версией.", S["body"]),
              card(P("Важно про «Открыть» и «Сохранить»: выбранный .flpui можно открыть из любой папки, но команда «Сохранить» записывает рабочую копию в <b>portable\\FLProg_WebUI_Editor\\projects\\&lt;ID&gt;.flpui</b>. Внешний исходный файл автоматически не перезаписывается. Собранный пакет появляется в соседней папке <b>project_packages</b>, а затем копируется в sketchbook\\libraries, если путь найден.", S["body"]), colors.HexColor("#fff6e8"), colors.HexColor("#e6a23c")),
              PageBreak()]

    # Page 3: launch and build in editor.
    story += [P("1. Запустить редактор и собрать пакет", S["h1"]),
              step(1, "Распакуйте папку редактора целиком", "Не переносите EXE отдельно: рядом с ним нужна папка <b>_internal</b>. В готовой поставке запускайте <b>Start_Editor.bat</b>; он сам найдёт переносимый EXE. Отдельный Python устанавливать не надо.", S),
              step(2, "Откройте проект", "Запустите <b>E:\\smirnov\\FLProg_WebUI_Editor\\Start_Editor.bat</b>. Редактор откроет браузер по адресу <b>http://127.0.0.1:8766/</b>. Окно программы/консоли оставьте открытым, пока работаете. Нажмите «Демо» или «Открыть» и выберите файл <b>.flpui</b>.", S),
              step(3, "Проверьте ID и транспорт", "ID проекта должен совпадать с именем создаваемого пакета. Для Wi-Fi выберите Wi-Fi HTTP. В FLProg затем должен быть добавлен интерфейс FLProg_Network того же типа.", S),
              step(4, "Сохраните проект", "Сохраните файл <b>.flpui</b> отдельно от библиотек. Это исходный дизайн, его стоит хранить вместе с FBD-проектом.", S),
              step(5, "Соберите и установите", "Нажмите «Собрать и установить». Редактор создаст <b>FLProg_WebUI_Project_&lt;ID&gt;</b> и скопирует его в sketchbook/libraries, если папка библиотек найдена. Запомните путь из сообщения редактора.", S),
              Spacer(1, 4*mm), P("Где находятся два нужных файла", S["h2"]),
              grid_table([
                  ["Файл", "Путь"],
                  ["Универсальный комплект блоков", "sketchbook\\libraries\\FLProg_WebUI\\user_blocks\\FLProg_WebUI_Universal_Blocks.ubl"],
                  ["Конфигуратор конкретного проекта", "sketchbook\\libraries\\FLProg_WebUI_Project_&lt;ID&gt;\\<br/>FLProg_WebUI_Configure_&lt;ID&gt;.ubi"],
              ], [65*mm, 109*mm]),
              Spacer(1, 5*mm),
              card(P("Если FLProg открыт во время установки пакета, закройте и снова запустите его, чтобы обновить список пользовательских библиотек.", S["body"])),
              PageBreak()]

    # Page 4: imports and exact configure block.
    story += [P("2. Импортировать блоки и включить Web UI", S["h1"]),
              P("В комплекте два разных вида пользовательских блоков. Их нельзя заменять друг другом:", S["body"]),
              grid_table([
                  ["Блок", "Откуда", "Сколько добавлять"],
                  ["FLProg Web UI Configure &lt;ID&gt;", "Из созданного пакета проекта .ubi", "Один блок в каждом FBD-проекте"],
                  ["FLProg Web UI Publish/Command ...", "Из общей папки .ubl", "По одному блоку на используемый канал/направление"],
                  ["Wi-Fi STA / другой интерфейс", "Из FLProg_Network", "Обычный сетевой блок проекта; соответствует выбранному транспорту"],
              ], [53*mm, 76*mm, 45*mm]),
              Spacer(1, 5*mm), P("Последовательность в FLProg", S["h2"]),
              card(P("<b>1.</b> Добавьте сетевой интерфейс FLProg_Network и задайте Wi-Fi/сеть.<br/><br/><b>2.</b> Импортируйте <b>FLProg_WebUI_Universal_Blocks.ubl</b> один раз. FLProg добавит папку <b>FLProg Web UI</b> со всеми типами блоков.<br/><br/><b>3.</b> Импортируйте <b>FLProg_WebUI_Configure_&lt;ID&gt;.ubi</b> из пакета проекта.<br/><br/><b>4.</b> Поместите <b>FLProg Web UI Configure &lt;ID&gt;</b> в FBD ровно один раз. Он генерирует код конфигурации в setup; к циклу и переменным его подключать не нужно.<br/><br/><b>5.</b> Добавьте нужные Publish/Command блоки и свяжите их с логикой проекта.", S["body"]), PALE, BLUE),
              Spacer(1, 5*mm),
              card(P("Не добавляйте общий блок «Web UI Core» или второй проектный Configure. Проектный блок уже включает descriptor и HTTP-адаптер. Повторное размещение может дать повторные объявления или запуск сервера.", S["callout"]), colors.HexColor("#fff6e8"), colors.HexColor("#e6a23c")),
              Spacer(1, 5*mm), P("Транспорт должен совпадать", S["h2"]),
              P("Для сборки Wi-Fi-проекта в редакторе выберите Wi-Fi HTTP и добавьте в FLProg Wi-Fi STA. Проектный UBI содержит выбранную привязку интерфейса. Если поменяли транспорт, пересоберите пакет и импортируйте новый UBI.", S["body"]),
              PageBreak()]

    # Page 5: channel blocks, pin definitions and example.
    story += [P("3. Подключить каналы FBD к виджетам", S["h1"]),
              P("Универсальные блоки не создаются заново при каждом изменении дизайна. Они обращаются к канальной модели по числовому номеру CHANNEL.", S["body"]),
              grid_table([
                  ["Направление в редакторе", "Какой блок взять", "Пины и смысл"],
                  ["publish", "Publish Bool / Int / Float / Text", "Входы EN, CHANNEL, VALUE. VALUE отправляется из FBD на страницу."],
                  ["command", "Command Bool / Int / Float / Text", "Входы EN, CHANNEL; выходы NEW, VALUE. NEW - импульс одного цикла при новой команде с веба."],
                  ["duplex", "Publish и Command одного типа", "Одинаковый CHANNEL у обоих. FBD публикует фактическое значение и отдельно принимает команду."],
              ], [39*mm, 59*mm, 76*mm]),
              Spacer(1, 5*mm), P("Как выбрать номер канала", S["h2"]),
              bullet("Откройте список каналов слева в редакторе и возьмите показанный номер №N.", S),
              bullet("Номера API FLProg_Network резервируются в диапазоне 0-100; пользовательские каналы начинаются с 101.", S),
              bullet("Вход CHANNEL должен получить именно номер из редактора, а не индекс строки/массива и не текстовый ID канала.", S),
              Spacer(1, 3*mm), P("Пример: двусторонний переключатель света", S["h2"]),
              card(P("В демо канал <b>light</b> имеет тип Bool, направление duplex и номер <b>102</b>.<br/><br/><b>Command Bool:</b> EN = true, CHANNEL = 102. Подключите NEW как признак нового события, а VALUE обработайте в логике включения/выключения.<br/><br/><b>Publish Bool:</b> EN = true, CHANNEL = 102, VALUE = фактическое состояние выхода/реле. Так страница покажет реальное состояние после обработки команды.", S["body"]), PALE_CYAN, CYAN),
              Spacer(1, 4*mm),
              card(P("Для Float, Int и Text используйте блок того же типа, что задан у канала. Неверное сочетание типа или направления обычно приводит к тому, что команда не принимается или значение не отображается.", S["body"])),
              PageBreak()]

    # Page 6: compile and troubleshoot.
    story += [P("4. Скомпилировать, прошить, проверить", S["h1"]),
              step(1, "Проверьте состав FBD", "Сетевой интерфейс FLProg_Network присутствует; проектный Configure добавлен ровно один раз; номера CHANNEL и типы блоков совпадают с каналами в редакторе.", S),
              step(2, "Сгенерируйте скетч в FLProg", "Выполните штатную генерацию Arduino-скетча средствами FLProg. Это создаёт .ino с кодом интерфейса и пользовательских блоков.", S),
              step(3, "Скомпилируйте и загрузите", "Откройте сгенерированный скетч в Arduino IDE, выберите ту же плату и COM-порт, нажмите «Проверить/Скомпилировать», затем «Загрузить». Дождитесь окончания прошивки.", S),
              step(4, "Откройте страницу контроллера", "Посмотрите IP в настройках/диагностике FLProg_Network или Serial Monitor и откройте его в браузере устройства в той же локальной сети.", S),
              Spacer(1, 4*mm), P("Типовые ошибки", S["h2"]),
              grid_table([
                  ["Симптом", "Что проверить"],
                  ["demo_controller_descriptor.h not found", "Проектный пакет установлен в sketchbook/libraries; выбран правильный ID и сгенерированный Configure-блок импортирован из этого пакета."],
                  ["FLProgWebUi...PagedHttp.h not found", "Установлены FLProg_WebUI и FLProg_Network рядом в sketchbook/libraries; перезапустите Arduino IDE/FLProg."],
                  ["FLPROG_WIFI_INTERFACE1 не объявлен", "Добавлен сетевой интерфейс Wi-Fi STA; транспорт в редакторе соответствует интерфейсу в FBD. Пересоберите и повторно импортируйте проектный UBI после изменения транспорта."],
                  ["Веб открывается, но значение не меняется", "Проверьте CHANNEL, тип блока, EN=true, направление канала, подключение VALUE; для duplex используйте пару Publish+Command."],
                  ["В FLProg нет папки блоков", "Импортируйте именно общий .ubl целиком или нужный проектный .ubi; затем перезапустите FLProg."],
              ], [56*mm, 118*mm]),
              Spacer(1, 4*mm),
              card(P("Изменили только подпись, цвет, размер или расположение? Откройте прежний .flpui, пересоберите пакет, сгенерируйте скетч и снова прошейте. Универсальный .ubl и уже импортированные канальные блоки повторно добавлять не нужно.", S["callout"]), PALE_CYAN, CYAN)]

    doc.build(story)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: build_editor_instruction_pdf.py OUTPUT.pdf")
    output = Path(sys.argv[1]).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    build(output)
    print(output)
