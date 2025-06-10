
def is_moderator(user) -> bool:
    return user.is_authenticated and user.groups.filter(name="moderator").exists()
