from contextlib import closing
import json
from math import atan2, cos, radians, sin
import sqlite3

from django.conf import settings
from django.contrib.auth import authenticate, logout as auth_logout, login
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views import generic

from app.forms import ExtendedUserForm


def calculate(lat1, lng1, lat2, lng2, R=6373):
    dlon = radians(lng2 - lng1)
    dlat = radians(lat2 - lat1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * (sin(dlon/2)**2)
    c = 2 * atan2(a**0.5, (1-a)**0.5)
    d = 6373 * c
    return d


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(login_url="/app/login/")(view)


def Login(request):
    if request.user.is_authenticated():
        return redirect('app:home')
    else:
        return render(request, "login.html")


def classicLogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        if not request.user.is_authenticated():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('app:home')
            else:
                return redirect('app:login')
        else:
            return redirect('app:login')


def updatelatlng(request):
    if request.method == 'POST':
        if request.user.is_authenticated():
            lat = request.POST['lat']
            lang = request.POST['lng']
            placename = request.POST['placename']
            address = request.POST['address']
            user = request.user
            user.lat = lat
            user.lang = lang
            user.placename = placename
            user.address = address
            user.save()
            return HttpResponse(json.dumps({"status": True}), content_type="application/json")
        else:
            raise PermissionDenied()
    else:
        return HttpResponse(json.dumps({"status": False, "error": "Only POST method is allowed."}),
                            content_type="application/json")


def ClassicSignUP(request):

    if request.method == 'POST':

        if not request.user.is_authenticated():
            with open('/home/ashwini/foo.txt', 'a') as f:
                f.write(str(request.POST))
            form = ExtendedUserForm(request.POST)
            if form.is_valid():
                with open('/home/ashwini/foo.txt', 'a') as f:
                    f.write('Here\n')
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                login(request, authenticate(email=user.email, password=form.cleaned_data['password']))
                return redirect('app:home')
            else:
                with open('/home/ashwini/foo.txt', 'a') as f:
                    f.write(str(form.errors))
                return redirect('app:login')
        else:
            return redirect('app:login')


def Logout(request):
    if request.user.is_authenticated():
        auth_logout(request)
        return redirect('app:login')
    else:
        return redirect('app:login')


class Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'home.html'


def get_users(lat, lang, distance=50):
    with closing(sqlite3.connect(settings.DATABASES['default']['NAME'])) as connection:
        connection.create_function("calculate", 4, calculate)
        with closing(connection.cursor()) as cur:
            query = ("select id, first_name, last_name, lat, lang, placename, address, calculate(lat, lang, %s, %s) "
                     "as distance from app_extendeduser as user "
                     "where distance <= %s order by distance")
            cur.execute(query % (lat, lang, distance))
            fields = [x[0] for x in cur.description]
            print fields
            return [dict(zip(fields, d)) for d in cur.fetchall()]


def explore(request):
    if request.user.is_authenticated():
        if request.user.lat or request.user.lang:
            data = get_users(request.user.lat, request.user.lang)
            return render(request, "explore.html", {'data': json.dumps(data)})
        else:
            return redirect('app:home')


def peopleNearby(request):

    if request.user.is_authenticated():
        distance = request.POST.get('distance', 50)
        lat, lang = request.user.lat, request.user.lang
        data = get_users(lat, lang, distance)
        return HttpResponse(json.dumps({'data': json.dumps(data), 'status': True}), content_type="application/json")
