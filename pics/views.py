from django.views.generic import ListView, UpdateView, CreateView, FormView
from .models import Year, Album, Image
from django.core.urlresolvers import reverse
from django import forms

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
        context_data['album'] = Album.objects.get(slug=self.kwargs['album'])
        return context_data

    def get_queryset(self):
        return Image.objects.filter(
                album__slug=self.kwargs['album'],
                album__year__slug=self.kwargs['year'])

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

class ImageUploadForm(forms.Form):
    image = forms.FileField()

class ImageUploadView(FormView):
    form_class = ImageUploadForm

    def form_valid(self, form):
        image =
