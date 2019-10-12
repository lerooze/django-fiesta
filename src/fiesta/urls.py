

from django.urls import path, register_converter, include
from fiesta import converters 
from fiesta.views import views
from rest_framework.urlpatterns import format_suffix_patterns

# "http://django-sdmx.org/wsrest/"
# "http://django-sdmx.org/ws/"

register_converter(converters.ResourceConverter, 'res')
register_converter(converters.AgencyConverter, 'age')
register_converter(converters.ContextConverter, 'con')

urlpatterns = [
    path('wsreg/SubmitStructure/', views.SubmitStructureRequestView.as_view()),
    path('wsrest/schema/<con:context>/<age:agencyID>/<str:resourceID>', views.SDMXRESTfulSchemaView.as_view()),
    path('wsrest/schema/<con:context>/<age:agencyID>/<str:resourceID>/<str:version>', views.SDMXRESTfulSchemaView.as_view()),
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

urlpatterns += [
    path('api-auth/', include('rest_framework.urls'))
]
