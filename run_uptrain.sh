mkdir data
API_KEY=$(openssl rand -hex 32)
echo -e "SERVER_DATA_DIR=$(pwd)/data\nUPTRAIN_LOCAL_URL=http://localhost:4300\nUPTRAIN_API_KEY=$API_KEY\nUPTRAIN_ALLOWED_ORIGINS=http://localhost:4300,http://localhost:3000\nNEXT_PUBLIC_BACKEND_URL=http://localhost:4300/\nNEXT_PUBLIC_BASE_PATH=/dashboard\nNEXT_PUBLIC_UPTRAIN_API_KEY=$API_KEY" > .env
docker compose --env-file .env --profile server up