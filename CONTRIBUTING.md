# Contributing

Ветка `main` защищена. Прямой push в неё запрещён, история линейная. Изменения попадают в `main` только через pull request: одно одобрение, треды ревью закрыты. Из способов вливания в ruleset разрешены merge, squash и rebase; при линейной истории подходят squash и rebase.

Ветку создавайте от актуального `main`. Один PR — одна задача. В описании PR — что изменено и зачем, со ссылкой на задачу, если она есть.

## Окружение

Python 3.11+, Poetry, GNU Make.

```sh
make install
```

Команда проверяет lockfile, ставит зависимости и включает pre-commit. Хуки при коммите: `ruff --fix`, `ruff-format`, `mypy`.

Пересоздать контейнеры и тома: `make reset`. Сеть `luminary` и `.env` должны уже быть, как в README.

## Проверки

Локально то же, что job `test` в `.github/workflows/ci.yml`, без установки зависимостей и без Gitleaks:

```sh
make ci
```

Отдельные цели: `make lint`, `make typecheck`, `make test`, `make check-lock`. Дополнительно, вне CI: `make bandit`, `make xenon`, `make detect-secrets`.

В GitHub Actions перед тестами запускается Gitleaks (`.gitleaks.toml`). Секреты в репозиторий не коммитить.

Новое поведение покрывайте тестами.

## Стиль

Как в `pyproject.toml` и в CI: Ruff (линт и формат) и mypy (`strict`). Не обходить проверки без причины в том же PR.
