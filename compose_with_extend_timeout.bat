@echo off
set DOCKER_CLIENT_TIMEOUT=600
set COMPOSE_HTTP_TIMEOUT=600
docker-compose up -d
pause
