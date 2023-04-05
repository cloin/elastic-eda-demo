import asyncio
from elasticsearch import AsyncElasticsearch
from datetime import datetime

async def query_log_stream():
    # Connect to your Elasticsearch instance
    es = AsyncElasticsearch(["http://localhost:9200"], http_auth=("elastic", "MY_PASSWORD"))

    # Define the initial timestamp
    start_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"

    while True:
        # Define your query
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "container.name.keyword": "nginx"
                            }
                        },
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": start_time
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "@timestamp": {
                        "order": "asc"
                    }
                }
            ]
        }

        # Execute the search query
        response = await es.search(index="filebeat-*", body=query)
        hits = response['hits']['hits']
        for hit in hits:
            message = hit['_source']['message']
            container_name = hit['_source']['container']['name']
            print(f"Container: {container_name}, Message: {message}")

            # Update the start_time to the timestamp of the latest hit
            start_time = hit['_source']['@timestamp']

        # Wait for 5 seconds before running the query again
        await asyncio.sleep(5)

    # Close the Elasticsearch connection
    await es.transport.close()

# Run the async function
asyncio.run(query_log_stream())
