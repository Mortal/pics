from django.db import models
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage

class Year(models.Model):
    number = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return self.name

    def get_local_directory(self):
        return 'images/%s-%s' % (self.number, self.slug)

    class Meta:
        ordering = ('number',)

class Album(models.Model):
    year = models.ForeignKey(Year)
    number = models.CharField(max_length=40)
    slug = models.CharField(max_length=40)
    name = models.CharField(max_length=40)

    def get_absolute_url(self):
        return reverse('pics_album',
                kwargs={'year': self.year.slug,
                    'album': self.slug})

    def get_local_directory(self):
        return '%s/%s-%s' % (
                self.year.get_local_directory(),
                self.number,
                self.slug)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('year', 'number',)
        unique_together = (('year', 'number'), ('year', 'slug'),)

class Image(models.Model):
    album = models.ForeignKey(Album)
    position = models.IntegerField()
    filename = models.CharField(max_length=40)

    def get_local_path(self):
        return '%s/%s' % (self.album.get_local_directory(), self.filename)

    def get_image_url(self):
        return default_storage.url(self.get_local_path())

    class Meta:
        ordering = ('position',)
