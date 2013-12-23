from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pics.models import Image
import sys
from optparse import make_option
import stat
import os

def list_all(base):
    if base[:1] == '/':
        base = base[:-1]

    result = []
    queue = [()]
    while len(queue) > 0:
        components = queue[0]
        queue = queue[1:]

        pathname = os.path.join(base, *components)
        mode = os.stat(pathname).st_mode
        if stat.S_ISDIR(mode):
            for e in sorted(os.listdir(pathname)):
                queue.append(components + (e,))
        elif stat.S_ISREG(mode):
            result.append(os.path.join(*components))

    return result

def merge(x1, x2):
    i1, i2 = 0, 0
    l1, l2 = len(x1), len(x2)
    result = []
    while i1 < l1 or i2 < l2:
        if i1 < l1 and i2 < l2:
            a1, a2 = x1[i1], x2[i2]
            if a1 < a2:
                yield (a1, True, False)
                i1 += 1
            elif a1 == a2:
                yield (a1, True, True)
                i1 += 1
                i2 += 1
            else:
                yield (a2, False, True)
                i2 += 1
        elif i1 < l1:
            yield (x1[i1], True, False)
            i1 += 1
        elif i2 < l2:
            yield (x2[i2], False, True)
            i2 += 1

class Command(BaseCommand):
    help = 'Compare media directory contents to database contents'

    option_list = BaseCommand.option_list + (
            make_option('-m', '--missing',
                action='store_true',
                help='list missing media'),
            make_option('-u', '--unknown',
                action='store_true',
                help='list media not referenced in database'),
            make_option('-a', '--all',
                action='store_true',
                help='list all media'),
            make_option('-d', '--delete',
                action='store_true',
                help='delete unknown media files'),
            )

    def handle(self, *args, **kwargs):
        all = bool(kwargs['all'])
        missing = bool(kwargs['missing']) or all
        unknown = bool(kwargs['unknown']) or all
        delete = bool(kwargs['delete'])
        filesystem_filenames = list_all(settings.MEDIA_ROOT)
        assert list(filesystem_filenames) == list(sorted(filesystem_filenames))
        image_filenames = list(sorted(image.get_local_path() for image in Image.objects.all()))
        for filename, is_img, is_fs in merge(image_filenames, filesystem_filenames):
            if missing and is_img and not is_fs:
                self.stdout.write("Missing: %s" % filename)
            if not is_img and is_fs:
                if unknown:
                    self.stdout.write("Unknown: %s" % filename)
                if delete:
                    os.remove(os.path.join(settings.MEDIA_ROOT, filename))
            if is_img and is_fs and all:
                self.stdout.write("Known: %s" % filename)
