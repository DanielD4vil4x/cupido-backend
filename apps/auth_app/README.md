# cupido-backend

## Requerimiento: Módulo de Registro de Usuario



Este módulo permite el registro de nuevos usuarios en la plataforma *cupido-backend*.  

El proceso asegura la validez, integridad y seguridad de la información suministrada, mediante validaciones estrictas de formato, dominio institucional, edad mínima y confirmación de cuenta por correo electrónico.



---



### Funcionalidades Principales



1. Formulario de Registro

  - Solicita todos los campos obligatorios: nombres, apellidos, correo institucional, programa académico, semestre, género, contraseña, número telefónico, y fecha de nacimiento.

  - Verifica que el correo tenga el dominio institucional `@unipamplona.edu.co`.

  - Comprueba que el correo no esté previamente registrado en la base de datos.

  - Valida que el usuario sea mayor de edad (≥18 años) según la fecha de nacimiento.

  - Exige que la contraseña y su confirmación coincidan exactamente.

  - Aplica políticas de seguridad para contraseñas, requiriendo longitud mínima, mayúsculas, números y caracteres especiales.

  - Verifica que todos los campos obligatorios estén diligenciados y tengan el formato correcto.



2. Validaciones y Confirmaciones

  - Solicita la aceptación explícita de los *Términos y Condiciones* y la *Política de Privacidad* antes del registro.

  - Crea un registro temporal en la base de datos encriptando la contraseña antes de su almacenamiento. Esto esta en revision

  - Envía un correo de verificación con enlace o código único para confirmar la propiedad del email.

  - Permite la activación de la cuenta al hacer clic en el enlace de verificación, cambiando su estado a “Activo”.

  - Muestra un mensaje de éxito y redirige al usuario a la página de inicio de sesión.



3. Mecanismos de Seguridad

  - Las contraseñas se almacenan utilizando algoritmos de hash robustos (bcrypt o Argon2) con salt aleatorio.

  - Toda la comunicación del formulario se cifra mediante protocolo HTTPS/SSL/TLS.

  - Incluye un sistema CAPTCHA (o equivalente) para prevenir registros automáticos.

  - Registra la dirección IP, fecha y hora de todos los intentos y registros exitosos para trazabilidad y auditoría.



4. Requisitos Adicionales

  - El campo “Semestre” aclara que para estudiantes es ≤12, y para otros usuarios, el valor es 13.

  - El sistema debe ser escalable y soportar un incremento en la cantidad de usuarios sin afectar el rendimiento.

  - El tiempo máximo de validación y respuesta del servidor no debe superar los 2 segundos bajo condiciones normales.



---



### Experiencia de Usuario y Compatibilidad



- El formulario de registro es responsive y funcional en los principales navegadores y dispositivos móviles.

- Se incluyen mensajes de error claros y orientativos que facilitan la corrección de datos.

- El botón “Registrar” valida toda la información antes de enviar el formulario.

- Se garantiza una interfaz intuitiva, clara y coherente con los estándares de accesibilidad web.



---



### Propósito del Requerimiento



El módulo de registro permite la incorporación de nuevos usuarios al sistema de forma segura, validada y trazable, asegurando que solo personas autorizadas y verificadas accedan a la plataforma.  

Su diseño protege la información personal, refuerza la autenticidad de las cuentas y contribuye al cumplimiento de políticas institucionales y de privacidad en *cupido-backend*.



# cupido-backend

## Requerimiento: Módulo de Inicio de Sesión (Login)

Este módulo permite a los usuarios autenticarse de forma segura en la plataforma mediante correo institucional y contraseña.  

El proceso incluye validaciones, políticas de seguridad, doble factor de autenticación (2FA) y mecanismos de recuperación de contraseña, garantizando la protección de las credenciales y la integridad de las sesiones activas.

---

## Funcionalidades Principales

1. **Formulario de acceso**
   - Solicita únicamente *Correo Electrónico* y *Contraseña*.
   - Verifica que el correo tenga formato institucional `@unipamplona.edu.co`.
   - Aplica políticas de seguridad a la contraseña (longitud mínima, uso de mayúsculas, números y caracteres especiales).

