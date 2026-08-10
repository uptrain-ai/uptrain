mkdir data
echo -e "SERVER_DATA_DIR=$(pwd)/data\nUPTRAIN_LOCAL_URL=http://localhost:4300\nUPTRAIN_API_KEY=default_key\nUPTRAIN_ALLOWED_ORIGINS=http://localhost:4300,http://localhost:3000\nNEXT_PUBLIC_BACKEND_URL=http://localhost:4300/\nNEXT_PUBLIC_BASE_PATH=/dashboard\nNEXT_PUBLIC_UPTRAIN_API_KEY=default_key" > .env
docker compose --env-file .env --profile server up