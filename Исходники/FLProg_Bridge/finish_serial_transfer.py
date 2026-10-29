# coding: utf-8
"""Stage a new transfer revision, leaving running applications unchanged."""
import hashlib,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parent.parent;B=Path(r'E:\SAI\FLProg_Network');U=B/'_work/bridge_web_20261028/user4'
old=B/'releases/FLProg_Network_FLE4D_1.0.8_COM_2026-10-28'
out=old.parent/(old.name+'_r2');assert not out.exists();shutil.copytree(old,out)
shutil.copytree(U/'serial_manager_dist/FLProg_Firmware_Manager',out/'Менеджер_прошивок',dirs_exist_ok=True)
m=R/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER'
target=out/'Исходники/hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER'
for f in m.glob('*.py'):shutil.copy2(f,target/f.name)
shutil.copy2(R/'flprog_webui_next/tools/bridge_launcher.py',out/'Исходники/flprog_webui_next/tools/bridge_launcher.py')
shutil.copy2(R/'flprog_bridge/MANAGER_RU.md',out/'Менеджер_прошивок/README_RU.md')
shutil.copy2(R/'flprog_bridge/MANAGER_RU.md',out/'Документация/МЕНЕДЖЕР_COM_UART.md')
chapter='''## Выбор COM и первичная прошивка

В менеджере0.8.0-preview.4 откройте вкладку **COM / UART** (или одноимённую
кнопку вверху). Здесь выбираются COM-порт и скорость, обновляется список портов
и запускается отдельный веб-мост с выбранными параметрами.

Ниже находятся кнопки проверки ROM-загрузчика и первичной записи загрузчика
с приложением по UART. Профиль и STM32CubeProgrammer CLI выбираются на вкладке
«Прошивка». IP-адрес для UART и первичной SWD-записи не нужен.

**Для STM32F407 UART6 не поддерживается системным загрузчиком.** Для первичной
UART-записи подключите USART1 PA9/PA10 либо USART3 PB10/PB11 (также PC10/PC11),
войдите в ROM: BOOT0=1, BOOT1=0, RESET. Проверьте ROM, затем запишите образы.
После успешной проверки записи верните BOOT0=0 и нажмите RESET.
ROM использует8E1; наш веб-мост на UART6 использует8N1. Это разные способы работы.
Фактическую разводку TTL-выводов смотрите по схеме платы; RS-485 не является TTL UART.

Перед записью проверяются Device ID и размер Flash, каждый образ проверяется
после записи. При ошибке запись не повторяется. Функция первичной UART-записи
проверена8программными тестами и осмотром GUI, на реальном ROM UART ещё не испытана.
[Подробное руководство](Документация/МЕНЕДЖЕР_COM_UART.md).

'''
for f in ('Инструкция.md','ПРОЧИТАТЬ.md'):
 p=out/f;text=p.read_text(encoding='utf-8').replace('0.8.0-preview.3','0.8.0-preview.4').replace('## Веб через COM без Ethernet',chapter+'## Веб через COM без Ethernet');p.write_text(text,encoding='utf-8')
shutil.copy2(U/'SERIAL_MANAGER_TESTS.log',out/'Проверки/SERIAL_MANAGER_TESTS.log')
(out/'Проверки/МЕНЕДЖЕР_COM_UART.md').write_text('# Проверка COM / UART\n\n8 программных тестов прошли: отсутствие записи при проверке, адреса двух образов, verify, остановка при неверных Device ID/Flash, отсутствие повторов после ошибки, проверка порта/скорости, передача параметров мосту и SWD без IP.\n\nПервичная аппаратная UART-прошивка не выполнялась. Для F407 текущий UART6 веб-моста не подходит ROM-загрузчику. Обновление программы не прошивает и не сбрасывает ПЛК.\n',encoding='utf-8')
assert hashlib.sha256((out/'Менеджер_прошивок/profiles/fle4d_30mt_profile_1_0_8/application.bin').read_bytes()).hexdigest()=='4c4763e1c9b2179037567b12d241750a7453b069f2f8afb899cb877ac5080176'
(U/'SERIAL_TRANSFER_READY.json').write_text(json.dumps(dict(folder=str(out),manager_version='0.8.0-preview.4',uart_hardware_tested=False),ensure_ascii=False,indent=2),encoding='utf-8')
print(str(out))
