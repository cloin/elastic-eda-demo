import asyncio
from datetime import datetime
from elasticsearch import AsyncElasticsearch
from dateutil.parser import parse

# Replace with your Elasticsearch credentials
your_username = 'elastic'
your_password = 'YOURPASSWORD!'

es = AsyncElasticsearch("http://localhost:9200", http_auth=(your_username, your_password))

async def run_query(query, index_pattern):
    # Set the initial search_after value to the current timestamp
    search_after = datetime.utcnow()

    while True:
        body = {
            "query": query,
            "sort": [
                {
                    "@timestamp": {
                        "order": "asc"
                    }
                }
            ],
            "search_after": [search_after.isoformat()],
            "size": 1000
        }

        # Run the query
        response = await es.search(index=index_pattern, body=body)

        # Process the results
        for hit in response['hits']['hits']:
            log_entry = hit["_source"]
            print(log_entry)

            # Update the search_after value to the current log entry's timestamp
            search_after = parse(log_entry["@timestamp"])

        # Wait before running the query again
        await asyncio.sleep(5)

# Default query collects log lines from the nginx container in this stack using filebeat-* index
your_query = {
    "term": {
        "container.name.keyword": "nginx"
    }
}

your_index_pattern = "filebeat-*"

asyncio.run(run_query(your_query, your_index_pattern))

