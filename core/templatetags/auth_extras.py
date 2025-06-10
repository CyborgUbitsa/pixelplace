from django import template

register = template.Library()

@register.filter
def has_group(user, name: str) -> bool:
    """{{ user|has_group:'artist' }} ⇒ True / False"""
    return (
        user.is_authenticated
        and user.groups.filter(name=name).exists()
    )
