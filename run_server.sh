rm docker-compose.yml
mv docker-compose-server.yml docker-compose.yml

# sudo docker container purne
# sudo docker image purne
sudo docker compose down
sudo docker ps -a
sudo docker compose up --build
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py createsuperuser