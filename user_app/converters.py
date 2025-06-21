import graphene
from graphene_django.converter import convert_django_field
from django_ckeditor_5.fields import CKEditor5Field


@convert_django_field.register(CKEditor5Field)
def convert_ckeditor5_field_to_string(field, registry):  # 👈 two arguments REQUIRED
    return graphene.String(description=field.help_text, required=not field.null)
