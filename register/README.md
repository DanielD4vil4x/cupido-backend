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

  - Crea un registro temporal en la base de datos encriptando la contraseña antes de su almacenamiento.

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



