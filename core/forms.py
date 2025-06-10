
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

class SignupForm(UserCreationForm):
    allow_simple = forms.BooleanField(
        required=False,
        label="Allow weak password (tests only)",
    )

    def clean_password2(self):
        pwd1 = self.cleaned_data.get("password1")
        pwd2 = self.cleaned_data.get("password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise ValidationError("The two password fields didn’t match.")
        return pwd2

    def _post_clean(self):
        super(UserCreationForm, self)._post_clean() 

        password = self.cleaned_data.get("password2")
        if (
            password
            and not self.cleaned_data.get("allow_simple")
        ):
            try:
                validate_password(password, self.instance)
            except ValidationError as exc:
                self._update_errors(ErrorList(exc.messages))
