from django.core.mail import EmailMessage


class Util:
    @staticmethod
    # @shared_task(name="send_email")
    def send_email(subject, body, recipients, attachements=None):
        """Send an email to recipients
        subject: subject of the email
        body: body of the email
        recipients: list of recipients

        Optional keyword arguments:
        attachements: list of files to attach to the email

        type: list of dicts with keys:
            - file_name: name of the file
            - content: content of the file
            - type: content type of the file
        """
        email = EmailMessage(
            subject=subject,
            body=body,
            to=recipients,
            from_email=None
        )
        if attachements:
            for attachement in attachements:
                email.attach(
                    attachement["file_name"], attachement["content"],
                    attachement["type"])
        email.content_subtype = 'html'
        email_status = email.send(fail_silently=False)
        return {"email_status": email_status, "result": "success"}
