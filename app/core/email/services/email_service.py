import traceback

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr


class EmailService:
    def __init__(self, email_settings: ConnectionConfig) -> None:
        self.fm = FastMail(email_settings)

    async def send_email(self, recipient: EmailStr, full_name: str, token: str) -> None:
        try:
            # Datos para plantilla o formato de mensaje
            template_data = {
                "full_name": full_name,
                "token": token,
            }

            # Mensaje HTML
            message = MessageSchema(
                subject="Bienvenido al Sistema de Gestión de Semáforos",
                recipients=[recipient],  # ✅ Debe ser una lista
                body=f"""
                    <html>
                        <body>
                            <h2>Hola, {full_name} 👋</h2>
                            <p>Has sido invitado al Sistema de Gestión de Semáforos.</p>
                            <p>Puedes activar tu cuenta usando el siguiente enlace:</p>
                            <a href="https://smartcitybq.com/activate?token={token}">
                                Activar cuenta
                            </a>
                            <p>Este enlace caduca en 48 horas.</p>
                        </body>
                    </html>
                """,
                subtype=MessageType.html,  # ✅ Enviar como HTML
            )

            await self.fm.send_message(message)

        except Exception:
            print(traceback.print_exc())
