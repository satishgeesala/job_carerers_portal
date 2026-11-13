
import os
import cloudinary
from cloudinary_storage.storage import RawMediaCloudinaryStorage


class PrivateResumeStorage(RawMediaCloudinaryStorage):

    def _upload(self, name, content):
        options = {
            'use_filename': True,
            'resource_type': 'raw',
            'type': 'authenticated',
            'tags': self.TAG,
        }

        folder = os.path.dirname(name)

        if folder:
            options['folder'] = folder

        return cloudinary.uploader.upload(content, **options)
