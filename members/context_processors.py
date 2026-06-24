from .permissions import can_access_staff_tools


def staff_tools(request):
    return {
        "can_access_staff_tools": can_access_staff_tools(request.user),
    }
