import os
import traceback
from datetime import datetime
from uuid import UUID

from asgiref.sync import sync_to_async
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db.models import Q

import storage.views
import storage.views_sync
from storage.models import File, Folder

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
active_sessions_consumers = {}
active_sessions_folder = {}
active_sessions_user = {}
class FileManagerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"Attempting to connect user: {self.scope['user'].username}")

        session_id = self.scope['session'].session_key

        await self.channel_layer.group_add("WebFiles", self.channel_name)

        await self.accept()
        print(f"User {self.scope['user'].username} connected")
        active_sessions_user[session_id] = self.scope['user'].id
        active_sessions_consumers[session_id] = self
        await self.send_path_question()
    async def disconnect(self, close_code):
        print(f"Disconnecting user: {self.scope['user'].username}, close_code: {close_code}")

        session_id = self.scope['session'].session_key
        if session_id in active_sessions_folder:
            del active_sessions_folder[session_id]
        if session_id in active_sessions_user:
            del active_sessions_user[session_id]
        if session_id in active_sessions_consumers:
            del active_sessions_consumers[session_id]
        await self.channel_layer.group_discard("WebFiles", self.channel_name)
        print(f"User {self.scope['user'].username} disconnected")
    async def receive(self, text_data):
        print(f"Received data: {text_data}")

        data = json.loads(text_data)
        action = data.get("action")

        if action == "reload":
            folder_id = data.get("folder_id")
            print(f"Received reload action from user {self.scope['user'].username} for folder {folder_id}")
            await self.send_tree(self.scope['user'].id, folder_id)
        if action == "upload":
            await self.handle_file_upload(data)
        elif action == "back":
            folder_id = data.get("folder_id")
            print(f"Received back action from user {self.scope['user'].username} for folder {folder_id}")
            folders = await sync_to_async(list)(
                Folder.objects.filter(id=folder_id)
            )
            parent_folder_id = None
            for folder in folders:
                parent_folder_id = folder.parent_id
                break
            await self.send_tree(self.scope['user'].id, parent_folder_id)
        elif action == "answer_path":
            folder_path = data.get("tree_path")
            folder_id = await get_folder_id_from_path(folder_path)
            print("Answer folder_id for user ", self.scope['user'].username, " is ", folder_id)
            await self.send_tree(self.scope['user'].id, folder_id)
    async def send_tree(self, user_id, folder_id=None):
        try:
            session_id = self.scope['session'].session_key
            file_tree = await get_file_tree_for_user(user_id, folder_id)
            folder_access = await get_folder_access(user_id, folder_id)
            tree_path = await get_db_path(folder_id)
            print(f"Sending file tree to {self.scope['user'].username} in folder {folder_id} with access: ", folder_access)
            active_sessions_folder[session_id] = str(folder_id)
            print(f"Set folder_id: {folder_id} for session_id {session_id}",
                  folder_access)
            await self.send(text_data=json.dumps({
                "action": "update",
                "message": "reload",
                "tree": file_tree,
                "parentFolderId": folder_id,
                "folderAccess": folder_access,
                "treePath": tree_path
            }, cls=CustomJSONEncoder))
        except Exception as e:
            print(f"Error while fetching file tree for user {self.scope['user'].username}: {e}")
    async def send_path_question(self):
        try:
            print(f"Send path question to user: {self.scope['user'].username}")
            await self.send(text_data=json.dumps({
                "action": "question_path",
                "message": "path_question"
            }, cls=CustomJSONEncoder))
        except Exception as e:
            print(f"Error while send question for user {self.scope['user'].username}: {e}")
    async def update_file_tree(self, event):
        """
        Обработчик события обновления дерева файлов.
        """
        print(f"Sending updated file tree to user {self.scope['user'].username}")

        tree_data = event["tree"]
        parent_folder_id = event.get("parent_folder_id")  # Получаем идентификатор родительской папки

        await self.send(text_data=json.dumps({
            "action": "update",
            "tree": tree_data,
            "parentFolderId": parent_folder_id  # Отправляем идентификатор родительской папки
        }))

        print(f"File tree sent to user {self.scope['user'].username}")
    async def handle_file_upload(self, data):
        folder_id = None
        try:

            # Извлекаем данные из сообщения
            folder_id = data.get('folder_id')
            file_name = data.get('file_name')
            print("file_name: ", file_name)
            file_blob = data.get('file_blob')  # Здесь нужно будет обработать Blob-данные

            folder = await database_sync_to_async(lambda: Folder.objects.filter(id=folder_id, user=self.scope['user'].id).first())() if folder_id else None

            content_file = ContentFile(file_blob.encode('utf-8'), name=file_name)
            # Сохраняем файл в файловую систему
            fs = FileSystemStorage()
            folder_url = await get_path(folder_id)
            folder_url = os.path.join(folder_url, file_name)
            filename = fs.save(folder_url, content_file)
            file_url = folder_url
            print("File_url: ", file_url)
            print("Folder: ", folder)

            await database_sync_to_async(File.objects.create)(
                name=file_name,
                folder=folder,
                user=self.scope['user']
            )

            # После успешной загрузки отправляем ответ обратно клиенту
            await self.send(text_data=json.dumps({
                "action": "upload_success",
                "message": "File uploaded successfully!",
                "parentFolderId": folder_id
            }, cls=CustomJSONEncoder))
        except Exception as e:
            print(f"Error save file for user_id {self.scope['user'].id}: {e}")
            await self.send(text_data=json.dumps({
                "action": "upload_error",
                "message": "File uploaded successfully!",
                "parent_folder_id": folder_id
            }, cls=CustomJSONEncoder))
            raise
    def __str__(self):
        return self.scope['user'].username + ' with id: ' + self.scope['user'].id
