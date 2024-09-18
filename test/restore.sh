#!/bin/bash

DUMPFILE=quiz.dump

DB=$(docker ps --filter name=quiz-db -q)
docker cp ./test/$DUMPFILE $DB:/tmp/$DUMPFILE;
docker exec -i $DB bash -c "pg_restore -c -Fc -U postgres -d quiz < /tmp/$DUMPFILE";

echo "Дамп успешно восстановлен в базу данных PostgreSQL."

