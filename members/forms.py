from datetime import timedelta

from django.utils import timezone
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import MemberProfile
from aquarium.models import MemberTicket, PointTransaction

class MemberSignUpForm(UserCreationForm):
    first_name = forms.CharField(
        label="姓名",
        max_length=50,
        widget=forms.TextInput(attrs={"placeholder": "請輸入姓名"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )
    phone = forms.CharField(
        label="手機",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "09xxxxxxxx"}),
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "email",
            "phone",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("這個 Email 已經註冊過了。")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("這個 Email 已經註冊過了。")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        email = self.cleaned_data["email"].strip().lower()
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data["first_name"].strip()

        if commit:
            user.save()
            profile = MemberProfile.objects.create(
                user=user,
                phone=self.cleaned_data.get("phone", "").strip(),
                points=100,
            )

            MemberTicket.objects.create(
                user=user,
                title="新會員迎賓入館券",
                ticket_type="gift",
                valid_until=timezone.localdate() + timedelta(days=30),
            )

            PointTransaction.objects.create(
                user=user,
                transaction_type="earn",
                points=100,
                title="新會員註冊禮",
                note="加入 Aqua Member 自動獲得 100 點。",
            )
        return user