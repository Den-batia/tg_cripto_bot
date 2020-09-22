from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

from api.admin import admin_site

urlpatterns = [
    path('admin01/', admin_site.urls),
    path('api/', include('api.urls'))
]

urlpatterns += staticfiles_urlpatterns()
