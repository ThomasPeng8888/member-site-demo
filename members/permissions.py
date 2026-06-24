STAFF_TOOL_GROUPS = ("店員", "staff_cashier", "cashier")


def can_access_staff_tools(user):
    """Return True when a user can use in-store staff tools.

    Demo/admin users can keep using is_staff. For production, you can create a
    Django Group named「店員」or staff_cashier and add cashier accounts to it
    without giving them Django admin access.
    """
    if not getattr(user, "is_authenticated", False):
        return False

    if user.is_superuser or user.is_staff:
        return True

    return user.groups.filter(name__in=STAFF_TOOL_GROUPS).exists()
