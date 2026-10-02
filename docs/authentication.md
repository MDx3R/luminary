# Авторизация через Zitadel

Вход и регистрация выполняются в Zitadel. Единственная публичная точка входа —
nginx; oauth2-proxy проверяет сессию, а приложение получает проверенный `sub`
через `X-User-Id`. `X-Username` и `Authorization` nginx также перезаписывает.
API не выпускает собственные JWT и не хранит пароли.

## Первый запуск

Базовый compose предназначен для локальной разработки: HTTP на `127.0.0.1:80`.
Не публикуйте его в интернет. Для сервера настройте HTTPS на этом же nginx,
публичные домены, secure cookies и HTTPS URL во всех настройках Zitadel/proxy.
Traefik рассмотрен, но nginx сохранён: он уже используется и поддерживает
необходимый h2c upstream через `grpc_pass`. Второго публичного прокси нет.

1. Скопируйте `.env.example` в `.env`, заполните существующие настройки приложения.
2. Заполните новые секреты. Для `ZITADEL_MASTERKEY` используйте вывод
   `openssl rand -hex 16` (ровно 32 символа). Для паролей БД и cookie secrets —
   отдельные результаты `openssl rand -base64 32`. Начальный пароль администратора
   должен содержать строчную и заглавную буквы, цифру и специальный символ.
   Храните master key вместе с резервной копией БД; не меняйте его на существующем томе.
3. Создайте сеть `docker network create luminary`, если она ещё не существует.
4. Поднимите Zitadel и прокси из того же compose:

   ```sh
   docker compose up -d zitadel-login nginx
   ```

5. Откройте `http://zitadel.localhost/ui/console`. Если система не разрешает
   `zitadel.localhost`, добавьте `127.0.0.1 zitadel.localhost` в hosts.
   Начальная учётная запись — `zitadel-admin@zitadel.zitadel.localhost`;
   используйте пароль из `ZITADEL_ADMIN_PASSWORD` и смените его по запросу.
6. Создайте проект Luminary и OIDC-приложение: **Web**, **Authorization Code**,
   способ аутентификации **BASIC**. Для локального HTTP включите development mode.
   Разрешённый redirect URI: `http://localhost/oauth2/callback`.
   Сохраните Client ID и Client Secret в `OAUTH2_PROXY_CLIENT_ID` и
   `OAUTH2_PROXY_CLIENT_SECRET`. У пользователя должны быть имя и подтверждённый email.
7. Проверьте в Login Behavior, что самостоятельная регистрация разрешена.
   Compose включает её при первоначальном setup; настройки уже существующего
   экземпляра меняются через консоль Zitadel.
   Для подтверждения email новых пользователей настройте SMTP в настройках
   уведомлений Zitadel. Проверка подтверждённого email в oauth2-proxy остаётся включённой.
8. Запустите весь стек:

   ```sh
   docker compose up -d --build
   ```

9. Откройте `http://localhost/oauth2/start`. После входа `/users/me` вернёт
   `{ "id": "локальный UUID", "name": "имя", "email": "email" }`.

Для повторного запуска достаточно последней команды compose. Init/setup
идемпотентны; БД приложения и Zitadel имеют отдельные контейнеры и тома.
Не используйте `make reset` для сохранения данных: эта существующая команда удаляет тома.
Секреты и PAT-файлы не коммитятся. Login PAT находится в Docker volume;
до даты `ZITADEL_LOGIN_PAT_EXPIRATION` его нужно перевыпустить в Zitadel.

## Профиль и существующие пользователи

Миграция `7b94c2e81a06` переименовывает `identities` в `users`, сохраняет UUID,
добавляет уникальный `zitadel_sub` и email. Старые пользователи остаются без `sub`
до явной привязки. Парольные хеши и локальные токены удаляются. Перед миграцией
сделайте резервную копию: downgrade не может восстановить удалённые учётные данные.

