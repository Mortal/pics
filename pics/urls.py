from django.conf.urls import patterns, include, url

from .views import (
        ImageListView, ImageTableView, AlbumListView,
        YearCreateView, YearUpdateView,
        AlbumCreateView, AlbumUpdateView,
        ImageUploadView, ImageRepositionView,
        ImageSortView,
        )


urlpatterns = patterns('',
    url(r'^$', AlbumListView.as_view(), name='album_list'),
    url(r'^new/$', YearCreateView.as_view(), name='year_create'),
    url(r'^(?P<year>[\w_-]+)/edit/$', YearUpdateView.as_view(), name='year_update'),
    url(r'^(?P<year>[\w_-]+)/new/$', AlbumCreateView.as_view(), name='album_create'),
    url(r'^(?P<year>[\w_-]+)/(?P<album>[\w_-]+)/edit/$', AlbumUpdateView.as_view(), name='album_update'),
    url(r'^(?P<year>[\w_-]+)/(?P<album>[\w_-]+)/upload/$', ImageUploadView.as_view(), name='image_upload'),
    url(r'^(?P<year>[\w_-]+)/(?P<album>[\w_-]+)/$', ImageListView.as_view(), name='pics_album'),
    url(r'^(?P<year>[\w_-]+)/(?P<album>[\w_-]+)/table/$', ImageTableView.as_view(), name='image_table'),
    url(r'^(?P<year>[\w_-]+)/(?P<album>[\w_-]+)/reorder/$', ImageRepositionView.as_view(), name='image_reposition'),
    url(r'^(?P<year>[\w_-]+)/(?P<album>[\w_-]+)/sort/$', ImageSortView.as_view(), name='image_sort'),
)
