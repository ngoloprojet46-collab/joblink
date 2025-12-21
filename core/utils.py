# core/utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def envoyer_email(sujet, template_html, context, destinataire):
    """
    Envoi email HTML professionnel via Brevo
    """
    html_content = render_to_string(template_html, context)

    email = EmailMultiAlternatives(
        subject=sujet,
        body="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[destinataire],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.timezone import now


def envoyer_email_global(users, subject, message, site_url):
    emails = []

    for user in users:
        if not user.email:
            continue

        context = {
            "user": user,
            "message": message,
            "site_url": site_url,
            "year": now().year,
            "logo_url": "https://res.cloudinary.com/dxndciemg/image/upload/v1765047604/joblink_%C3%A9_beq8ok.jpg",
        }

        html_content = render_to_string(
            "emails/email_global.html",
            context
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(html_content, "text/html")
        emails.append(email)

    # ✅ ENVOI CORRECT
    for email in emails:
        email.send(fail_silently=False)