from __future__ import annotations

from typing import Optional

import django.http
from django.shortcuts import redirect
from django.contrib import messages

HttpRequest: django.http.HttpRequest
HttpResponseRedirect: django.http.HttpResponseRedirect

def action_response(
    request: HttpRequest,
    message: Optional[str] = None,
    level: int = messages.INFO,
    keep_querystring: bool = True,
) -> HttpResponseRedirect:
    """
    Redirects the user to the current page with an optional message.

    Args:
        request: The current request.
        message: The message to display to the user.
        level: The level of the message.
        keep_querystring: Whether to keep the query string in the redirect URL.

    Returns:
        An HttpResponseRedirect object.
    """
    redirect_url = "."
    if keep_querystring and request.GET:
        redirect_url = "./?" + request.GET.urlencode()
    if message:
        messages.add_message(request, level, message, fail_silently=True)
    return redirect(redirect_url)
