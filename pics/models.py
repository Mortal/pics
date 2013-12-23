import wand.image
from django.db import models
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.conf import settings
import re
import datetime
import tempfile

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

def make_thumbnail(source_path, target_path):
    storage = default_storage
    with storage.open(source_path) as source_file, \
            wand.image.Image(file=source_file) as source_image, \
            source_image.clone() as target_image:
        width = settings.THUMBNAIL_WIDTH
        height = settings.THUMBNAIL_HEIGHT
        ratio = min(width / source_image.width, height / source_image.height)
        target_image.resize(
                width=int(ratio * source_image.width),
                height=int(ratio * source_image.height))
        with tempfile.TemporaryFile() as tmp_target:
            target_image.save(file=tmp_target)
            storage.save(target_path, tmp_target)


class Image(models.Model):
    album = models.ForeignKey(Album)
    position = models.IntegerField()
    filename = models.CharField(max_length=40)

    def get_local_path(self):
        return '%s/%s' % (self.album.get_local_directory(), self.filename)

    def get_local_thumbnail_path(self):
        return '%s/thumbs/%s' % (self.album.get_local_directory(), self.filename)

    def get_image_url(self):
        return default_storage.url(self.get_local_path())

    def get_thumbnail_url(self):
        return default_storage.url(self.get_local_thumbnail_path())

    def ensure_thumbnail(self):
        storage = default_storage
        source_path = self.get_local_path()
        target_path = self.get_local_thumbnail_path()
        try:
            source_time = storage.modified_time(source_path)
        except FileNotFoundError:
            return
        try:
            target_time = storage.modified_time(target_path)
            if target_time >= source_time:
                return
        except FileNotFoundError:
            pass
        make_thumbnail(source_path, target_path)

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
