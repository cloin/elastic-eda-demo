# Elasticsearch, Logstash, Kibana (Elastic Stack) with Filebeat using Docker Compose

This repository contains a Docker Compose configuration file that sets up the stack and Filebeat. The stack is composed of Elasticsearch, Logstash, and Kibana, and Filebeat is used for log collection and forwarding.

Filebeat is configured to ship the docker logs for this stack to Elasticsearch.

ansible-rulebook is also running in this stack and is configured to pull a rulebook and custom source plugin from galaxy. This source plugin is able to accept elastic queries and run them at an interval to retrieve log entries. In the default setup, this rulebook is watching for new log entries from the nginx container and dumping the events. View logs of this occurring by running `docker compose logs -f ansible-rulebook`

This configuration is not suitable for a production environment.

## Prerequisites

- Docker and Docker Compose installed on your system.

## Services

- **Elasticsearch**: A distributed, RESTful search and analytics engine.
- **Logstash**: A data processing pipeline that ingests data from various sources, transforms it, and forwards it to Elasticsearch.
- **Kibana**: A data visualization and exploration tool for Elasticsearch.
- **Filebeat**: A lightweight log shipper that forwards logs to Logstash or Elasticsearch.

## Usage

1. Clone this repository:
```
git clone https://github.com/cloin/elastic-eda.git
cd elastic-eda
```

2. Set the `ELASTIC_PASSWORD` environment variable:

```
export ELASTIC_PASSWORD=your_password
```

3. Start the services using Docker Compose:

```
docker compose up -d
```

4. Access Kibana at http://localhost:5601 using the username `elastic` and the password you set in step 2.

5. Go to the "Index Patterns" section in Kibana (under "Stack Management") and create a new index pattern with the pattern filebeat-*. Select @timestamp as the time filter field name.

6. Navigate to the "Discover" section in Kibana, and you should see the docker logs from this stack. You can create visualizations and dashboards based on this data as needed.

## Configuration

- Elasticsearch configuration is set through environment variables in the `docker-compose.yml` file.
- Logstash configuration is mounted from `./logstash/config/logstash.yml`, and Logstash pipelines are mounted from `./logstash/pipeline`.
- Kibana configuration is set through environment variables in the `docker-compose.yml` file.
- Filebeat configuration is mounted from `./filebeat/filebeat.yml`.

## Volumes and Networks

- Elasticsearch data is stored in a named volume `esdata`.
- All services are connected to a custom bridge network called `elk`.

## Ports

- Elasticsearch: 9200
- Logstash: 5044
- Kibana: 5601

## Customization

You can customize the configuration files and pipeline settings as needed. Be sure to restart the affected services after making any changes.

## Cleanup

To stop the services and remove containers, networks, and volumes:

```
docker-compose down -v
```