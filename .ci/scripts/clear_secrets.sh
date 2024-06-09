#!/bin/bash
ACTUAL_CONF=$(docker secret ls --filter name=remote_config --format '{{.ID}}' | tail -n 1) &&
OLD_CONF=$(docker secret ls --filter name=remote_config --format '{{.ID}}' | grep -v $ACTUAL_CONF) &&
for conf_id in $OLD_CONF; do
  docker secret rm $conf_id
done || true