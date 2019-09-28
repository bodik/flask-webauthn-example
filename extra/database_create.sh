#!/bin/sh
# postgres helper; create role and database

DBNAME="fwe"
if [ -n "$1" ]; then DBNAME="$1"; fi
ROLE="${USER}"
if [ -n "$2" ]; then ROLE="$2"; fi

psql -c "SELECT datname FROM pg_catalog.pg_database;" | grep "${DBNAME}" >/dev/null
if [ $? -ne 0 ]; then
	psql -c "CREATE DATABASE ${DBNAME}"
fi

psql -c "SELECT usename FROM pg_catalog.pg_user;" | grep "${ROLE}" >/dev/null
if [ $? -ne 0 ]; then
	psql -c "CREATE USER ${ROLE};"
fi
