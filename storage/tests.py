from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Folder

class FolderCreationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_create_folder_success(self):
        response = self.client.post(reverse('create_folder'), {
            'name': 'New Folder',
            'parent_id': ""
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Folder created successfully.")
        self.assertTrue(Folder.objects.filter(name='New Folder', user=self.user).exists())
