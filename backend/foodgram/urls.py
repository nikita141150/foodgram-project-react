from django.contrib import admin
from django.urls import include, path

import api.urls
import users.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(users.urls)),
    path('api/', include(api.urls))
]