2. **Proceso de autenticación**
   - Al presionar *Iniciar sesión*, se envían las credenciales al servidor para validación segura.
   - Solo se permite el ingreso a cuentas activas y no bloqueadas.
   - Si las credenciales son inválidas o la cuenta está bloqueada, se muestra un mensaje de error específico.
   - Implementa autenticación en dos pasos (2FA) con código temporal de un solo uso y validez máxima de 5 minutos.
   - El sistema invalida el código después de usarlo y mantiene una sola sesión activa por usuario.

3. **Recuperación de contraseña**
   - Incluye el enlace “¿Olvidaste tu contraseña?” para iniciar el proceso.
   - Solicita únicamente el correo electrónico y valida su existencia.
   - Envía automáticamente un enlace cifrado de restablecimiento, válido por 30 minutos.
   - No revela si el correo existe, por motivos de seguridad.
   - Permite establecer una nueva contraseña cumpliendo las políticas de seguridad.
   - Notifica al usuario por correo o SMS sobre el restablecimiento exitoso y redirige a la página de inicio de sesión.

4. **Redirección post-autenticación**
   - Tras el inicio de sesión exitoso, el usuario es dirigido al *Dashboard (Match)*.
   - Si aún no ha definido sus preferencias, se le redirige al módulo de *Preferencias*.

---

### Reglas de Seguridad y Rendimiento

- **Cifrado de credenciales:** Todas las contraseñas se almacenan mediante algoritmos de hash robustos (bcrypt o Argon2) con salt aleatorio.
- **Comunicación segura:** Todo el tráfico del formulario está protegido con HTTPS/SSL/TLS.
- **Protección contra ataques automatizados:** Se integra Google reCAPTCHA v2 o v3 para evitar intentos masivos de acceso.
- **Bloqueo temporal:** La cuenta se bloquea tras múltiples intentos fallidos.
- **Cierre automático:** La sesión expira tras 15–30 minutos de inactividad.
- **Trazabilidad:** Se registran la dirección IP, fecha y hora de cada intento e inicio de sesión exitoso.
- **Rendimiento:** El proceso completo de autenticación no debe exceder los 2 segundos bajo carga normal.

---

### Compatibilidad y Usabilidad

- Interfaz responsive, funcional en navegadores y dispositivos móviles.
- Mensajes de error claros e informativos que guían al usuario.
- Cumplimiento de estándares de accesibilidad y experiencia de usuario.

---

### Propósito del Requerimiento

Este módulo garantiza la **autenticación segura, rápida y confiable** de los usuarios en el sistema.  
Su objetivo es proteger la información personal, prevenir accesos no autorizados y mantener la integridad del entorno digital de *cupido-backend*.

# auth_app

Módulo de autenticación del proyecto **cUPido**.

### Funcionalidades
- **Registro completo**: Validaciones de email institucional, edad ≥18, reCAPTCHA, FKs existentes
- **Verificación por código**: Redis + email con TTL y límites de intentos
- **Login con JWT**: SimpleJWT con blacklist para logout seguro
- **Gestión de contraseña**: Cambio y recuperación con tokens seguros
- **Desactivación de cuenta**: Soft delete con confirmación
- **Sesiones múltiples**: Logout individual y global
- **Rate limiting**: Protección contra abuso en endpoints críticos

### Endpoints
| Método | Ruta | Descripción |
|--------|------|--------------|
| POST | `/api/auth/register/` | Registra nuevo usuario con validaciones completas |
| POST | `/api/auth/verify-email/` | Verifica email con código y crea usuario |
| POST | `/api/auth/resend-code/` | Reenvía código de verificación |
| POST | `/api/auth/login/` | Autentica y devuelve tokens JWT |
| GET | `/api/auth/session/` | Devuelve info del usuario autenticado |
| POST | `/api/auth/logout/` | Cierra sesión actual |
| POST | `/api/auth/logout-all/` | Cierra todas las sesiones |
| POST | `/api/auth/password-change/` | Cambia contraseña (autenticado) |
| POST | `/api/auth/password-reset/` | Solicita recuperación de contraseña |
| POST | `/api/auth/password-reset-confirm/` | Confirma recuperación con token |
| POST | `/api/auth/deactivate/` | Desactiva cuenta de usuario |
