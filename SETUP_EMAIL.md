# Configuración del Sistema de Email — Mazolo Contenedores

## 📧 Guía de Configuración de Gmail con App Password

Para que el sistema envíe correos de verificación reales, sigue estos pasos:

### Paso 1: Habilitar la autenticación de dos factores en Google

1. Ve a [https://myaccount.google.com](https://myaccount.google.com)
2. Haz clic en **Seguridad** (en el panel izquierdo)
3. Busca la sección **"Cómo iniciar sesión en Google"**
4. Habilita **"Verificación en dos pasos"** si aún no está activa
5. Sigue las instrucciones de Google para completar la configuración

### Paso 2: Generar una contraseña de aplicación

1. Ve a [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. En el menú desplegable **"Select device type"**, elige **"Windows"** (o tu SO)
3. En el menú desplegable **"Select app"**, elige **"Mail"**
4. Google generará una contraseña de 16 caracteres
5. **Copia esta contraseña** (sin espacios)

### Paso 3: Configurar el archivo `.env`

Edita el archivo `api_contenedores/.env` y reemplaza las siguientes líneas:

```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USER=tu_email@gmail.com        # ← Tu email de Gmail
MAIL_PASSWORD=xxxx xxxx xxxx xxxx   # ← La contraseña de aplicación (sin espacios)
MAIL_FROM=Mazolo Contenedores <tu_email@gmail.com>
```

**Ejemplo:**
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USER=libiacq24@gmail.com
MAIL_PASSWORD=abcdefghijklmnop
MAIL_FROM=Mazolo Contenedores <libiacq24@gmail.com>
```

### Paso 4: Reinicia el servidor

Una vez que hayas configurado el archivo `.env`, reinicia el servidor FastAPI:

```bash
cd api_contenedores
python -m uvicorn main:app --reload
```

## ✅ Verificación

Para probar que todo funciona:

1. Inicia sesión en el dashboard
2. Abre tu perfil (esquina inferior izquierda)
3. En la pestaña **Perfil**, asegúrate de que tu email esté correcto
4. Haz clic en **"Verificar email"**
5. Deberías recibir un correo con el código de 6 dígitos
6. Copia el código e ingresa en el campo correspondiente
7. ¡El email debe marcarse como verificado! ✓

## 🔒 Seguridad

- **Nunca compartas tu contraseña de aplicación** (app password)
- Esta contraseña solo funciona para acceso a Gmail desde esta aplicación
- Puedes revocar la contraseña en cualquier momento desde [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

## 🆘 Solución de problemas

| Problema | Solución |
|----------|----------|
| **Error: "Invalid credentials"** | Verifica que la contraseña de app esté correcta (sin espacios) |
| **Error: "Domain not found"** | El email tiene un dominio inválido (ej: `test@dominiofalso.xyz`) |
| **No llega el correo** | Revisa la carpeta de spam; Gmail a veces filtra correos automatizados |
| **Puerto 587 no disponible** | Cambia `MAIL_PORT` a `465` si tu firewall bloquea el 587 |
| **Variables SMTP no configuradas** | Asegúrate de que el archivo `.env` esté en `api_contenedores/` |

## 📚 Referencias

- [Guía oficial de Google para contraseñas de aplicación](https://support.google.com/accounts/answer/185833)
- [Documentación de aiosmtplib](https://aiosmtplib.readthedocs.io/)
- [Verificación de dominio con DNSPython](https://dnspython.readthedocs.io/)
