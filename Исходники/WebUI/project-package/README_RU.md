# Пакет одного FLProg Web UI проекта

Этот каталог будет шаблоном для результата редактора. Он принадлежит одному
проекту и не размещается в `FLProg_Network`.

При выпуске редактор создаст:

```text
<проект>/webui/<id>.flpui
<проект>/webui/<id>.fvl
<sketchbook>/libraries/FLProg_WebUI_Project_<id>/src/<id>_descriptor.h
```

Постоянный конфигурационный блок подключает этот descriptor один раз. Обычная
правка дизайна обновляет только descriptor и не затрагивает FBD-схему.
