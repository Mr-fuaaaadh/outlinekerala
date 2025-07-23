from django.views.decorators.csrf import csrf_exempt
from graphene_file_upload.django import FileUploadGraphQLView
from django.urls import path

# URL configuration for the user_app GraphQL API
urlpatterns = [
    path("graphql/", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),

]
