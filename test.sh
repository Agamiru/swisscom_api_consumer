# Script to run app on Docker

# Ansible could do same, but shell script used because of the need
# to see stdout of the test runner in real time.

echo "Ensure external network exists..."
docker network create app-localhost || echo "All good"

echo "Starting nodes..."
cd swisscom_challenge_servers
docker-compose up --detach
cd ..

echo "Starting redis server..."
cd swisscom_challenge
docker-compose up redis-server --detach

echo "Starting scheduler and worker..."
docker-compose up celery-beat celery-worker --detach

echo "Running test..."
docker-compose up swisscom-challenge
cd ..

echo "Show requests logs"
server_container_name=$(docker ps | grep -o 'swisscom_challenge_servers-flask-app-[0-9]\+')
docker logs $server_container_name

echo "Stopping containers"
redis_container_name=$(docker ps | grep -o 'swisscom_challenge-redis-server-[0-9]\+')
docker stop $redis_container_name
scheduler_container_name=$(docker ps | grep -o 'swisscom_challenge-celery-beat-[0-9]\+')
docker stop $scheduler_container_name
worker_container_name=$(docker ps | grep -o 'swisscom_challenge-celery-worker-[0-9]\+')
docker stop $worker_container_name
docker stop $server_container_name