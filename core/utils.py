# core/utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def envoyer_email(sujet, template_html, context, destinataire):
    """
    Envoi email HTML.
    ⚠️ Ne bloque jamais l'application si l'email échoue.
    """
    try:
        html_content = render_to_string(template_html, context)

        email = EmailMultiAlternatives(
            subject=sujet,
            body="",  # fallback texte
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinataire],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    except Exception as e:
        logger.warning(f"⚠️ Email non envoyé à {destinataire} : {e}")
        # 👉 On ne lève PAS l’erreur

from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def envoyer_email_global(users, subject, message, site_url):
    """
    Envoi email global.
    ✔️ Continue même si Gmail limite / bloque
    ✔️ Aucun crash (pas d'erreur 500)
    """

    for user in users:
        if not user.email:
            continue

        try:
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
                body=message,  # fallback texte
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")

            # 🔒 PROTECTION CRITIQUE
            email.send()

        except Exception as e:
            logger.warning(
                f"⚠️ Email global non envoyé à {user.email} : {e}"
            )
            # 👉 on continue la boucle sans bloquer