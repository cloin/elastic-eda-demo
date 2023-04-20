import asyncio
from datetime import datetime
from elasticsearch import AsyncElasticsearch
from dateutil.parser import parse
from typing import Any, Dict
import yaml


async def main(queue: asyncio.Queue, args: Dict[str, Any]):
    elastic_host = args.get("elastic_host", "localhost")
    elastic_port = args.get("elastic_port", 9200)
    elastic_username = args.get("elastic_username", "elastic")
    elastic_password = args.get("elastic_password", "elastic!")
    elastic_index_pattern = args.get("elastic_index_pattern", "filebeat-*")
    interval = args.get("interval", 5)
    query = args.get("query", "term:\n  container.name.keyword: nginx")

    elastic_query = yaml.safe_load(query)

    async with AsyncElasticsearch(f"http://{elastic_host}:{elastic_port}", basic_auth=(elastic_username, elastic_password)) as es:
        # Set the initial search_after value to the current timestamp
        search_after = datetime.utcnow()

        while True:
            sort = [
                {
                    "@timestamp": {
                        "order": "asc"
                    }
                }
            ]

            # Run the query
            response = await es.search(
                index=elastic_index_pattern,
                query=elastic_query,
                sort=sort,
                search_after=[search_after.isoformat()],
                size=1000
            )

            # Process the results
            for hit in response['hits']['hits']:
                log_entry = hit["_source"]
                await queue.put(log_entry)

                # Update the search_after value to the current log entry's timestamp
                search_after = parse(log_entry["@timestamp"])

            # Wait before running the query again
            await asyncio.sleep(interval)


if __name__ == "__main__":

    class MockQueue:
        async def put(self, event):
            print(event)

    mock_arguments = dict()
    asyncio.run(main(MockQueue(), mock_arguments))
