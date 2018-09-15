from django.conf.urls import url
from django.contrib import messages
from django.http.response import HttpResponseRedirect

from easy.helper import get_model_name
from easy.six import reverse


class MixinEasyViews(object):

    def _get_info(self):
        return self.model._meta.app_label, get_model_name(self.model)

    def get_urls(self):
        urls = super(MixinEasyViews, self).get_urls()

        easy_urls = [
            url(r'^(?P<pk>.+)/easy/(?P<action>.+)/$', self.admin_site.admin_view(self.easy_object_view),
                name='%s_%s_easy' % self._get_info()),

            url(r'^easy/(?P<action>.+)/$', self.admin_site.admin_view(self.easy_list_view),
                name='%s_%s_easy' % self._get_info()),
        ]

        return easy_urls + urls

    def easy_object_view(self, request, pk, action):

        method_name = 'easy_view_%s' % action

        view = getattr(self, method_name, None)
        if view:
            return view(request, pk)

        self.message_user(request, 'Easy view %s not found' % method_name, messages.ERROR)

        redirect = reverse('admin:%s_%s_change' % self._get_info(), args=(pk,))

        return HttpResponseRedirect(redirect)

    def easy_list_view(self, request, action):
        method_name = 'easy_view_%s' % action

        view = getattr(self, method_name, None)
        if view:
            return view(request)

        self.message_user(request, 'Easy view %s not founded' % method_name, messages.ERROR)

        redirect = reverse('admin:%s_%s_changelist' % self._get_info(),)

        return HttpResponseRedirect(redirect)
