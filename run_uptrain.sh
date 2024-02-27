mkdir data
echo "SERVER_DATA_DIR=$(pwd)/data" > .env
docker compose --env-file .env --profile server up