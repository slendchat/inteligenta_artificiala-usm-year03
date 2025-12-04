## Лаба 8 — планирование действий

### Структура
- `src/planner/state.py` — описание мира (5×5 сетка, база, ящики, препятствия) и правила переходов.
- `src/planner/search.py` — прямой, обратный и двунаправленный поиск с метриками.
- `src/planner/heuristics.py` — эвристики (число оставшихся ящиков, дистанции и т.д.).
- `src/planner/experiments.py` — запуск набора экспериментов и оценка коэффициента ветвления.
- `src/app.py` — приложение на Tkinter с визуализацией и UI.
- `src/tests/test_planner.py` — простые проверки на корректность алгоритмов.

### Как запустить
```bash
python3 -m venv .venv
source .venv/bin/activate
export PYTHONPATH=$(pwd)/lab08/src
python lab08/src/app.py
```

В окне можно выбрать алгоритм, запустить анимацию поиска, увидеть метрики, построить таблицу и график зависимости времени от коэффициента ветвления.

Тесты:
```bash
PYTHONPATH=lab08/src python -m unittest discover -s lab08/src/tests
```
