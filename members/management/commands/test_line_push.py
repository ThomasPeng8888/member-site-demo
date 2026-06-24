from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from members.line_services import push_line_to_user
from members.models import MemberProfile


class Command(BaseCommand):
    help = "Send a test LINE push message to a bound member."

    def add_arguments(self, parser):
        parser.add_argument("keyword", help="會員編號、Email、Username 或 LINE 顯示名稱")
        parser.add_argument(
            "message",
            nargs="?",
            default="嘎比嘎比孔雀魚 LINE 通知測試成功 🐠",
            help="要傳送的測試訊息",
        )

    def handle(self, *args, **options):
        keyword = options["keyword"].strip()
        profile = (
            MemberProfile.objects
            .select_related("user")
            .filter(
                Q(member_no__iexact=keyword)
                | Q(user__email__iexact=keyword)
                | Q(user__username__iexact=keyword)
                | Q(line_display_name__icontains=keyword)
            )
            .first()
        )

        if not profile:
            raise CommandError("找不到會員。")

        if not profile.line_user_id:
            raise CommandError("這位會員尚未綁定 LINE。")

        ok = push_line_to_user(profile.user, options["message"])

        if ok:
            self.stdout.write(self.style.SUCCESS("LINE 測試訊息已送出。"))
        else:
            raise CommandError("LINE 測試訊息送出失敗，請確認 Channel access token 與會員是否已加入官方帳號。")
