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