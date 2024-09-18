#!/bin/bash
DUMPFILE=quiz.dump;
DB=$(docker ps --filter name=quiz-db -q)
docker exec -i $DB bash -c "pg_dump -U postgres -W -Fc -x quiz -f /tmp/dumpfile.dump";
docker cp $DB:/tmp/dumpfile.dump ./test/$DUMPFILE