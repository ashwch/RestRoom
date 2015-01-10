from django.conf.urls import patterns, url

from app.views import classicLogin, ClassicSignUP, explore, Home, Login, Logout, peopleNearby, updatelatlng


urlpatterns = patterns('',
                       url(r'^$', Home.as_view(), name='home'), 
                       url(r'^login/$', Login, name='login'),
                       url(r'^classiclogin/$', classicLogin, name='classiclogin'),
                       url(r'^logout/$', Logout, name='logout'),
                       url(r'^home/$', Home.as_view(), name='home'),
                       url(r'^signup', ClassicSignUP, name='signup'),
                       url(r'^updatelatlng/$', updatelatlng, name='updatelatlng'),
                       url(r'^explore/$', explore, name='explore'),
                       url(r'^peoplenearby/$', peopleNearby, name='peoplenearby'),
                       )
