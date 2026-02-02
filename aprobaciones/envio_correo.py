# envio_correo.py
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
import logging
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Configurar logging (formato con hora y mensaje)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ServicioEnvioCorreo:
    """
    Servicio para envío de correos electrónicos usando Gmail SMTP
    """

    def __init__(self):
        logger.info("Inicializando ServicioEnvioCorreo...")

        self.smtp_server = "smtp.gmail.com"
        self.puerto = 587
        self.correo_remitente = f"{os.getenv('nombre_cuenta')}"
        self.password = os.getenv('password')
        self.correo_destinatario_pruebas = "correo"

        logger.info(f"Servidor SMTP: {self.smtp_server}:{self.puerto}")
        logger.info(f"Correo remitente configurado: {self.correo_remitente}")

        # Validar configuración
        # if not self.correo_remitente or not self.password:
        #     logger.error("❌ Faltan credenciales en variables de entorno")
        #     raise ValueError("Faltan credenciales de correo en las variables de entorno")
        # else:
        #     logger.info("✅ Credenciales cargadas correctamente")

    def enviar_correo(self, destinatario=None, asunto="", mensaje="", html_mensaje="", adjuntos=None):
        """
        Enviar correo electrónico
        """
        try:
            destinatario_final = destinatario or self.correo_destinatario_pruebas
            logger.info(f"Preparando correo para: {destinatario_final} | Asunto: {asunto}")

            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = self.correo_remitente
            msg['To'] = destinatario_final
            msg['Subject'] = asunto

            # Agregar cuerpo
            if mensaje:
                logger.info("Adjuntando cuerpo en texto plano")
                msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))

            if html_mensaje:
                logger.info("Adjuntando cuerpo en HTML")
                msg.attach(MIMEText(html_mensaje, 'html', 'utf-8'))

            # Adjuntos
            if adjuntos:
                for archivo in adjuntos:
                    logger.info(f"Procesando adjunto: {archivo}")
                    if os.path.exists(archivo):
                        self._agregar_adjunto(msg, archivo)
                    else:
                        logger.warning(f"⚠ Archivo no encontrado: {archivo}")

            # Conectar y enviar
            logger.info("Conectando al servidor SMTP...")
            with smtplib.SMTP(self.smtp_server, self.puerto) as server:
                server.starttls()
                logger.info("Conexión TLS iniciada")
                logger.info("Autenticando en el servidor SMTP...")
                server.login(self.correo_remitente, self.password)
                logger.info("✅ Autenticación exitosa")
                server.sendmail(self.correo_remitente, destinatario_final, msg.as_string())
                logger.info(f"✅ Correo enviado a {destinatario_final}")

            return True, f"Correo enviado exitosamente a {destinatario_final}"

        except smtplib.SMTPAuthenticationError:
            error_msg = "❌ Error de autenticación SMTP. Verifica las credenciales."
            logger.error(error_msg)
            return False, error_msg

        except smtplib.SMTPRecipientsRefused:
            error_msg = f"❌ Destinatario rechazado: {destinatario_final}"
            logger.error(error_msg)
            return False, error_msg

        except smtplib.SMTPException as e:
            error_msg = f"❌ Error SMTP: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"❌ Error inesperado enviando correo: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _agregar_adjunto(self, msg, ruta_archivo):
        """Agregar un archivo como adjunto al mensaje"""
        try:
            logger.info(f"Adjuntando archivo: {ruta_archivo}")
            with open(ruta_archivo, "rb") as archivo:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(archivo.read())

            encoders.encode_base64(parte)
            nombre_archivo = os.path.basename(ruta_archivo)
            parte.add_header(
                'Content-Disposition',
                f'attachment; filename="{nombre_archivo}"'
            )
            msg.attach(parte)
            logger.info(f"✅ Adjunto agregado: {nombre_archivo}")

        except Exception as e:
            logger.error(f"❌ Error agregando adjunto {ruta_archivo}: {str(e)}")

    def enviar_notificacion_solicitud(self, tipo_notificacion, datos_solicitud, destinatario=None):
        logger.info(f"Generando notificación tipo: {tipo_notificacion} | Datos: {datos_solicitud}")
        asunto, mensaje_texto, mensaje_html = self._generar_contenido_notificacion(
            tipo_notificacion, datos_solicitud
        )
        return self.enviar_correo(
            destinatario=destinatario,
            asunto=asunto,
            mensaje=mensaje_texto,
            html_mensaje=mensaje_html
        )

    def _generar_contenido_notificacion(self, tipo, datos):
        logger.info(f"Construyendo contenido de notificación para tipo: {tipo}")
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        if tipo == 'nueva_solicitud':
            asunto = f"🔔 Nueva Solicitud de Aprobación - {datos.get('titulo', 'Sin título')}"
            
            mensaje_texto = f"""
NUEVA SOLICITUD DE APROBACIÓN RECIBIDA

ID de Solicitud: {datos.get('id', 'N/A')}
Título: {datos.get('titulo', 'N/A')}
Tipo: {datos.get('tipo_formateado', datos.get('tipo_solicitud', 'N/A'))}
Solicitante: {datos.get('solicitante', 'N/A')}
Estado: {datos.get('estado', 'Pendiente').upper()}

Descripción:
{datos.get('descripcion', 'Sin descripción')}

Por favor, revisa y procesa esta solicitud en el sistema.

Fecha de notificación: {fecha_actual}
Sistema de Aprobaciones - Django App
            """
            
            mensaje_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <h2 style="color: #2c3e50; text-align: center;">🔔 Nueva Solicitud de Aprobación</h2>
                        
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #495057;">Detalles de la Solicitud</h3>
                            <p><strong>ID:</strong> {datos.get('id', 'N/A')}</p>
                            <p><strong>Título:</strong> {datos.get('titulo', 'N/A')}</p>
                            <p><strong>Tipo:</strong> {datos.get('tipo_formateado', datos.get('tipo_solicitud', 'N/A'))}</p>
                            <p><strong>Solicitante:</strong> {datos.get('solicitante', 'N/A')}</p>
                            <p><strong>Estado:</strong> <span style="color: #28a745; font-weight: bold;">{datos.get('estado', 'Pendiente').upper()}</span></p>
                        </div>
                        
                        <div style="background: #fff; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                            <h4 style="margin-top: 0; color: #007bff;">Descripción:</h4>
                            <p>{datos.get('descripcion', 'Sin descripción')}</p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <p style="color: #6c757d;">Por favor, revisa y procesa esta solicitud en el sistema.</p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="text-align: center; color: #6c757d; font-size: 12px;">
                            Sistema de Aprobaciones - Django App<br>
                            Fecha: {fecha_actual}
                        </p>
                    </div>
                </body>
            </html>
            """
            
        elif tipo == 'aprobada':
            asunto = f"✅ Solicitud Aprobada - {datos.get('titulo', 'Sin título')}"
            
            mensaje_texto = f"""
