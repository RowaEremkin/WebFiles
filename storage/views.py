import os
import shutil
import traceback

from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.core.files.base import ContentFile
from django.utils import translation
from . import consumers, views_sync
from .consumers import get_path
from .models import Folder, File
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomLoginForm
from .translations import get_translations
from .views_sync import get_user_id, get_folder, create_folder_sync, create_file_sync, create_folder_bd, create_file_bd, \
    delete_file_sync, delete_folder_async, get_file_or_404, get_folder_or_404_sync, change_file_public, \
    save_file, save_folder, get_child_folders, get_child_files, set_file_public, \
    set_folder_public, get_parent_folder, get_file


def index(request, folder_path=""):
    user = request.user
    user_language = request.session.get('language', 'en')
    context = {
        'folder_path': folder_path,
        't': get_translations(user_language),
        'lang': user_language
    }

    return render(request, 'storage/index.html', context)
@csrf_exempt
def set_language(request, lang):
    user_language = lang
    translation.activate(user_language)
    request.session['language'] = user_language
    return JsonResponse({'success': True},status=200)
async def get_file_path(file_instance):
    if file_instance == None:
        return None
    return await get_path(file_instance.folder_id) + "\\" + file_instance.name
@login_required
async def upload_file(request):
    if request.method == 'POST':
        folder_id = request.POST.get('folder_id')
        file_name = request.POST.get('file_name')
        file_blob = request.FILES.get('file_blob')
        creation_date = request.POST.get('creation_date')

        try:
            folder = await get_folder(folder_id, request.user)
            folder_url = await get_path(folder_id)
            new_file = await create_file_bd(file_name, request.user, folder, creation_date)
            file_name = new_file.name
            file_url = os.path.join(folder_url, file_name)
            await create_file_sync(file_url, file_blob)

            user_id = await get_user_id(request)
            await consumers.update_all_session_in_folder(folder_id, user_id)

            return JsonResponse({
                "action": "upload_success",
                "message": "File uploaded successfully!",
                "parentFolderId": folder_id,
                "file_url": file_url
            })
        except Exception as e:
            traceback.print_exc()
            print(f"Error saving file for user_id {request.user}: {e}")
            return JsonResponse({
                "action": "upload_error",
                "message": str(e),
                "parent_folder_id": folder_id
            }, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)
async def download_file(request, file_id):
    try:
        user_id = await get_user_id(request)
        #print(f"User: ", user_id, " try to download file: ", file_id)
        @sync_to_async
        def get_file(file_id):
            return File.objects.get(id=file_id)
        file = await get_file(file_id)
        if file is None:
            print(f"User: ", request.user.id, " failed download file: ", file_id, " because file not found in DB")
            raise Http404("File not found")
        if file.user_id != user_id and not file.is_public:
            print(f"User: ", user_id, " failed download file: ", file_id, " because not access")
            raise Http404("File not found")

        file_path = await get_path(file.folder_id)
        file_path = file_path + "\\" + file.name
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{file.name}"'
        #print(f"User: ", user_id, " successful download file: ", file_id)
        return response

    except File.DoesNotExist:
        raise Http404("File not found")
async def open_file(request, file_id):
    try:
        user_id = await get_user_id(request)
        #print(f"User: ", user_id, " try to open file: ", file_id)
        file = await get_file(file_id)
        if file is None:
            print(f"User: ", request.user.id, " failed open file: ", file_id, " because file not found in DB")
            raise Http404("File not found")
        if file.user_id != user_id and not file.is_public:
            print(f"User: ", user_id, " failed open file: ", file_id, " because not access")
            raise Http404("File not found")

        file_path = await get_path(file.folder_id)
        file_path = file_path + "\\" + file.name
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{file.name}"'
        #print(f"User: ", user_id, " successful open file: ", file_id)
        return response

    except File.DoesNotExist:
        raise Http404("File not found")
def register_view(request):
    user_language = request.session.get('language', 'en')
    t = get_translations(user_language)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')
        else:
            messages.error(request, 'There was an error with your registration.')
    else:
        form = CustomUserCreationForm(t=t)

    context = {
        'form': form,
        't': t,
        'lang': user_language
    }
    return render(request, 'registration/register.html', context)

def login_view(request):
    user_language = request.session.get('language', 'en')
    t = get_translations(user_language)
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have logged in successfully!')
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'There was an error with your login.')
    else:
        form = CustomLoginForm(t=t)

    context = {
        'form': form,
        't': t,
        'lang': user_language
    }
    return render(request, 'registration/login.html', context)
