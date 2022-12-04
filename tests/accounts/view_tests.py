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


def test_search_account_view(admin_client, django_user_model):
    """Test the SearchAccountView with searching among existing accounts"""
    user1 = django_user_model.objects.create_user(
        username='user-one',
        email='userone@gmail.com',
        password='password'
    )
    user2 = django_user_model.objects.create_user(
        username='user-two',
        email='usertwo@gmail.com',
        password='password'
    )
    url = f"{reverse('accounts:search')}?q=user-tw"
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert user2 in response.context['page_obj']
    assert user1 not in response.context['page_obj']


def test_update_profile_view_status_code(admin_client):
    """Test ProfileUpdateView status code with logged in user"""
    url = reverse('accounts:edit_profile')
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_profile_update_view_edit_username(client: Client, django_user_model):
    """Test update the user's hide_email and username fileds"""
    user = django_user_model.objects.create_user(
        username='user-one',
        email='usertwo@gmail.com',
        password='password',

    )
    client.force_login(user)
    url = reverse('accounts:edit_profile')
    client.post(url, data={'username': 'foo', 'hide_email': False}, follow=True)
    foo = django_user_model.objects.get(email='usertwo@gmail.com')
    assert foo.username == 'foo'
    assert foo.hide_email == False