Администратор проверяет соответствие старой учётной записи пользователю Zitadel
и **до первого входа этого пользователя в Luminary** выполняет:

```sh
docker compose exec app poetry run python -m cli.users.link \
  --user-id OLD_LOCAL_UUID --subject ZITADEL_SUB
```

Команда отказывает, если UUID отсутствует, уже привязан или `sub` занят другим
пользователем. Совпадение имени/email не является основанием для автоматического
объединения аккаунтов. Если новый профиль уже создан, остановитесь и отдельно
спланируйте перенос его данных: команда не перезаписывает чужую привязку.

Для нового `sub` запись создаётся атомарным upsert; конкурентные запросы получают
один UUID. Имя/email синхронизируются через настроенный UserInfo endpoint Zitadel
с access token. Ответ должен содержать тот же `sub`, что передал прокси. Это
работает и с opaque access tokens; приложение не декодирует непроверенный JWT.
Недоступность провайдера возвращает `503`, отклонённый токен — `401`.

## Контракт для фронтенда

Реализован серверный Authorization Code flow oauth2-proxy с PKCE S256 и HttpOnly
cookie. Фронтенд на том же origin делает запросы с cookie; при `401` направляет
браузер на `/oauth2/start`. API самостоятельно не перенаправляет на HTML-страницу входа.
После истечения часовой cookie нужна новая авторизация; сессия Zitadel может
позволить войти повторно без ввода пароля.

`/oauth2/sign_out` удаляет сессию proxy, но не завершает глобальную сессию Zitadel.
Для полного выхода используйте также OIDC end-session flow Zitadel с разрешённым
post-logout redirect URI. Старые `/auth/login`, `/auth/refresh`, `/auth/logout` и
`/users/register` удалены.

Упомянутый в issue React `react-oidc-context` предполагает отдельный SPA-клиент.
В этом backend нет React-приложения. Его самостоятельный bearer flow не включён:
не передавайте SPA client secret в браузер и не смешивайте его с Web-клиентом proxy.

## Проверки

```sh
poetry run pytest -q tests/unit/user
poetry run pytest -q tests/integration/sqlalchemy/test_user_repository.py tests/integration/sqlalchemy/test_zitadel_migration.py
poetry run pytest -q tests/integration/auth
RUN_ZITADEL_SMOKE=1 poetry run pytest -q tests/integration/auth/test_zitadel_stack.py
make ci
poetry run ruff format --check src tests cli
poetry run black --check src tests cli
```

Интеграционные тесты требуют Docker и создают временные контейнеры. Тесты nginx
используют управляемый auth responder, чтобы проверить подмену заголовков и маршруты;
они не заменяют проверку реального входа в Zitadel.
Отдельный smoke-тест запускает настоящий Zitadel, Login UI и oauth2-proxy с
одноразовой БД, проверяет discovery, доступность Login UI, `401` и перенаправление
Authorization Code + PKCE. Он не выполняет интерактивный вход пользователя и
обмен authorization code: для этого нужен настроенный Web-клиент из инструкции выше.

На запущенном стеке проверьте:

- `GET /users/me` без cookie возвращает `401`, в том числе с поддельными
  `X-User-Id`, `X-Username` и `Authorization`.
- После `/oauth2/start` профиль доступен, повторный вход сохраняет UUID.
- Другой пользователь не получает доступ к чужим чатам/папкам/источникам.
- `GET /api/v1/assistants/public` работает без входа.
- У приложения, oauth2-proxy и Zitadel нет опубликованных портов в `docker compose ps`.
- Привязанный старый пользователь видит прежние данные.

## Источники

- https://zitadel.com/docs/self-hosting/deploy/compose
- https://zitadel.com/docs/self-hosting/manage/reverseproxy/nginx
- https://zitadel.com/docs/examples/identity-proxy/oauth2-proxy
- https://oauth2-proxy.github.io/oauth2-proxy/configuration/overview/