¡TU SOLICITUD HA SIDO APROBADA!

ID de Solicitud: {datos.get('id', 'N/A')}
Título: {datos.get('titulo', 'N/A')}
Estado: APROBADA

¡Felicitaciones! Tu solicitud ha sido aprobada exitosamente.
Ahora puedes proceder con la implementación según lo solicitado.

Fecha de aprobación: {fecha_actual}
Sistema de Aprobaciones - Django App
            """
            
            mensaje_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #28a745; border-radius: 10px;">
                        <h2 style="color: #28a745; text-align: center;">✅ ¡Solicitud Aprobada!</h2>
                        
                        <div style="background: #d4edda; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                            <h3 style="margin-top: 0; color: #155724;">¡Felicitaciones!</h3>
                            <p style="font-size: 18px; margin: 0;">Tu solicitud ha sido <strong>APROBADA</strong> exitosamente.</p>
                        </div>
                        
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p><strong>ID de Solicitud:</strong> {datos.get('id', 'N/A')}</p>
                            <p><strong>Título:</strong> {datos.get('titulo', 'N/A')}</p>
                            <p><strong>Estado:</strong> <span style="color: #28a745; font-weight: bold;">APROBADA</span></p>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                            <p style="margin: 0;"><strong>Próximos pasos:</strong> Ahora puedes proceder con la implementación según lo solicitado en tu solicitud.</p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="text-align: center; color: #6c757d; font-size: 12px;">
                            Sistema de Aprobaciones - Django App<br>
                            Fecha: {fecha_actual}
                        </p>
                    </div>
                </body>
            </html>
            """
            
        elif tipo == 'rechazada':
            asunto = f"❌ Solicitud Rechazada - {datos.get('titulo', 'Sin título')}"
            
            mensaje_texto = f"""
TU SOLICITUD HA SIDO RECHAZADA

ID de Solicitud: {datos.get('id', 'N/A')}
Título: {datos.get('titulo', 'N/A')}
Estado: RECHAZADA

Lamentablemente, tu solicitud ha sido rechazada.
Por favor, revisa los comentarios del revisor y considera crear una nueva solicitud con las correcciones necesarias.

Fecha de rechazo: {fecha_actual}
Sistema de Aprobaciones - Django App
            """
            
            mensaje_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #dc3545; border-radius: 10px;">
                        <h2 style="color: #dc3545; text-align: center;">❌ Solicitud Rechazada</h2>
                        
                        <div style="background: #f8d7da; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                            <p style="font-size: 16px; margin: 0; color: #721c24;">Lamentablemente, tu solicitud ha sido <strong>RECHAZADA</strong>.</p>
                        </div>
                        
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p><strong>ID de Solicitud:</strong> {datos.get('id', 'N/A')}</p>
                            <p><strong>Título:</strong> {datos.get('titulo', 'N/A')}</p>
                            <p><strong>Estado:</strong> <span style="color: #dc3545; font-weight: bold;">RECHAZADA</span></p>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                            <p style="margin: 0;"><strong>Qué hacer ahora:</strong> Por favor, revisa los comentarios del revisor y considera crear una nueva solicitud con las correcciones necesarias.</p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="text-align: center; color: #6c757d; font-size: 12px;">
                            Sistema de Aprobaciones - Django App<br>
                            Fecha: {fecha_actual}
                        </p>
                    </div>
                </body>
            </html>
            """
            
        else:  # actualizada u otro tipo
            asunto = f"📝 Actualización de Solicitud - {datos.get('titulo', 'Sin título')}"
            
            mensaje_texto = f"""
