mkdir data
echo -e "SERVER_DATA_DIR=$(pwd)/data\nUPTRAIN_LOCAL_URL=http://localhost:4300\nNEXT_PUBLIC_BACKEND_URL=http://localhost:4300/\nNEXT_PUBLIC_BASE_PATH=/dashboard" > .env
docker compose --env-file .env --profile server up