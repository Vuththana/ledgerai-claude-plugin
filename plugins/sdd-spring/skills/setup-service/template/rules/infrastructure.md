# Shared infrastructure: one set for every service

PostgreSQL, Keycloak, Consul, Redis, RustFS, Mailpit, Zipkin and the api-gateway run **once** and every service shares them, on the Docker network `ledgervision-net`. Where they live and every port: `docs/TRD.md` §1b. For now they live in the **identity-service** repo, folder `infra/`.

## In identity-service: this repo owns `infra/`

- A change under `infra/` reaches every service. Keep it backward compatible and call it out in the pull request.
- `infra/consul/application*.yml` holds only what every service shares. identity-service's own settings go in `consul/identity-service*.yml`.
- A new service's routes go in `infra/consul/api-gateway.yml` (`lb://<service-name>`, the paths from `docs/TRD.md` §1).

## In any other service repo (sales-service, finance-service, ...)

**Never add shared containers or shared config here**: no Postgres, Keycloak, Consul, Redis, RabbitMQ, RustFS, Mailpit, Zipkin or gateway in this repo's compose file, and no copy of `infra/`. A second copy breaks tokens, service discovery and the shared data. Start the shared set from a clone of identity-service, next to this repo:

```bash
cd ../ledgervision-identity-service
docker start postgres   # or, the first time: docker compose -f infra/docker-compose.yml --profile db up -d postgres
docker compose -f infra/docker-compose.yml up -d --no-recreate keycloak consul consul-seed-shared redis rustfs rustfs-init mailpit zipkin api-gateway
```

This repo holds only the service. Copy the pattern from identity-service's files:

| File | What it holds |
|---|---|
| `src/main/resources/application.yml` | Bootstrap only: `spring.application.name` = the Consul name in the gateway's routes, `server.port` from `docs/TRD.md` §1b, the Consul address, `consul:` import except in tests, and the `dev` profile's `discovery.hostname: host.docker.internal` (so the gateway in Docker reaches `bootRun`) |
| `consul/<service>.yml` | This service's settings (`config/<service>/data`): datasource with `currentSchema=<schema>`, Flyway schema, anything only it uses. Shared settings (Keycloak issuer, Redis, mail, Zipkin, S3) already come from `config/application/data` |
| `consul/<service>-docker.yml` | Its Docker overrides (`config/<service>,docker/data`), e.g. the datasource host |
| `docker-compose.yml` | Only this service and its `consul-seed` job, on the network `ledgervision-net` declared `external: true`, `env_file: .env`, and `DB_HOST` overridden for the container (`host.docker.internal`; `.env`'s `localhost` is for `bootRun`) |
| `.env.example` | Every variable the service reads, placeholders only. `.env` is git-ignored |

Run it: `docker compose up -d consul-seed` (after every Consul restart), then `./gradlew bootRun`. Check that it shows green in Consul (http://localhost:8500) and answers through the gateway (`http://localhost:8080/api/v1/<its path>`).

**Need something shared changed** (a new container such as RabbitMQ, a shared setting, a gateway route)? Don't do it here: it's a change to identity-service's `infra/`. Say so, and propose it to its owner.
