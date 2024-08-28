from __future__ import annotations

import django.http
from django.contrib import messages
from django.http import HttpRequest
from django.http.response import HttpResponseRedirect
from django.urls import re_path, reverse

HttpRequest: django.http.HttpRequest


class MixinEasyViews(object):

    def _get_info(self):
        return self.model._meta.app_label, self.model._meta.model_name

    def get_urls(self):
        urls = super(MixinEasyViews, self).get_urls()

        easy_urls = [
            re_path(r'^(?P<pk>.+)/easy/(?P<action>.+)/$', self.admin_site.admin_view(self.easy_object_view),
                name='%s_%s_easy' % self._get_info()),

            re_path(r'^easy/(?P<action>.+)/$', self.admin_site.admin_view(self.easy_list_view),
                name='%s_%s_easy' % self._get_info()),
        ]

        return easy_urls + urls

    def easy_object_view(self, request: "HttpRequest", pk: int, action: str) -> "HttpResponseRedirect":
        """
        Executes the easy object view based on the action.

        Args:
            request (HttpRequest): The current request.
            pk (int): The primary key of the object.
            action (str): The action to perform.

        Returns:
            HttpResponseRedirect: The redirect response.
        """
        method_name = 'easy_view_%s' % action

        view = getattr(self, method_name, None)
        if view:
            return view(request, pk)

        self.message_user(request, 'Easy view %s not found' % method_name, messages.ERROR)

        redirect = reverse('admin:%s_%s_change' % self._get_info(), args=(pk,))

        return HttpResponseRedirect(redirect)

    def easy_list_view(self, request: "HttpRequest", action: str) -> "HttpResponseRedirect":
        """
        Executes the easy list view based on the action.

        Args:
            request (HttpRequest): The current request.
            action (str): The action to perform.

        Returns:
            HttpResponseRedirect: The redirect response.
        """
        method_name = 'easy_view_%s' % action

        view = getattr(self, method_name, None)
        if view:
            return view(request)

        self.message_user(request, 'Easy view %s not found' % method_name, messages.ERROR)

        redirect = reverse('admin:%s_%s_changelist' % self._get_info())

        return HttpResponseRedirect(redirect)
