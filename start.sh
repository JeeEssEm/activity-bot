#!/bin/bash
source config/.env

export DB_USER=$DB_USER
export DB_HOST=$DB_HOST
export DB_PASSWORD=$DB_PASSWORD
export DB_PORT=$DB_PORT
export DB_NAME=$DB_NAME
export REDIS_PASSWORD=$REDIS_PASSWORD

docker-compose up -d --build
