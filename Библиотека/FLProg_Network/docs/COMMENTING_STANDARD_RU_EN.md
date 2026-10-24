# Стандарт комментариев / Commenting standard

## Русский

Каждый исходный файл `src/**/*.h` и `src/**/*.cpp`, а также каждый executable
пример, содержит два слоя комментариев.

1. **Назначение и архитектурные заметки.** Они объясняют роль модуля в
   FLProg_Network, его границу ответственности и причину важных решений.
2. **Расширенный контракт сопровождения.** Он фиксирует владельца состояния,
   порядок вызовов, cooperative lifecycle, profile/platform границы и условия,
   при которых изменение требует отдельного compatibility или hardware gate.

Комментарии не повторяют построчно код и не заменяют API reference. При
изменении поведения разработчик обновляет оба языковых варианта в том же
изменении. Описание `.md`, отчёты, `library.properties`, `keywords.txt` и
изображения являются данными/документацией, а не исходным кодом; в них вместо
искусственных комментариев поддерживаются заголовки, дата, статус и история.

## English

Every `src/**/*.h` and `src/**/*.cpp` source file, plus every executable
example, carries two comment layers.

1. **Purpose and architecture notes.** They explain the module role in
   FLProg_Network, its responsibility boundary and the reason for important
   decisions.
2. **Extended maintenance contract.** It records state ownership, call order,
   the cooperative lifecycle, profile/platform boundaries and cases where a
   change requires a separate compatibility or hardware gate.

Comments do not repeat code line by line and do not replace the API reference.
When behavior changes, the developer updates both language variants in the
same change. Markdown documents, reports, `library.properties`, `keywords.txt`
and images are documentation/data rather than source code; they keep headings,
dates, status and history instead of artificial comments.
