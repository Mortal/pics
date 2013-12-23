from django.views.generic import ListView, UpdateView, CreateView, FormView, View
from .models import Year, Album, Image
from django.core.urlresolvers import reverse
from django import forms
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
import os
from django.db import transaction
import json
from django.http import HttpResponse, HttpResponseRedirect

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        exclude = ('year',)

class AlbumListView(ListView):
    model = Year

class ImageListView(ListView):
    model = Image

    def get_context_data(self, **kwargs):
        context_data = super(ImageListView, self).get_context_data(**kwargs)
        context_data['year'] = Year.objects.get(slug=self.kwargs['year'])
        context_data['album'] = Album.objects.get(
                year__slug=self.kwargs['year'],
                slug=self.kwargs['album'])
        return context_data

    def get_queryset(self):
        return Image.objects.filter(
                album__slug=self.kwargs['album'],
                album__year__slug=self.kwargs['year'])

class ImageTableView(ImageListView):
    template_name = 'pics/image_table.html'

class SingleAlbumMixin(object):
    def get_year(self):
        return Year.objects.get(slug=self.kwargs['year'])

class YearUpdateView(UpdateView):
    model = Year

    def get_object(self):
        return Year.objects.get(slug=self.kwargs['year'])

    def get_success_url(self):
        return reverse('album_list')

class AlbumUpdateView(UpdateView, SingleAlbumMixin):
    model = Album
    form_class = AlbumForm

    def get_context_data(self, **kwargs):
        context_data = super(AlbumUpdateView, self).get_context_data(**kwargs)
        context_data['year'] = self.get_year()
        return context_data

    def get_object(self):
        return Album.objects.get(
                year__slug=self.kwargs['year'],
                slug=self.kwargs['album'])

class YearCreateView(CreateView):
    model = Year

    def form_valid(self, form):
        form.save()
        return super(YearCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('album_list')

class AlbumCreateView(CreateView, SingleAlbumMixin):
    model = Album
    form_class = AlbumForm

    def get_context_data(self, **kwargs):
        context_data = super(AlbumCreateView, self).get_context_data(**kwargs)
        context_data['year'] = self.get_year()
        return context_data

    def form_valid(self, form):
        album = form.save(commit=False)
        album.year = self.get_year()
        album.save()
        return super(AlbumCreateView, self).form_valid(form)

def AjaxResponse(payload, **kwargs):
    return HttpResponse(json.dumps(payload), **kwargs)

def AjaxBadRequest(error_message):
    return AjaxResponse({'error': error_message}, content_type='application/json', status=400)

def AjaxResponseOK():
    # 204 No Content
    return HttpResponse(status=204)

class ImageUploadView(View):
    def get_album(self):
        return Album.objects.get(
                year__slug=self.kwargs['year'],
                slug=self.kwargs['album'])

    def get_success_url(self):
        album = self.get_album()
        return reverse('album_update', kwargs={
            'year': album.year.slug,
            'album': album.slug})

    def post(self, request, **kwargs):
        self.request = request
        self.kwargs = kwargs

        ajax = bool(request.GET['ajax']) if 'ajax' in request.GET else False

        album = self.get_album()
        directory = album.get_local_directory()

        files = request.FILES.getlist('image')
        position = 0
        for image in album.image_set.all():
            position = max(position, image.position)
        position += 1
        result = []

        for f in files:
            filename = default_storage.get_valid_name(f.name)
            path = '%s/%s' % (directory, filename)
            path = default_storage.save(path, f)
            dir_name, file_name = os.path.split(path)
            assert dir_name == directory
            i = Image(album=album, position=position, filename=file_name)
            position += 1
            i.save()
            result.append({'pk': i.pk, 'filename': i.filename, 'original_filename': f.name})

        if ajax:
            return AjaxResponse(result)
        else:
            return HttpResponseRedirect(self.get_success_url())

class ImageRepositionView(View):
    def post(self, request, **kwargs):
        self.kwargs = kwargs

        album = get_object_or_404(Album, 
                year__slug=self.kwargs['year'],
                slug=self.kwargs['album'])

        try:
            image_pks = list(int(x) for x in request.POST['images'].split(','))
        except (KeyError, ValueError):
            return AjaxBadRequest('Incorrect or missing "images"')

        prev = None
        for pk in sorted(image_pks):
            if pk == prev:
                return AjaxBadRequest('Duplicate pk %s' % pk)
            prev = pk

        images = album.image_set.all().in_bulk(image_pks)
        if frozenset(image_pks) != frozenset(images.keys()):
            return AjaxBadRequest('Some images not found')

        min_position = min(image.position for image in images.values())
        max_position = max(image.position for image in images.values())

        if max_position - min_position + 1 >= len(image_pks):
            positions = tuple(sorted(image.position for image in images.values()))
        else:
            positions = tuple(range(min_position, min_position + len(image_pks)))

        assert len(positions) == len(image_pks)

        with transaction.commit_on_success():
            for pk, position in zip(image_pks, positions):
                Image.objects.filter(pk=pk).update(position=position)

        return AjaxResponseOK()

class ImageSortView(View):
    def post(self, request, **kwargs):
        self.request = request
        self.kwargs = kwargs

        album = get_object_or_404(Album, 
                year__slug=self.kwargs['year'],
                slug=self.kwargs['album'])

        if 'by_name' in request.POST:
            key = lambda image: image.filename
        elif 'by_time' in request.POST:
            def force_naive(dt):
                return dt.replace(tzinfo=None)
            key = lambda image: force_naive(image.exif_datetime or image.mtime)
        else:
            return AjaxBadRequest('You must specify by_name or by_time')

        images = list(album.image_set.all())
        images.sort(key=key)
        pos = 1
        with transaction.commit_on_success():
            for image in images:
                image.position = pos
                image.save()
                pos += 1

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('pics_album', kwargs=self.kwargs)
