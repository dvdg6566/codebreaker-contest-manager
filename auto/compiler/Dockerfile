FROM public.ecr.aws/lts/ubuntu:24.04_stable
ENV PYTHONIOENCODING="utf8"
# See: https://docs.aws.amazon.com/lambda/latest/dg/images-create.html

# Fixes tzdata hanging problem
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -y g++ \
    cmake \
    libtool \
    autoconf \
    python3 \
    python3-pip \
    curl

# Install the runtime interface client
RUN pip3 install awslambdaric --break-system-packages

COPY ./entry_script.sh /entry_script.sh
ENTRYPOINT [ "/entry_script.sh" ]

# Install AWS CLI
RUN pip3 install awscli boto3 --break-system-packages

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}
COPY awstools.py ${LAMBDA_TASK_ROOT}
COPY compilesub.py ${LAMBDA_TASK_ROOT}
COPY compilechecker.py ${LAMBDA_TASK_ROOT}
COPY testlib.h ${LAMBDA_TASK_ROOT}

CMD [ "app.lambda_handler" ]
