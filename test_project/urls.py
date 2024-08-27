from django.contrib import admin
from easy.six import url
from debug_toolbar.toolbar import debug_toolbar_urls


urlpatterns = [
    url(r'^admin/', admin.site.urls),
] + debug_toolbar_urls()
