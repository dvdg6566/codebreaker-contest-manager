docker kill $(docker ps -a -q)
docker rm -f $(docker ps -a -q)
docker rmi -f $(docker images -a -q)