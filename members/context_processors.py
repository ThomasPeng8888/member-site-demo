from .permissions import can_access_staff_tools, can_manage_campaigns


def staff_tools(request):
    return {
        "can_access_staff_tools": can_access_staff_tools(request.user),
        "can_manage_campaigns": can_manage_campaigns(request.user),
    }
