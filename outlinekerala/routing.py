from django.urls import re_path
from channels_graphql_ws import GraphqlWsConsumer

class MyGraphqlWsConsumer(GraphqlWsConsumer):
    async def on_connect(self, payload):
        # You can check auth here
        pass

websocket_urlpatterns = [
    re_path(r"graphql/", MyGraphqlWsConsumer.as_asgi()),
]
