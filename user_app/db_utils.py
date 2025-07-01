from graphql import GraphQLError


def get_object_or_error(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        model_name = model.__name__
        raise GraphQLError(f"{model_name} not found.")
