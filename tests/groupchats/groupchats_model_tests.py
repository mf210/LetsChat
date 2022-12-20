import pytest

from groupchats.models import GroupChatRoom




@pytest.mark.django_db
def test_group_chat_room_str_method():
    group_chat_room_obj = GroupChatRoom.objects.create(name='group_one')
    assert str(group_chat_room_obj) == 'group_one'


@pytest.mark.django_db
def test_group_chat_room_channel_name_property():
    obj = GroupChatRoom.objects.create(name='group_one')
    assert obj.channel_name == f'GroupChatRoom-{obj.id}'