def logout_view(request):
    user_language = request.session.get('language', 'en')
    t = get_translations(user_language)
    context = {
        't': t,
        'lang': user_language
    }
    logout(request)
    return render(request, 'registration/logout.html', context)

@login_required
async def create_folder(request):
    if request.method == "POST":
        #t = get_translations(request.user.language)
        try:
            folder_name = request.POST.get("name")
            parent_id = request.GET.get("parent_id")
            #print("Try to create folder: ", folder_name, " in folder_id: ", parent_id)
            if not folder_name:
                return JsonResponse({"error": "Folder name is required."}, status=400)
            parent_folder = None
            if parent_id:
                parent_folder = await get_folder(parent_id, request.user)
                if not parent_folder:
                    return JsonResponse({"error": "Parent folder not found."}, status=404)
            #print("parent_folder: ", parent_folder)
            new_folder = await create_folder_bd(folder_name, request.user, parent_folder)
            folder_name = new_folder.name
            folder_path = await consumers.get_path(parent_id)
            if folder_path != None:
                folder_path = os.path.join(folder_path, folder_name)
            else:
                folder_path = folder_name
            #print("FolderPath: ", folder_path)
            await create_folder_sync(folder_path)

            user_id = await get_user_id(request)
            await consumers.update_all_session_in_folder(parent_id, user_id)

            return JsonResponse({
                "action": "message",
                "message": "Folder created successfully.",
                "folder": {
                    "id": new_folder.id,
                    "name": new_folder.name,
                    "parent_id": new_folder.parent.id if new_folder.parent else None,
                },
            })
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)
@login_required
async def create_file(request):
    if request.method == "POST":
        try:
            folder_id = request.POST.get("folder_id")
            file_name = request.POST.get("name")
            file_content = request.POST.get("content", "").encode("utf-8")

            if not file_name:
                return JsonResponse({"error": "File name is required."}, status=400)

            folder = await get_folder(folder_id, request.user)

            new_file = await create_file_bd(file_name, request.user, folder)
            file_name = new_file.name

            fs = FileSystemStorage()
            folder_url = await consumers.get_path(folder_id)
            folder_url = os.path.join(folder_url, file_name)
            #print("File try to save to: ", folder_url)
            content_file = ContentFile(file_content, name=file_name)
            fs.save(folder_url, content_file)
            user_id = await get_user_id(request)
            await consumers.update_all_session_in_folder(folder_id, user_id)

            return JsonResponse({
                "message": "File created successfully.",
                "file": {"id": new_file.id, "name": new_file.name},
            })
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)
@login_required
def get_folder_contents(request):
    folder_id = request.GET.get("folder_id")

    try:
        if folder_id:
            folder = Folder.objects.filter(id=folder_id, user=request.user).first()
            if not folder:
                return JsonResponse({"error": "Folder not found."}, status=404)
        else:
            folder = None

        folders = Folder.objects.filter(parent=folder, user=request.user).values("id", "name", "is_public")
        files = File.objects.filter(folder=folder, user=request.user).values("id", "name", "is_public")

        return JsonResponse({
            "folders": list(folders),
            "files": list(files),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
@login_required
async def rename_file(request, file_id):
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        file_instance = await get_file_or_404(file_id)

        if new_name:
            file_path = await get_file_path(file_instance)
            if file_path == None:
                return JsonResponse({"error"}, status=404)

            new_name = await save_file(file_instance, new_name)

            if(os.path.isfile(file_path)):
                parent_directory = os.path.dirname(file_path)
                new_file_path = os.path.join(parent_directory, new_name)
                os.rename(file_path, new_file_path)
                #print("Rename file path: ", file_path, " to ", new_file_path)


            user_id = await get_user_id(request)
            await consumers.update_all_session_in_folder(file_instance.folder_id, user_id)

            return JsonResponse({'success': True, 'new_name': file_instance.name})

    return JsonResponse({'success': False}, status=400)
@login_required
async def rename_folder(request, folder_id):
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        folder_instance = await views_sync.get_folder_or_404_sync(folder_id)

        if new_name:
            folder_path = await consumers.get_path(folder_id)
            if folder_path == None:
                return JsonResponse({"error"}, status=404)

            new_name = await save_folder(folder_instance, new_name)

            if(os.path.isdir(folder_path)):
                parent_directory = os.path.dirname(folder_path)
                new_folder_path = os.path.join(parent_directory, new_name)
                os.rename(folder_path, new_folder_path)
                #print("Rename folder path: ", folder_path, " to ", new_folder_path)

            user_id = await get_user_id(request)
            await consumers.update_all_session_in_folder(folder_instance.parent_id, user_id)

            return JsonResponse({'success': True, 'new_name': folder_instance.name})

    return JsonResponse({'success': False}, status=400)
@login_required
async def toggle_file_access(request, file_id):
    if request.method == 'POST':
        file_instance = await get_file_or_404(file_id)
        await change_file_public(file_instance)

        user_id = await get_user_id(request)
        await consumers.update_all_session_in_folder(file_instance.folder_id, user_id)
        await public_recursive_parent(file_instance.folder)

        return JsonResponse({'success': True, 'is_public': file_instance.is_public})

    return JsonResponse({'success': False}, status=400)
@login_required
async def toggle_folder_access(request, folder_id):
    if request.method == 'POST':
        folder_instance = await get_folder_or_404_sync(folder_id)
        if folder_instance == None:
            return JsonResponse({'success': False}, status=404)
        access = not folder_instance.is_public
        await set_folder_public_async(folder_id, access)

        user_id = await get_user_id(request)
        await consumers.update_all_session_in_folder(folder_instance.parent_id, user_id)


        return JsonResponse({'success': True, 'is_public': access})

    return JsonResponse({'success': False}, status=400)
async def set_folder_public_async(folder_id, public=True):
    #print(f"set_folder_public_async> Start in folder_id: {folder_id}")
    folder_instance = await get_folder_or_404_sync(folder_id)

    async def public_recursive(folder, public=True):
        files = await get_child_files(folder)
        for file in files:
            await set_file_public(file, public)
        subfolders = await get_child_folders(folder)
        for subfolder in subfolders:
            await public_recursive(subfolder, public)
        await set_folder_public(folder, public)

        await consumers.update_all_session_in_folder(folder.id)
    await public_recursive(folder_instance, public)
    if(public==True):
        #print(f"set_folder_public_async> Try to find parent of folder: {folder_id}")
        await public_recursive_parent(folder_instance, prev_set_true = True)
async def public_recursive_parent(folder, prev_set_true = False):
    if(folder == None):
        return
    set_true = False
    folder_parent = await get_parent_folder(folder)
    if(folder_parent==None):
        #print(f"public_recursive_parent>Parent folder of: {folder.id} is None")
        return
    if(prev_set_true == True):
        await consumers.update_all_session_in_folder(folder_parent.id)
    #print(f"public_recursive_parent>Find parent folder of {folder.id}. Parent is {folder_parent.id}")
    if(not folder_parent.is_public):
        #print(f"public_recursive_parent>Set public to true for folder: {folder_parent.id}")
        await set_folder_public(folder_parent, True)
        set_true = True
    #else:
        #print(f"public_recursive_parent>Parent folder with id: {folder_parent.id} already public")
    await public_recursive_parent(folder_parent, prev_set_true=set_true)
@login_required
async def delete_folder(request, folder_id):
    try:
        if request.method == 'POST':
            folder_instance = await get_folder_or_404_sync(folder_id)
            if folder_instance == None:
                return JsonResponse({'success': False}, status=404)
            folder_parent_id = folder_instance.parent_id
            folder_path = await consumers.get_path(folder_id)
            #print("Delete folder path: ", folder_path)
            if folder_path == None:
                return JsonResponse({'success': False}, status=404)
            if(os.path.isdir(folder_path)):
                shutil.rmtree(folder_path)

            await delete_folder_async(folder_id)

            user_id = await get_user_id(request)
            await consumers.update_all_session_in_folder(folder_parent_id, user_id)

            return JsonResponse({'success': True})

        return JsonResponse({'success': False}, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
@login_required
async def delete_file(request, file_id):
    try:
        if request.method == 'POST':
            file_instance = await get_file_or_404(file_id)
            file_path = await get_file_path(file_instance)
            if os.path.isfile(file_path):
                os.remove(file_path)
            folder_id = file_instance.folder_id
            await delete_file_sync(file_instance)

            user_id = await get_user_id(request)
            await consumers.update_all_session_in_folder(folder_id, user_id)

            return JsonResponse({'success': True})

        return JsonResponse({'success': False}, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
