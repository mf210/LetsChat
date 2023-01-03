import pytest

from privatechats.models import PrivateChatRoom, PrivateChatRoomMessage




@pytest.mark.django_db
def test_private_chat_room_str_method():
    """Test PrivateChatRoom __str__ method"""
    group_chat_room_obj = PrivateChatRoom.objects.create(name='user1user2')
    assert str(group_chat_room_obj) == 'user1user2'


def test_group_chat_room_message_str_method(django_user_model):
    """Test PrivateChatRoomMessage __str__ method"""
    user = django_user_model.objects.create(username='user1')
    room_obj = PrivateChatRoom.objects.create(name='user1user2')
    room_msg_obj = PrivateChatRoomMessage.objects.create(
        user=user,
        room=room_obj,
        content='Hello World!'
    )
    assert str(room_msg_obj) == f"user1user2:user1 | {room_msg_obj.timestamp} => Hello World!"

