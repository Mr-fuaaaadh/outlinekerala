from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from django.urls import path

# URL configuration for the user_app GraphQL API
urlpatterns = [
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))),
]
