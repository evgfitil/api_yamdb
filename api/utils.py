from django.core import mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from api_yamdb.settings import NOREPLY_YAMDB_EMAIL


def email_is_valid(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def generate_mail(to_email, code):
    subject = 'Confirmation code for YaMDB'
    to = to_email
    text_content = f'''You requested a confirmation code for API YaMDB.\n
                        Attention, keep it a secret {code}'''
    mail.send_mail(
        subject, text_content,
        NOREPLY_YAMDB_EMAIL, [to],
        fail_silently=False
    )
