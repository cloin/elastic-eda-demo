import asyncio
from elasticsearch_async import AsyncElasticsearch

# create an async Elasticsearch client instance
es = AsyncElasticsearch(['localhost:9200'])

async def search_logs():
    # define the Elasticsearch query
    query = {
        "query": {
            "match": {
                "log": "error"
            }
        }
    }

    # search for documents matching the query
    result = await es.search(index='my_index', body=query)

    # print the results
    for hit in result['hits']['hits']:
        print(hit['_source'])

# run the search_logs function in an asyncio event loop
asyncio.run(search_logs())
