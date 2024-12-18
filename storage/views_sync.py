import os

from asgiref.sync import sync_to_async
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404
from django.utils import timezone

from storage.models import Folder, File


@sync_to_async
def save_file(file_instance, new_name):
    file_instance.name = new_name
    file_instance.save()
    return file_instance.name
@sync_to_async
def save_folder(folder_instance, new_name):
    folder_instance.name = new_name
    folder_instance.save()
    return folder_instance.name
@sync_to_async
def get_user_id(request):
    return request.user.id
@sync_to_async
def get_folder(folder_id, user):
    user_id = user.id
    return Folder.objects.filter(id=folder_id, user=user_id).first()
@sync_to_async
def get_folder_or_404_sync(folder_id):
    return get_object_or_404(Folder, id=folder_id)
@sync_to_async
def create_folder_sync(folder_path):
    os.makedirs(folder_path, exist_ok=True)
@sync_to_async
def create_file_sync(file_url, content):
    fs = FileSystemStorage()
    return fs.save(file_url, content)
@sync_to_async
def create_folder_bd(folder_name, user, parent_folder, creation_date=None):
    if creation_date is None:
        creation_date = timezone.now()
    return Folder.objects.create(
        name=folder_name,
        user=user,
        parent=parent_folder,
        creation_date=creation_date,
    )
@sync_to_async
def create_file_bd(file_name, user, parent_folder, creation_date=None):
    if creation_date is None:
        creation_date = timezone.now()
    return File.objects.create(
        name=file_name,
        user=user,
        folder=parent_folder,
        creation_date=creation_date
    )

@sync_to_async
def delete_file_sync(file_instance):
    file_instance.delete()
@sync_to_async
def delete_folder_async(folder_id):
    folder_instance = get_object_or_404(Folder, id=folder_id)
    def delete_recursive(folder):
        folder.files.all().delete()
        subfolders = Folder.objects.filter(parent=folder)
        for subfolder in subfolders:
            delete_recursive(subfolder)
        folder.delete()
    delete_recursive(folder_instance)
@sync_to_async
def get_file_or_404(file_id):
    return get_object_or_404(File, id=file_id)
@sync_to_async
def get_file(file_id):
    return File.objects.get(id=file_id)
@sync_to_async
def change_file_public(file_instance):
    file_instance.is_public = not file_instance.is_public
    file_instance.save()
    if(file_instance.is_public == True):
        folder_instance = get_object_or_404(Folder, id=file_instance.folder_id)
        folder_instance.is_public = True
        folder_instance.save()

@sync_to_async
def set_file_public(file_instance, public = True):
    file_instance.is_public = public
    file_instance.save()
    return file_instance.is_public
@sync_to_async
def change_folder_public(folder_instance):
    folder_instance.is_public = not folder_instance.is_public
    folder_instance.save()
    return folder_instance.is_public
@sync_to_async
def set_folder_public(folder_instance, public = True):
    folder_instance.is_public = public
    folder_instance.save()
    return folder_instance.is_public
@sync_to_async
def get_child_folders(folder_instance):
    return list(Folder.objects.filter(parent=folder_instance))
@sync_to_async
def get_child_files(folder_instance):
    return list(File.objects.filter(folder=folder_instance))
@sync_to_async
def get_parent_folder(folder_instance):
    return folder_instance.parent

