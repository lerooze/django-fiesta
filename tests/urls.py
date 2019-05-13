
from django.urls import re_path, include

urlpatterns = [
    re_path(r'^api-auth/', include('rest_framework.urls')),
    re_path('^fiesta/', include('fiesta.urls')),
]
