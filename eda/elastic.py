import asyncio
from datetime import datetime
from prometheus_api_client import PrometheusConnect
from dateutil.parser import parse
from typing import Any, Dict
import yaml

async def main(queue: asyncio.Queue, args: Dict[str, Any]):
    prometheus_host = args.get("prometheus_host", "localhost")
    prometheus_port = args.get("prometheus_port", 9090)
    interval = args.get("interval", 5)
    query = args.get("query", "up")

    prometheus_query = query  # Modify as needed

    pc = PrometheusConnect(url=f"http://{prometheus_host}:{prometheus_port}")

    # Set the initial timestamp value
    timestamp = datetime.utcnow()

    while True:
        query_result = pc.custom_query_range(query=prometheus_query, start=timestamp.isoformat(), end=datetime.utcnow().isoformat(), step=60)

        for result in query_result:
            # Process the results
            metric_entry = result["values"]
            await queue.put(metric_entry)

            # Update the timestamp value to the current metric entry's timestamp
            timestamp = datetime.utcfromtimestamp(result["timestamp"])

        # Wait before running the query again
        await asyncio.sleep(interval)

if __name__ == "__main__":
    class MockQueue:
        async def put(self, event):
            print(event)

    mock_arguments = dict()
    asyncio.run(main(MockQueue(), mock_arguments))