ACTUALIZACIÓN EN TU SOLICITUD

ID de Solicitud: {datos.get('id', 'N/A')}
Título: {datos.get('titulo', 'N/A')}
Estado Actual: {datos.get('estado', 'N/A').upper()}

Ha habido una actualización en tu solicitud.
Por favor, revisa el sistema para ver los detalles completos.

Fecha de actualización: {fecha_actual}
Sistema de Aprobaciones - Django App
            """
            
            mensaje_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #007bff; border-radius: 10px;">
                        <h2 style="color: #007bff; text-align: center;">📝 Actualización de Solicitud</h2>
                        
                        <div style="background: #cce7ff; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                            <p style="font-size: 16px; margin: 0; color: #004085;">Ha habido una <strong>ACTUALIZACIÓN</strong> en tu solicitud.</p>
                        </div>
                        
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p><strong>ID de Solicitud:</strong> {datos.get('id', 'N/A')}</p>
                            <p><strong>Título:</strong> {datos.get('titulo', 'N/A')}</p>
                            <p><strong>Estado Actual:</strong> <span style="color: #007bff; font-weight: bold;">{datos.get('estado', 'N/A').upper()}</span></p>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                            <p style="margin: 0;">Por favor, revisa el sistema para ver los detalles completos de la actualización.</p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="text-align: center; color: #6c757d; font-size: 12px;">
                            Sistema de Aprobaciones - Django App<br>
                            Fecha: {fecha_actual}
                        </p>
                    </div>
                </body>
            </html>
            """
        
        return asunto, mensaje_texto, mensaje_html

    def probar_conexion(self):
        """Probar la conexión SMTP y credenciales"""
        logger.info("Probando conexión SMTP...")
        try:
            with smtplib.SMTP(self.smtp_server, self.puerto) as server:
                server.starttls()
                server.login(self.correo_remitente, self.password)
            logger.info("✅ Conexión SMTP exitosa")
            return True, "Conexión exitosa con el servidor SMTP"
        except Exception as e:
            logger.error(f"❌ Error de conexión SMTP: {str(e)}")
            return False, f"Error de conexión: {str(e)}"


# Instancia global del servicio
logger.info("Creando instancia global de ServicioEnvioCorreo...")
servicio_correo = ServicioEnvioCorreo()
