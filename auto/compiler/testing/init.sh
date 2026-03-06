# INITIALISING FOR LOCAL TESTING
# Builds docker container and tests locally
docker build -t dockertest .; 

# Runs docker container as server that can be queried via "query.sh"
# Provides AWS access key and AWS secret access key as environment variables to botocore
docker run -p 9000:8080 -e AWS_SECRET_ACCESS_KEY="[AWS_SECRET_ACCESS_KEY]" -e AWS_ACCESS_KEY_ID="[AWS_ACCESS_KEY_ID]" dockertest:latest