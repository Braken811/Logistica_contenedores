import os
import aiosmtplib
import dns.resolver
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USER = os.getenv("MAIL_USER", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", "")


def validate_email_domain(email: str) -> tuple[bool, str]:
    """
    Valida que el dominio del email tenga registros MX.
    Retorna (es_valido, mensaje_error)
    """
    if not email or "@" not in email:
        return False, "Email inválido"

    _, domain = email.rsplit("@", 1)

    try:
        records = dns.resolver.resolve(domain, "MX")
        if records:
            return True, ""
    except dns.resolver.NXDOMAIN:
        return False, f"El dominio '{domain}' no existe"
    except dns.resolver.NoAnswer:
        return False, f"El dominio '{domain}' no tiene registros de correo"
    except Exception as e:
        _logger.warning(f"Error validando dominio {domain}: {e}")
        return False, "No se pudo validar el dominio del email"

    return False, "El dominio del email no tiene servicio de correo"


async def send_verification_email(to_email: str, nombre: str, codigo: str) -> tuple[bool, str]:
    """
    Envía un correo de verificación con el código.
    Retorna (éxito, mensaje)
    """
    if not all([MAIL_USER, MAIL_PASSWORD, MAIL_FROM]):
        _logger.error("❌ Variables SMTP no configuradas")
        return False, "El sistema de email no está configurado"

    try:
        # Crear mensaje HTML
        html_content = f"""
        <html>
            <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%); padding: 40px; text-align: center; border-radius: 12px 12px 0 0;">
                    <h1 style="color: #fff; margin: 0; font-size: 28px;">🔐 Verificación de Email</h1>
                </div>
                <div style="background: #f5f5f5; padding: 40px; border-radius: 0 0 12px 12px;">
                    <p style="color: #333; font-size: 16px;">Hola <strong>{nombre}</strong>,</p>
                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        Has solicitado verificar tu dirección de correo electrónico en el <strong>Sistema Mazolo Contenedores</strong>.
                        Usa el siguiente código de verificación para completar el proceso:
                    </p>
                    <div style="background: white; border: 2px solid #d32f2f; border-radius: 8px; padding: 30px; text-align: center; margin: 30px 0;">
                        <span style="font-size: 32px; font-weight: bold; color: #d32f2f; letter-spacing: 8px;">{codigo}</span>
                    </div>
                    <p style="color: #999; font-size: 12px;">
                        ⏰ Este código expira en <strong>15 minutos</strong>. No compartas este código con nadie.
                    </p>
                    <p style="color: #666; font-size: 13px; line-height: 1.6; margin-top: 30px;">
                        Si no solicitaste esta verificación, puedes ignorar este correo.
                    </p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 11px; text-align: center;">
                        © 2026 Mazolo Contenedores — Sistema de Logística<br>
                        {datetime.now().strftime('%d de %B de %Y')}
                    </p>
                </div>
            </body>
        </html>
        """

        # Crear mensaje
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🔐 Código de verificación — Mazolo Contenedores"
        msg["From"] = MAIL_FROM
        msg["To"] = to_email

        # Versión texto plano como fallback
        text_content = f"Tu código de verificación es: {codigo}\n\nExpira en 15 minutos."
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        # Enviar
        async with aiosmtplib.SMTP(hostname=MAIL_SERVER, port=MAIL_PORT) as smtp:
            await smtp.starttls()
            await smtp.login(MAIL_USER, MAIL_PASSWORD)
            await smtp.send_message(msg)

        _logger.info(f"✅ Email de verificación enviado a {to_email}")
        return True, "Código enviado al email"

    except aiosmtplib.SMTPException as e:
        _logger.error(f"❌ Error SMTP enviando a {to_email}: {e}")
        return False, "Error al enviar el correo. Por favor, intenta más tarde."
    except Exception as e:
        _logger.error(f"❌ Error inesperado enviando email: {e}")
        return False, "Error al enviar el correo"
