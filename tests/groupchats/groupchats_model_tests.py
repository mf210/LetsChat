import pytest

from groupchats.models import GroupChatRoom, GroupChatRoomMessage




@pytest.mark.django_db
def test_group_chat_room_str_method():
    """Test GroupChatRoom __str__ method"""
    group_chat_room_obj = GroupChatRoom.objects.create(name='group_one')
    assert str(group_chat_room_obj) == 'group_one'


@pytest.mark.django_db
def test_group_chat_room_channel_name_property():
    """Test GroupChatRoom channel_name property"""
    obj = GroupChatRoom.objects.create(name='group_one')
    assert obj.channel_name == f'GroupChatRoom-{obj.id}'


def test_group_chat_room_message_str_method(django_user_model):
    """Test GroupChatRoomMessage __str__ method"""
    user = django_user_model.objects.create(username='user-one')
    room_obj = GroupChatRoom.objects.create(name='group-one')
    room_msg_obj = GroupChatRoomMessage.objects.create(
        user=user,
        room=room_obj,
        content='Hello World!'
    )
    assert str(room_msg_obj) == f"group-one:user-one | {room_msg_obj.timestamp} => Hello World!"

