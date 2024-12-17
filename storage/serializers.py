# storage/serializers.py

from rest_framework import serializers
from .models import UserFolder, UserFile

class UserFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFolder
        fields = ['id', 'name', 'is_public', 'parent_folder', 'owner']

class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ['id', 'file', 'uploaded_at', 'is_public', 'folder']
