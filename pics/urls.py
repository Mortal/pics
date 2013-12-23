from django.conf.urls import patterns, include, url

from .views import (
        ImageListView, ImageTableView, AlbumListView,
        YearCreateView, YearUpdateView,
        AlbumCreateView, AlbumUpdateView,
        ImageUploadView, ImageRepositionView,
        )


urlpatterns = patterns('',
    url(r'^$', AlbumListView.as_view(), name='album_list'),
    url(r'^new/$', YearCreateView.as_view(), name='year_create'),
    url(r'^(?P<year>\w+)/edit/$', YearUpdateView.as_view(), name='year_update'),
    url(r'^(?P<year>\w+)/new/$', AlbumCreateView.as_view(), name='album_create'),
    url(r'^(?P<year>\w+)/(?P<album>\w+)/edit/$', AlbumUpdateView.as_view(), name='album_update'),
    url(r'^(?P<year>\w+)/(?P<album>\w+)/upload/$', ImageUploadView.as_view(), name='image_upload'),
    url(r'^(?P<year>\w+)/(?P<album>\w+)/$', ImageListView.as_view(), name='pics_album'),
    url(r'^(?P<year>\w+)/(?P<album>\w+)/table/$', ImageTableView.as_view(), name='image_table'),
    url(r'^(?P<year>\w+)/(?P<album>\w+)/reorder/$', ImageRepositionView.as_view(), name='image_reposition'),
)
