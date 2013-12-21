from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from .views import (
        ImageListView, AlbumListView,
        YearCreateView, YearUpdateView,
        AlbumCreateView, AlbumUpdateView,
        ImageUploadView,
        )


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pics.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', AlbumListView.as_view(), name='album_list'),
    url(r'^new/$', YearCreateView.as_view(), name='year_create'),
    url(r'^(?P<year>\w+)/edit/$', YearUpdateView.as_view(), name='year_update'),
    url(r'^(?P<year>\w+)/new/$', AlbumCreateView.as_view(), name='album_create'),
    url(r'^(?P<year>\w+)/(?P<album>\w+)/edit/$', AlbumUpdateView.as_view(), name='album_update'),
    url(r'^(?P<year>\w+)/(?P<album>\w+)/upload/$', ImageUploadView.as_view(), name='image_upload'),
    url(r'^(?P<year>\w+)/(?P<album>\w+)/$', ImageListView.as_view(), name='pics_album'),
)
