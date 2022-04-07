from django.conf.urls import include
from django.contrib import admin

from easy.six import url

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]
