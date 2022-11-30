from http import HTTPStatus

from django.test import Client
from django.urls import reverse




def test_profile_view_status_code_notloggedin_user(client: Client):
    """Check the status code of response with not logged in user"""
    url = reverse('accounts:profile', kwargs={'username': 'testuser'})
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND


def test_profile_view_status_code_loggedin_user(client: Client, django_user_model):
    """Check the status code of response with logged in user"""
    user = django_user_model.objects.create_user(username='test-user', email='testuser@gmail.com', password='password')
    client.force_login(user)
    url = reverse('accounts:profile', kwargs={'username': user.username})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


