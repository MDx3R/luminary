# Авторизация через Zitadel

Вход и регистрация выполняются в Zitadel. Единственная публичная точка входа —
nginx; oauth2-proxy проверяет сессию, а приложение получает проверенный профиль
через заголовки nginx. API не получает токены или cookies, не обращается к Zitadel,
не выпускает собственные JWT и не хранит пароли.

## Контракт прокси и бэкенда

nginx выполняет `auth_request` к внутреннему `/oauth2/auth`. Cookies браузера
передаются только oauth2-proxy, который отвечает за OIDC и проверку сессии.
После успешной проверки nginx заменяет клиентские значения следующими:

| Заголовок бэкенду | Проверенное поле сессии oauth2-proxy |
| --- | --- |
| `X-User-Id` | `sub` (поле `user` сессии OIDC-провайдера) |
| `X-Username` | `preferred_username` |
| `X-User-Name` | `name` — отображаемое имя, не подмена его username |
| `X-Email` | `email` |

Для `name` используется `additionalClaims` и `injectResponseHeaders` в
`oauth2-proxy/oauth2-proxy.yaml`. Это структурированная alpha-конфигурация
закреплённой версии **v7.15.0**; обновление образа требует повторной проверки
совместимости. Общие настройки cookies остаются в `oauth2-proxy.cfg`.
Устаревший параметр `userIDClaim: sub` намеренно не задаётся: в этой версии он
переопределяет источник **email**, а не `session.user`, и мешает проверке
`email_verified`. OIDC-провайдер и без него использует `sub` для идентификатора;
это проверяется интеграционным тестом с различающимися `sub` и email.
Client ID/Secret по-прежнему задаются в `.env` как `OAUTH2_PROXY_CLIENT_ID` и
`OAUTH2_PROXY_CLIENT_SECRET`; Compose передаёт их шаблону YAML под внутренними
именами `LUMINARY_OIDC_CLIENT_ID` и `LUMINARY_OIDC_CLIENT_SECRET`.

До передачи запроса бэкенду nginx удаляет `Authorization`, `Cookie`,
`Proxy-Authorization`, `X-Forwarded-Access-Token` и `X-Auth-Request-Access-Token`.
Публичный каталог дополнительно получает запрос без четырёх заголовков профиля.
Бэкенд проверяет полноту и отсутствие дубликатов заголовков, сопоставляет внешний
`sub` с локальным UUID и проверяет права на данные. Заголовки профиля передаются
как UTF-8; бэкенд декодирует их из байтов ASGI, включая имена на кириллице.

**Граница доверия:** доступ к порту бэкенда должен быть только у доверенной
инфраструктуры. Отсутствие опубликованного порта не изолирует его от других
контейнеров в той же Docker-сети. Не подключайте недоверенные контейнеры к сети
`luminary`, не публикуйте порт приложения и не направляйте клиентов к нему
в обход nginx. Бэкенд не проверяет криптографическую подлинность заголовков.

Проверка cookie-сессии в oauth2-proxy не означает интроспекцию токена в Zitadel
на каждом API-запросе. Немедленный отзыв доступа в Zitadel не гарантируется
этим контрактом; учитывайте срок жизни сессии и выбранную политику её проверки.

## Первый запуск

Базовый compose предназначен для локальной разработки: HTTP на `127.0.0.1:80`.
Не публикуйте его в интернет. Для сервера настройте HTTPS на этом же nginx,
публичные домены, secure cookies и HTTPS URL во всех настройках Zitadel/proxy.
Traefik рассмотрен, но nginx сохранён: он уже используется и поддерживает
необходимый h2c upstream через `grpc_pass`. Второго публичного прокси нет.

1. Скопируйте `.env.example` в `.env`, заполните существующие настройки приложения.
2. Заполните новые секреты. Для `ZITADEL_MASTERKEY` используйте вывод
   `openssl rand -hex 16` (ровно 32 символа). Для `ZITADEL_DB_PASSWORD`,
   `ZITADEL_DB_ADMIN_PASSWORD` и `ZITADEL_LOGIN_COOKIE_SECRET` используйте
   отдельные результаты `openssl rand -base64 32`.
   Для `OAUTH2_PROXY_COOKIE_SECRET` нужен отдельный ключ из 32 случайных байт
   в URL-safe Base64:

   ```sh
   openssl rand -base64 32 | tr '+/' '-_'
   ```

   Скопируйте результат в `OAUTH2_PROXY_COOKIE_SECRET` в локальном `.env`.
   Завершающий `=` допустим. Обычный Base64 может содержать `+` или `/`,
   из-за которых oauth2-proxy не декодирует ключ и отказывается запускаться.
   Если такой ключ уже создан, замените в нём `+` на `-` и `/` на `_`;
   остальные секреты не меняйте. Значения секретов не коммитятся.
   Начальный пароль администратора
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

После обновления с версии, где бэкенд обращался к UserInfo, пересоздайте
`app`, `nginx` и `oauth2-proxy` через `docker compose up -d --build`.
Выйдите через `/oauth2/sign_out` и войдите заново: старая cookie может не содержать
дополнительный claim `name`. UUID и миграция пользователей не меняются.
Переменная `OIDC__USERINFO_URL` больше не используется и может быть удалена из `.env`.

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
один UUID. Имя/email обновляются из проверенного профиля сессии, переданного
прокси. Изменение профиля в Zitadel может потребовать повторного входа, чтобы
обновить снимок профиля в cookie. Бэкенд не обрабатывает JWT, opaque access tokens
или ошибки Zitadel; неполный профиль от прокси возвращает `401`.

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
`test_oauth2_proxy.py` дополнительно запускает настоящий oauth2-proxy с тестовым
OIDC-провайдером и одноразовым RSA-ключом. Он проверяет обмен authorization code,
создание сессии, передачу имени/email без токенов/cookies, выход, отказ при
неверной подписи и неподтверждённом email. Этот тест не использует реальные
учётные записи и не подменяет пользовательскую проверку Login UI Zitadel.
Отдельный smoke-тест запускает настоящий Zitadel, Login UI и oauth2-proxy с
одноразовой БД, проверяет discovery, доступность Login UI, `401` и перенаправление
Authorization Code + PKCE. Он не выполняет интерактивный вход пользователя и
обмен authorization code: для этого нужен настроенный Web-клиент из инструкции выше.

На запущенном стеке проверьте:

- `GET /users/me` без cookie возвращает `401`, в том числе с поддельными
  `X-User-Id`, `X-Username` и `Authorization`.
- После `/oauth2/start` профиль доступен, повторный вход сохраняет UUID.
- `/users/me.name` соответствует отображаемому имени, а email — профилю Zitadel.
- После `/oauth2/sign_out` запрос `/users/me` без новой авторизации возвращает `401`.
- Другой пользователь не получает доступ к чужим чатам/папкам/источникам.
- `GET /api/v1/assistants/public` работает без входа.
- У приложения, oauth2-proxy и Zitadel нет опубликованных портов в `docker compose ps`.
- Привязанный старый пользователь видит прежние данные.

## Источники

- https://zitadel.com/docs/self-hosting/deploy/compose
- https://zitadel.com/docs/self-hosting/manage/reverseproxy/nginx
- https://zitadel.com/docs/examples/identity-proxy/oauth2-proxy
- https://oauth2-proxy.github.io/oauth2-proxy/configuration/overview/
- https://oauth2-proxy.github.io/oauth2-proxy/configuration/alpha-config/
