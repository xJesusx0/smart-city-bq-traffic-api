import traceback

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from app.core.settings import settings


class EmailService:
    def __init__(self, email_settings: ConnectionConfig) -> None:
        self.fm = FastMail(email_settings)

    async def send_welcome_email(
        self, recipient: EmailStr, full_name: str, token: str
    ) -> None:
        try:
            email_body = f"""
                <html>
                <body style="font-family: 'Segoe UI', Roboto, sans-serif; background-color: #f4f4f7; padding: 30px; color: #333;">
                    <table width="100%%" cellspacing="0" cellpadding="0" style="max-width: 600px; margin: auto; background-color: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="padding: 30px; text-align: center;">
                        <h2 style="color: #2E86C1;">👋 ¡Hola, {full_name}!</h2>
                        <p style="font-size: 16px; line-height: 1.5;">
                            Has sido invitado a formar parte del <strong>Sistema Inteligente de Gestión de Semáforos</strong>.
                        </p>
                        <p style="font-size: 16px; line-height: 1.5;">
                            Para activar tu cuenta y establecer tu contraseña, haz clic en el siguiente botón:
                        </p>
                        <a href="{settings.change_password_url}/change-password?token={token}"
                            style="display: inline-block; margin-top: 20px; padding: 12px 24px; background-color: #2E86C1; color: #fff; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            🔗 Activar mi cuenta
                        </a>
                        <p style="margin-top: 30px; font-size: 14px; color: #777;">
                            Si no esperabas este correo, simplemente ignóralo.
                        </p>
                        </td>
                    </tr>
                    </table>
                    <p style="text-align: center; margin-top: 20px; font-size: 12px; color: #aaa;">
                    © 2025 Smart City Traffic System — Todos los derechos reservados
                    </p>
                </body>
                </html>
                """

            # Mensaje HTML
            message = MessageSchema(
                subject="Bienvenido al Sistema de Gestión de Semáforos",
                recipients=[recipient],  # type: ignore
                body=email_body,
                subtype=MessageType.html,  # ✅ Enviar como HTML
            )

            await self.fm.send_message(message)

        except Exception:
            print(traceback.print_exc())
