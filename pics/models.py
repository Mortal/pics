import wand.image
from django.db import models
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
import re
import datetime

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

    @property
    def exif_datetime(self):
        try:
            with default_storage.open(self.get_local_path()) as f:
                with wand.image.Image(file=f) as img:
                    timestring = img.metadata['exif:DateTimeOriginal']
                    o = re.match(r'(....):(..):(..) (..):(..):(..)', timestring)
                    if not o:
                        return None
                    else:
                        return datetime.datetime(*[int(o.group(1+i))
                            for i in range(6)])
        except FileNotFoundError:
            return None

    @property
    def mtime(self):
        try:
            return default_storage.modified_time(self.get_local_path())
        except FileNotFoundError:
            return None

    class Meta:
        ordering = ('position',)
        unique_together = (('album', 'filename'),)
