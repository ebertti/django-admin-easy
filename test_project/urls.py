from django.contrib import admin
from django.urls import re_path

# from debug_toolbar.toolbar import debug_toolbar_urls


urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
] # + debug_toolbar_urls()