async def get_path(folder_id):
    path_list = await get_db_path(folder_id)
    folder_path = FileSystemStorage().location
    folder_path = folder_path + path_list
    print("FolderPath: ", folder_path)
    if folder_path == FileSystemStorage().location:
        return None
    if folder_path == os.path.join(FileSystemStorage().location, ""):
        return None
    return folder_path
async def get_db_path(folder_id):
    path_list = []

    @sync_to_async
    def add_parent_sync(folder_id):
        folder = Folder.objects.filter(id=folder_id).first()
        if folder is None:
            print("CreateFolder - parent folder with id: ", folder_id, " does not exist")
            return None
        return folder

    async def add_parent(folder_id):
        folder = await add_parent_sync(folder_id)
        if folder is None:
            return
        path_list.append(folder.name)
        #print("Folder_id - parent_id: ", folder.parent_id)
        if folder.parent_id is not None:
            await add_parent(folder.parent_id)

    await add_parent(folder_id)

    path_list.reverse()
    folder_path = "\\"
    for path in path_list:
        folder_path = folder_path + "\\"  + path

    print("FolderDBPath: ", folder_path)
    return folder_path
async def get_folder_id_from_path(folder_path):
    if folder_path==None:
        return None
    path_parts = folder_path.split('/')
    path_parts = list(filter(bool, path_parts))
    #print("path_parts: ", path_parts)
    current_folder_id = None

    for part in path_parts:
        @sync_to_async
        def get_folder(part, current_folder_id):
            return Folder.objects.filter(Q(name=part) & Q(parent_id=current_folder_id)).first()
        folder = await get_folder(part, current_folder_id)
        if folder is None:
            print(f"Folder '{part}' not found.")
            return None
        #print("current_folder_id: ", current_folder_id, " find folder: ", folder.id)

        current_folder_id = folder.id

    print(f"Folder ID for path '{folder_path}': {current_folder_id}")
    return current_folder_id
async def update_all_session_in_folder(folder_id, current_user_id=None):
    print("update_all_session_in_folder> Start update all session in folder: ", folder_id, " from user: ", current_user_id)
    #print("update_all_session_in_folder> active_sessions_consumers: ", active_sessions_consumers)
    print("update_all_session_in_folder> active_sessions_folder: ", active_sessions_folder)
    #print("update_all_session_in_folder> active_sessions_user: ", active_sessions_user)
    for session_id, session_folder_id in active_sessions_folder.items():
        if session_folder_id == str(folder_id):
            user_id = active_sessions_user.get(session_id)
            if user_id is not None and (user_id != current_user_id or current_user_id ==None):
                consumer_instance = active_sessions_consumers[session_id]
                print("update_all_session_in_folder> Updated tree for session_id: ", session_id, " from user: ", current_user_id)
                await consumer_instance.send_tree(user_id, folder_id)
            else:
                print("update_all_session_in_folder> Not update tree for session_id: ", session_id, " from user: ", current_user_id, "and user_id: ", user_id)
        else:
                print("update_all_session_in_folder> session_folder_id: ", session_folder_id, " != folder_id: ", str(folder_id))

@sync_to_async
def get_folder_access(user_id, folder_id):
    try:
        folder = Folder.objects.filter(id=folder_id).first()
        if folder is None:
            #print(f"Folder access for user {user_id} false because folder does not exist")
            return False
        elif folder.user.id == user_id:
            #print(f"Folder access for user {user_id} true")
            return True
        #print(f"Folder access for user {user_id} false because folder user not equal to folder.user: {folder.user.id}")
        return False

    except Exception as e:
        traceback.print_exc()
        return False
async def get_file_tree_for_user(user_id, folder_id=None):
    try:

        tree = []
        if folder_id is None:
            # Получаем корневые папки
            root_folders = await sync_to_async(list)(
                Folder.objects.filter(Q(user_id=user_id) | Q(is_public=True), parent=None)
            )
            user_root = False
            for folder in root_folders:
                if folder.user_id == user_id:
                    user_root = True
                tree.append({
                    "id": folder.id,
                    "name": folder.name,
                    "type": "folder",
                    "is_public": folder.is_public,
                    "edit_access": folder.user_id == user_id,
                    "creation_date": folder.creation_date
                })
            if user_root==False:
                @sync_to_async
                def GetUser(user_id):
                    try:
                        return User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        return None
                user = await GetUser(user_id)
                folder = None
                if(user!=None):
                    folder = await storage.views_sync.create_folder_bd(user.username, user, None)
                    await storage.views_sync.create_folder_sync(FileSystemStorage().location + "\\" + user.username)
                    tree.append({
                        "id": folder.id,
                        "name": folder.name,
                        "type": "folder",
                        "is_public": folder.is_public,
                        "edit_access": folder.user_id == user_id,
                        "creation_date": folder.creation_date
                    })
        else:
            # Получаем содержимое указанной папки
            folders = await sync_to_async(list)(
                Folder.objects.filter(Q(user_id=user_id) | Q(is_public=True), parent=folder_id)
            )
            for folder in folders:
                tree.append({
                    "id": folder.id,
                    "name": folder.name,
                    "type": "folder",
                    "is_public": folder.is_public,
                    "edit_access": folder.user_id == user_id,
                    "creation_date": folder.creation_date
                })
            files = await sync_to_async(list)(
                File.objects.filter(Q(user=user_id) | Q(is_public=True), folder=folder_id)
            )
            for file in files:
                tree.append({
                    "id": file.id,
                    "name": file.name,
                    "type": "file",
                    "is_public": file.is_public,
                    "edit_access": file.user_id == user_id,
                    "creation_date": file.creation_date
                })

        return tree

    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching file tree for user_id {user_id}: {e}")
        raise

