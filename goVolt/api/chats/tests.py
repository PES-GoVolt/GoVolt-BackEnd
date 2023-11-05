from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
import json

class ChatsAPIViewTest(TestCase):
    def test_send_message(self):
        client = APIClient()
        url = reverse('chats-view')
        data = {
            "content" : "Hello",
            "room_name" : "random_room",
            "sender" : "Hi"
        }
        response = client.post(url,data, format= 'json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)