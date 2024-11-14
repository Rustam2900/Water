import re
from django.core.exceptions import ValidationError


def phone_number_validator(value):
    regex = re.compile(r'^\+998 \d{2} \d{3} \d{2} \d{2}$')
    if not regex.match(value):
        raise ValidationError("error")

    if len(value) > 20:
        raise ValidationError("Phone number cannot be longer than 20 characters.")
