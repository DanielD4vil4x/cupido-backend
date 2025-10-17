# cupido-backend

\## Requerimiento: Módulo de Inicio de Sesión (Login)



Este módulo permite a los usuarios autenticarse de forma segura en la plataforma mediante correo institucional y contraseña.  

El proceso incluye validaciones, políticas de seguridad, doble factor de autenticación (2FA) y mecanismos de recuperación de contraseña, garantizando la protección de las credenciales y la integridad de las sesiones activas.



---



\### Funcionalidades Principales



1\. \*\*Formulario de acceso\*\*

&nbsp;  - Solicita únicamente \*Correo Electrónico\* y \*Contraseña\*.

&nbsp;  - Verifica que el correo tenga formato institucional `@unipamplona.edu.co`.

&nbsp;  - Aplica políticas de seguridad a la contraseña (longitud mínima, uso de mayúsculas, números y caracteres especiales).



2\. \*\*Proceso de autenticación\*\*

&nbsp;  - Al presionar \*Iniciar sesión\*, se envían las credenciales al servidor para validación segura.

&nbsp;  - Solo se permite el ingreso a cuentas activas y no bloqueadas.

&nbsp;  - Si las credenciales son inválidas o la cuenta está bloqueada, se muestra un mensaje de error específico.

&nbsp;  - Implementa autenticación en dos pasos (2FA) con código temporal de un solo uso y validez máxima de 5 minutos.

&nbsp;  - El sistema invalida el código después de usarlo y mantiene una sola sesión activa por usuario.



3\. \*\*Recuperación de contraseña\*\*

&nbsp;  - Incluye el enlace “¿Olvidaste tu contraseña?” para iniciar el proceso.

&nbsp;  - Solicita únicamente el correo electrónico y valida su existencia.

&nbsp;  - Envía automáticamente un enlace cifrado de restablecimiento, válido por 30 minutos.

&nbsp;  - No revela si el correo existe, por motivos de seguridad.

&nbsp;  - Permite establecer una nueva contraseña cumpliendo las políticas de seguridad.

&nbsp;  - Notifica al usuario por correo o SMS sobre el restablecimiento exitoso y redirige a la página de inicio de sesión.



4\. \*\*Redirección post-autenticación\*\*

&nbsp;  - Tras el inicio de sesión exitoso, el usuario es dirigido al \*Dashboard (Match)\*.

&nbsp;  - Si aún no ha definido sus preferencias, se le redirige al módulo de \*Preferencias\*.



---



\### Reglas de Seguridad y Rendimiento



\- \*\*Cifrado de credenciales:\*\* Todas las contraseñas se almacenan mediante algoritmos de hash robustos (bcrypt o Argon2) con salt aleatorio.

\- \*\*Comunicación segura:\*\* Todo el tráfico del formulario está protegido con HTTPS/SSL/TLS.

\- \*\*Protección contra ataques automatizados:\*\* Se integra Google reCAPTCHA v2 o v3 para evitar intentos masivos de acceso.

\- \*\*Bloqueo temporal:\*\* La cuenta se bloquea tras múltiples intentos fallidos.

\- \*\*Cierre automático:\*\* La sesión expira tras 15–30 minutos de inactividad.

\- \*\*Trazabilidad:\*\* Se registran la dirección IP, fecha y hora de cada intento e inicio de sesión exitoso.

\- \*\*Rendimiento:\*\* El proceso completo de autenticación no debe exceder los 2 segundos bajo carga normal.



---



\### Compatibilidad y Usabilidad



\- Interfaz responsive, funcional en navegadores y dispositivos móviles.

\- Mensajes de error claros e informativos que guían al usuario.

\- Cumplimiento de estándares de accesibilidad y experiencia de usuario.



---



\### Propósito del Requerimiento



Este módulo garantiza la \*\*autenticación segura, rápida y confiable\*\* de los usuarios en el sistema.  

Su objetivo es proteger la información personal, prevenir accesos no autorizados y mantener la integridad del entorno digital de \*cupido-backend\*.



