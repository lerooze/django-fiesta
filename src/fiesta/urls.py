

from django.urls import path, register_converter
from fiesta import converters 
from fiesta.views import views
from rest_framework.urlpatterns import format_suffix_patterns

# "http://django-sdmx.org/wsrest/"
# "http://django-sdmx.org/ws/"

register_converter(converters.ResourceConverter, 'res')
register_converter(converters.AgencyConverter, 'age')

urlpatterns = [
    path('wsreg/SubmitStructure/', views.SubmitStructureRequestView.as_view()),
    path('wsrest/<res:resource>/', views.SDMXRESTfulStructureView.as_view()),
    path('wsrest/<res:resource>/<age:agencyID>/',
         views.SDMXRESTfulStructureView.as_view()),
    path('wsrest/<res:resource>/<age:agencyID>/<str:resourceID>/', 
         views.SDMXRESTfulStructureView.as_view()),
    path('wsrest/<res:resource>/<age:agencyID>/<str:resourceID>/'
         '<str:version>/', 
         views.SDMXRESTfulStructureView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
