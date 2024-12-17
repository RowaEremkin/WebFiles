import os
import uuid
from django.db import models
from django.contrib.auth.models import User

class Folder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)
    creation_date = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'parent'], name='unique_folder_name_per_parent')
        ]

    def save(self, *args, **kwargs):
        original_name = self.name
        counter = 1

        while Folder.objects.filter(name=self.name, parent=self.parent).exclude(id=self.id).exists():
            self.name = f"{original_name} ({counter})"
            counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, related_name='files', on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)
    creation_date = models.DateTimeField(null=True, blank=True)
    uploaded_at = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'folder'], name='unique_file_name_per_folder')
        ]

    def save(self, *args, **kwargs):
        original_name, extension = os.path.splitext(self.name)
        counter = 1

        while File.objects.filter(name=self.name, folder=self.folder).exclude(id=self.id).exists():
            self.name = f"{original_name} ({counter}){extension}"
            counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
