from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendgridBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        for message in email_messages:
            message_data = {
                'to': [{'email': message.to[0]}],
                'from': {'email': message.from_email},
                'subject': message.subject,
                'html_content': message.body,
            }
            mail = Mail(**message_data)
            sg.send(mail)
