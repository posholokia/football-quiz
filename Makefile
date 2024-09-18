DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env
APP_FILE = ./.ci/docker/app.dev.yml
APP_CONTAINER = fastapi-quiz
CELERY_WORKER_CONTAINER = celery-worker
CELERY_BEAT_CONTAINER = celery-beat
STOR_FILE = ./.ci/docker/storage.dev.yml
STOR_FILE_TEST = ./.ci/docker/storage.test.yml
DB_CONTAINER = quiz-db
ALEMBIC_MIGRATIONS = alembic revision --autogenerate
APP_RUN = docker run --rm


.PHONY: run
run:
	${DC} -f ${STOR_FILE} up -d
	${DC} -f ${APP_FILE} up --build -d

.PHONY: app
app:
	${DC} -f ${APP_FILE} up --build -d

.PHONY: debug
debug:
	cd ./src/ && uvicorn main:create_app --reload

.PHONY: stor
stor:
	${DC} -f ${STOR_FILE} up -d

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: db-logs
db-logs:
	${LOGS} ${DB_CONTAINER} -f

.PHONY: down
down:
	${DC} -f ${APP_FILE} down
	${DC} -f ${STOR_FILE} down

.PHONY: app-down
app-down:
	${DC} -f ${APP_FILE} down

.PHONY: migrate
migrate:
	${EXEC} ${APP_CONTAINER} alembic upgrade head

.PHONY: migrations
migrations:
	${EXEC} ${APP_CONTAINER} alembic revision --autogenerate -m "${COMMIT}"

.PHONY: app-bash
app-bash:
	${EXEC} ${APP_CONTAINER} bash

.PHONY: worker-logs
worker-logs:
	${LOGS} ${CELERY_WORKER_CONTAINER} -f

.PHONY: beat-logs
beat-logs:
	${LOGS} ${CELERY_BEAT_CONTAINER} -f

.PHONY: test-mobile
test-mobile:
	${DC} -f ${APP_FILE} down
	${DC} -f ${STOR_FILE} down
	${DC} -f ${STOR_FILE_TEST} down
	${DC} -f ${STOR_FILE_TEST} up -d
	sleep 2
	chmod +x ./test/restore.sh
	./test/restore.sh
	pytest test/test_api/test_mobile.py --capture=tee-sys


.PHONY: test-admin
test-admin:
	${DC} -f ${APP_FILE} down
	${DC} -f ${STOR_FILE} down
	${DC} -f ${STOR_FILE_TEST} down
	${DC} -f ${STOR_FILE_TEST} up -d
	sleep 2
	chmod +x ./test/restore.sh
	./test/restore.sh
	pytest test/test_api/test_admin.py --capture=tee-sys


.PHONY: test
test:
	${DC} -f ${APP_FILE} down
	${DC} -f ${STOR_FILE} down
	${DC} -f ${STOR_FILE_TEST} down
	${DC} -f ${STOR_FILE_TEST} up -d
	sleep 2
	chmod +x ./test/restore.sh
	./test/restore.sh
	pytest --capture=tee-sys