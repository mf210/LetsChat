from django import template

register = template.Library()



@register.filter()
def is_friend_with(loggedin_user, curr_user):
    """If logged in user is friend with current user then return true"""
    return loggedin_user.friendship.is_friend_with(curr_user)