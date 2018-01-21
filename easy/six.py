urlencode = None
reverse = None
flatatt = None

try:
    from django.utils.http import urlencode
except ImportError:
    from django.utils.six.moves.urllib.parse import urlencode

try:
    from django.urls import reverse
except:
    from django.core.urlresolvers import reverse

try:
    from django.forms.utils import flatatt
except:
    from django.forms.util import flatatt
