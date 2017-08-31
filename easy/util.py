from django.shortcuts import redirect
from django.contrib import messages


def action_response(request, message=None, level=messages.INFO, keep_querystring=True):
    redirect_url = '.'
    if keep_querystring and request.GET:
        redirect_url = './?' + request.GET.urlencode()
    if message:
        messages.add_message(request, level, message, fail_silently=True)
    return redirect(redirect_url)
