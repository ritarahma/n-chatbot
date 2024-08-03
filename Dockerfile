# Set the base image
FROM rahmaci/oculusdei-be:latest

ENV PYTHONUNBUFFERED=1

# Dockerfile author / maintainer 
MAINTAINER Rita Rahmawati <ritarahma1706@gmail.com> 


#ENV CASSANDRA_HOSTS=elassandra_node1
#ENV ELASTIC_HOSTS=elastic
ENV CQLENG_ALLOW_SCHEMA_MANAGEMENT="True"

# SET WORKDIR
WORKDIR /usr/local/bank-data-be

# COPY PROJECT FILES
COPY . .

# JUST COPY requirements.txt

ENV TZ=Asia/Jakarta

# COPY CONFIGURATION FILE
# COPY deploy /

EXPOSE 5001

# TEMP FOR TEST PURPOSE
CMD [ "python3", "/usr/local/bank-data-be/run.py" ]
