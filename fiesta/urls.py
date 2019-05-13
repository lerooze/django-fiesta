
from django.urls import path, register_converter
from rest_framework.urlpatterns import format_suffix_patterns

from . import converters, views

# "http://django-sdmx.org/wsrest/"
# "http://django-sdmx.org/ws/"

register_converter(converters.ResourceConverter, 'res')
register_converter(converters.AgencyConverter, 'age')

urlpatterns = [
    path('wsreg/SubmitStructure/', views.SubmitStructureRequestView.as_view()),
    path('wsrest/<res:resource>/', views.StructureView.as_view()),
    path('wsrest/<res:resource>/<age:agencyID>/', views.StructureView.as_view()),
    path('wsrest/<res:resource>/<age:agencyID>/<str:resourceID>/', views.StructureView.as_view()),
    path('wsrest/<res:resource>/<age:agencyID>/<str:resourceID>/<str:version>/', views.StructureView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
