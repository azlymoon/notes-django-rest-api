from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Note
from django.utils import timezone
from datetime import timedelta


class NoteAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.note = Note.objects.create(user=self.user, title='Sample Title', content='Sample Content')

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_note(self):
        url = '/notes/create/'
        data = {'title': 'New Note', 'content': 'A new note content.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 2)
        self.assertEqual(Note.objects.get(id=2).title, 'New Note')

    def test_retrieve_note_list(self):
        url = '/notes/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_retrieve_specific_note_unauthorized(self):
        other_user = User.objects.create_user(username='other', password='password')
        other_note = Note.objects.create(user=other_user, title='Other Title', content='Other Content')
        url = f'/notes/{other_note.id}/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_note(self):
        url = f'/notes/{self.note.id}/update/'
        data = {'title': 'Updated Note', 'content': 'Updated content.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Note')

    def test_update_note_after_one_day(self):
        self.note.created_at = timezone.now() - timedelta(days=1, minutes=1)
        self.note.save()
        url = f'/notes/{self.note.id}/update/'
        data = {'title': 'Updated Note', 'content': 'Updated content.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_note(self):
        url = f'/notes/{self.note.id}/delete/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 0)

    def test_delete_note_unauthorized(self):
        other_user = User.objects.create_user(username='other', password='password')
        other_note = Note.objects.create(user=other_user, title='Other Title', content='Other Content')
        url = f'/notes/{other_note.id}/delete/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(reverse('list_note'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_notes_by_date(self):
        Note.objects.create(user=self.user, title='Old Note', content='Old Content',
                            created_at=timezone.now() - timedelta(days=10))
        Note.objects.create(user=self.user, title='New Note', content='New Content',
                            created_at=timezone.now())

        response = self.client.get(reverse('list_note'), {'min_date': timezone.now() - timedelta(days=5)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_filter_notes_by_user(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        Note.objects.create(user=other_user, title='Other Note', content='Visible?')

        response = self.client.get(reverse('list_note'), {'user': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_delete_note_unauthorized(self):
        url = reverse('delete_note', kwargs={'pk': self.note.id})
        self.client.logout()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
