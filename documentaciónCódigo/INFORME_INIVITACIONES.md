# GoalApp · Documentación técnica del flujo de invitaciones por código

## 1. Objetivo

Definir el flujo backend para invitaciones a ligas en GoalApp cuando el acceso del usuario se realiza mediante **código de invitación**.

El flujo funcional es el siguiente:

**Recibe invitación → descarga/abre la app → introduce el código → entra en la liga con su rol**

Este documento cubre:

- modelo de datos

- lógica de negocio

- generación y validación del código

- envío del correo

- endpoints recomendados

- ejemplos de implementación en Python

- validaciones de seguridad

---

## 2. Resumen del flujo

### Flujo de alto nivel

1. Un administrador invita a un usuario a una liga.

2. El backend genera un **código de invitación**.

3. El backend guarda la invitación en base de datos.

4. El backend envía un correo con:

   - liga

   - rol asignado

   - código de invitación

   - pasos para acceder

5. El usuario abre la app.

6. El usuario pulsa en **“Unirme a una liga”**.

7. El usuario introduce el código.

8. El backend valida la invitación.

9. Si todo es correcto, el backend crea la relación **usuario ↔ liga ↔ rol**.

10. La invitación pasa a estado **accepted**.

---

## 3. Información que debe aparecer en el correo

El email de invitación debe mostrar claramente estos cuatro elementos:

| Elemento                 | Descripción                                     |
| ------------------------ | ----------------------------------------------- |
| **Liga**                 | Nombre de la liga a la que ha sido invitado     |
| **Rol asignado**         | Jugador, Entrenador o Delegado                  |
| **Código de invitación** | Código que el usuario debe introducir en la app |
| **Cómo acceder**         | Pasos claros para completar el alta             |

### Estructura recomendada del email

#### Cabecera

**Has sido invitado a una liga en GoalApp**

#### Bloque principal

- **Liga:** Liga Sevilla Premier

- **Rol asignado:** Entrenador

- **Código de invitación:** ABC-123-XYZ

#### CTA principal

- **Abrir app**

- o **Descargar app**

#### Bloque explicativo

**Cómo acceder**

1. Descarga o abre GoalApp.

2. Pulsa en **“Unirme a una liga”**.

3. Introduce este código: **ABC-123-XYZ**.

---

## 4. Modelo de datos recomendado

### Tabla `league_invitations`

Esta tabla representa la invitación pendiente o ya consumida.

```sql

id

league_id

email

role                -- "Jugador" | "Entrenador" | "Delegado"

invite_code         -- "ABC-123-XYZ"

status              -- "pending" | "accepted" | "expired" | "cancelled"

invited_by_user_id

accepted_by_user_id

expires_at

accepted_at

created_at

```

### Tabla `league_members`

Esta tabla representa la pertenencia real del usuario a la liga.

```sql

id

league_id

user_id

role

status              -- "active"

created_at

```

---

## 5. Principio clave del sistema

> El **rol real** del usuario no debe decidirlo el frontend al canjear el código.
> El frontend solo envía el código.
> El backend recupera el rol desde la invitación almacenada y crea el acceso con ese valor.

Esto evita:

- manipulación del rol desde cliente

- inconsistencias entre interfaz y permisos

- escalado indebido de privilegios

---

## 6. Flujo backend detallado

## 6.1 Crear invitación

### Entrada esperada desde frontend

```json
{
  "league_id": 12,

  "email": "carlos@correo.com",

  "name": "Carlos Ruiz",

  "role": "Entrenador",

  "invited_by_user_id": 5
}
```

### Qué debe hacer el backend

1. Validar que el usuario invitador tiene permisos para invitar.

2. Validar que el rol enviado es válido.

3. Generar un código de invitación único.

4. Calcular fecha de expiración.

5. Guardar la invitación en base de datos con estado `pending`.

6. Construir el email HTML.

7. Enviar el correo al usuario invitado.

8. Responder al frontend con confirmación.

---

## 6.2 Canjear invitación

### Entrada esperada desde frontend

```json
{
  "invite_code": "ABC-123-XYZ",

  "user_id": 42
}
```

### Qué debe hacer el backend

1. Buscar la invitación por código.

2. Validar que existe.

3. Validar que sigue en estado `pending`.

4. Validar que no ha expirado.

5. Validar, si aplica, que el email del usuario coincide con el invitado.

6. Comprobar que el usuario aún no pertenece a esa liga.

7. Insertar el registro en `league_members` con el rol almacenado en la invitación.

8. Marcar la invitación como `accepted`.

9. Devolver al frontend la liga y el rol final asignado.

---

## 7. Generación segura del código de invitación

Se recomienda usar `secrets` en Python para generar códigos no predecibles.

```python

import secrets



ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

# sin O, I, 0, 1 para evitar confusiones visuales



def generate_invite_code() -> str:

    parts = []

    for _ in range(3):

        part = "".join(secrets.choice(ALPHABET) for _ in range(3))

        parts.append(part)

    return "-".join(parts)

```

### Ejemplo de salida

```text

ABC-123-XYZ

```

### Recomendaciones

- usar caracteres fáciles de distinguir

- usar guiones para mejorar legibilidad

- convertir siempre a mayúsculas

- permitir validar aunque el usuario escriba el código sin guiones

---

## 8. Plantilla HTML del correo

El backend puede generar un HTML compatible con Gmail y otros clientes de correo usando CSS inline.

### Variables dinámicas recomendadas

```json
{
  "user_name": "Carlos Ruiz",

  "inviter_name": "Marta López",

  "league_name": "Liga Sevilla Premier",

  "role": "Entrenador",

  "invite_code": "ABC-123-XYZ",

  "app_link": "https://tuapp.com/open",

  "download_link": "https://tuapp.com/download"
}
```

### Constructor del HTML

```python

def build_invite_email_html(

    user_name: str,

    inviter_name: str,

    league_name: str,

    role: str,

    invite_code: str,

    app_link: str,

    download_link: str,

) -> str:

    return f"""

<!DOCTYPE html>

<html lang="es">

  <body style="margin:0; padding:0; background:#f3f4f6;">

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6; padding:24px 0;">

      <tr>

        <td align="center">

          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:640px; background:#161722; border-radius:24px; overflow:hidden;">

            <tr>

              <td style="padding:32px; background:#1b1d2a;">

                <div style="font-family:Arial, sans-serif; font-size:28px; font-weight:700; color:#fff;">

                  GoalApp

                </div>

                <div style="font-family:Arial, sans-serif; font-size:14px; color:#a7adbb;">

                  Invitación a liga

                </div>

              </td>

            </tr>



            <tr>

              <td style="padding:32px;">

                <div style="font-family:Arial, sans-serif; font-size:30px; line-height:36px; font-weight:700; color:#fff; margin-bottom:12px;">

                  Has sido invitado a una liga

                </div>



                <div style="font-family:Arial, sans-serif; font-size:16px; line-height:24px; color:#c7ccd7; margin-bottom:24px;">

                  Hola {user_name}, {inviter_name} te ha invitado a participar en

                  <strong style="color:#fff;">{league_name}</strong>.

                </div>



                <div style="background:#202231; border:1px solid #2b2f41; border-radius:18px; padding:18px; margin-bottom:12px;">

                  <div style="font-family:Arial, sans-serif; font-size:13px; color:#9ca3af;">Liga</div>

                  <div style="font-family:Arial, sans-serif; font-size:18px; font-weight:700; color:#fff; margin-top:6px;">

                    {league_name}

                  </div>

                </div>



                <div style="background:#202231; border:1px solid #2b2f41; border-radius:18px; padding:18px; margin-bottom:12px;">

                  <div style="font-family:Arial, sans-serif; font-size:13px; color:#9ca3af;">Rol asignado</div>

                  <div style="margin-top:8px;">

                    <span style="display:inline-block; background:#d7ff45; color:#111; font-family:Arial, sans-serif; font-size:14px; font-weight:700; border-radius:999px; padding:6px 12px;">

                      {role}

                    </span>

                  </div>

                </div>



                <div style="background:#202231; border:1px solid #3b4057; border-radius:18px; padding:18px; margin-bottom:24px;">

                  <div style="font-family:Arial, sans-serif; font-size:13px; color:#9ca3af;">Código de invitación</div>

                  <div style="font-family:Arial, sans-serif; font-size:28px; line-height:34px; font-weight:700; letter-spacing:2px; color:#fff; margin-top:8px;">

                    {invite_code}

                  </div>

                </div>



                <div style="background:#202231; border:1px solid #2b2f41; border-radius:18px; padding:18px; margin-bottom:24px;">

                  <div style="font-family:Arial, sans-serif; font-size:18px; font-weight:700; color:#fff; margin-bottom:12px;">

                    Cómo acceder

                  </div>

                  <div style="font-family:Arial, sans-serif; font-size:15px; line-height:24px; color:#c7ccd7;">

                    1. Descarga o abre GoalApp.<br/>

                    2. Pulsa en <strong style="color:#fff;">“Unirme a una liga”</strong>.<br/>

                    3. Introduce este código: <strong style="color:#fff;">{invite_code}</strong>.

                  </div>

                </div>



                <a href="{app_link}" style="display:inline-block; background:#d7ff45; color:#111; font-family:Arial, sans-serif; font-size:16px; font-weight:700; text-decoration:none; border-radius:14px; padding:16px 24px; margin-right:8px;">

                  Abrir app

                </a>



                <a href="{download_link}" style="display:inline-block; background:transparent; color:#fff; font-family:Arial, sans-serif; font-size:15px; font-weight:700; text-decoration:none; border:1px solid #3a3f57; border-radius:14px; padding:14px 22px;">

                  Descargar app

                </a>

              </td>

            </tr>

          </table>

        </td>

      </tr>

    </table>

  </body>

</html>

"""

```

---

## 9. Envío del correo con Python

```python

import smtplib

from email.message import EmailMessage



SMTP_HOST = "smtp.tudominio.com"

SMTP_PORT = 587

SMTP_USER = "no-reply@goalapp.com"

SMTP_PASSWORD = "TU_PASSWORD"



def send_invitation_email(

    to_email: str,

    subject: str,

    html_body: str,

    from_email: str = SMTP_USER,

) -> None:

    msg = EmailMessage()

    msg["Subject"] = subject

    msg["From"] = from_email

    msg["To"] = to_email



    msg.set_content(

        "Has sido invitado a una liga en GoalApp.\n"

        "Abre la app, pulsa en 'Unirme a una liga' e introduce tu código."

    )



    msg.add_alternative(html_body, subtype="html")



    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:

        smtp.starttls()

        smtp.login(SMTP_USER, SMTP_PASSWORD)

        smtp.send_message(msg)

```

### Recomendaciones de envío

- usar un correo remitente tipo `no-reply@goalapp.com`

- añadir versión texto plano además del HTML

- no bloquear la request principal si el SMTP tarda demasiado

- mover el envío a cola en producción

---

## 10. Servicio de creación de invitación

```python

from datetime import datetime, timedelta, timezone



def create_league_invitation(

    db,

    *,

    league_id: int,

    league_name: str,

    invitee_name: str,

    invitee_email: str,

    role: str,

    invited_by_user_id: int,

    inviter_name: str,

    app_link: str,

    download_link: str,

):

    if role not in {"Jugador", "Entrenador", "Delegado"}:

        raise ValueError("Rol no válido")



    invite_code = generate_invite_code()

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)



    while db.fetch_one(

        "SELECT id FROM league_invitations WHERE invite_code = %s",

        (invite_code,)

    ):

        invite_code = generate_invite_code()



    db.execute(

        """

        INSERT INTO league_invitations

        (league_id, email, role, invite_code, status, invited_by_user_id, expires_at, created_at)

        VALUES (%s, %s, %s, %s, 'pending', %s, %s, %s)

        """,

        (

            league_id,

            invitee_email.lower().strip(),

            role,

            invite_code,

            invited_by_user_id,

            expires_at,

            datetime.now(timezone.utc),

        ),

    )



    html = build_invite_email_html(

        user_name=invitee_name,

        inviter_name=inviter_name,

        league_name=league_name,

        role=role,

        invite_code=invite_code,

        app_link=app_link,

        download_link=download_link,

    )



    send_invitation_email(

        to_email=invitee_email,

        subject=f"Has sido invitado a {league_name} en GoalApp",

        html_body=html,

    )



    return {

        "ok": True,

        "invite_code": invite_code,

        "status": "pending",

    }

```

---

## 11. Servicio de canje de invitación

```python

from datetime import datetime, timezone



def redeem_league_invitation(db, *, invite_code: str, user_id: int, user_email: str):

    normalized_code = invite_code.strip().upper()



    invite = db.fetch_one(

        """

        SELECT id, league_id, email, role, status, expires_at

        FROM league_invitations

        WHERE invite_code = %s

        """,

        (normalized_code,)

    )



    if not invite:

        raise ValueError("Código no válido")



    if invite["status"] != "pending":

        raise ValueError("La invitación ya no está disponible")



    if invite["expires_at"] and invite["expires_at"] < datetime.now(timezone.utc):

        db.execute(

            "UPDATE league_invitations SET status = 'expired' WHERE id = %s",

            (invite["id"],)

        )

        raise ValueError("La invitación ha expirado")



    if invite["email"].lower().strip() != user_email.lower().strip():

        raise ValueError("Esta invitación pertenece a otro correo")



    existing_member = db.fetch_one(

        """

        SELECT id

        FROM league_members

        WHERE league_id = %s AND user_id = %s

        """,

        (invite["league_id"], user_id)

    )



    if not existing_member:

        db.execute(

            """

            INSERT INTO league_members (league_id, user_id, role, status, created_at)

            VALUES (%s, %s, %s, 'active', %s)

            """,

            (invite["league_id"], user_id, invite["role"], datetime.now(timezone.utc))

        )



    db.execute(

        """

        UPDATE league_invitations

        SET status = 'accepted',

            accepted_by_user_id = %s,

            accepted_at = %s

        WHERE id = %s

        """,

        (user_id, datetime.now(timezone.utc), invite["id"])

    )



    return {

        "ok": True,

        "league_id": invite["league_id"],

        "role": invite["role"],

        "status": "active",

    }

```

---

## 12. Endpoints recomendados

## 12.1 Crear invitación

**Endpoint**

```http

POST /api/leagues/{league_id}/invitations

```

**Body**

```json
{
  "name": "Carlos Ruiz",

  "email": "carlos@correo.com",

  "role": "Entrenador"
}
```

**Respuesta**

```json
{
  "ok": true,

  "invite_code": "ABC-123-XYZ",

  "status": "pending"
}
```

---

## 12.2 Canjear código

**Endpoint**

```http

POST /api/invitations/redeem

```

**Body**

```json
{
  "invite_code": "ABC-123-XYZ"
}
```

**Respuesta**

```json
{
  "ok": true,

  "league_id": 12,

  "role": "Entrenador",

  "status": "active"
}
```

---

## 13. Validaciones recomendadas

### Validaciones funcionales

- el invitador debe tener permisos para invitar

- el rol debe ser válido

- la invitación debe existir

- la invitación debe seguir pendiente

- la invitación no debe haber expirado

- el usuario no debe pertenecer ya a la liga

### Validaciones de seguridad

- el código debe ser difícil de adivinar

- el código debe poder usarse solo una vez

- el rol final debe salir de backend, nunca del cliente

- el correo del usuario autenticado debería coincidir con el correo invitado

- registrar quién invitó y quién aceptó

### Validaciones UX

- normalizar el código a mayúsculas

- permitir introducirlo con o sin guiones

- mostrar errores claros al usuario

- informar si el código ha expirado

---

## 14. Estados recomendados de invitación

| Estado      | Significado                         |
| ----------- | ----------------------------------- |
| `pending`   | Invitación creada y aún no aceptada |
| `accepted`  | Invitación canjeada correctamente   |
| `expired`   | Invitación caducada                 |
| `cancelled` | Invitación anulada manualmente      |

---

## 15. Errores típicos que debe contemplar el backend

```text

Código no válido

La invitación ya no está disponible

La invitación ha expirado

Esta invitación pertenece a otro correo

El usuario ya pertenece a esta liga

Rol no válido

No tienes permisos para invitar usuarios

```

---

## 16. Recomendación para producción

En desarrollo se puede enviar el correo dentro de la misma request.

En producción es preferible este enfoque:

1. crear invitación

2. guardar en base de datos

3. encolar tarea de envío de correo

4. responder rápido al frontend

5. dejar que un worker procese el email

### Ventajas

- menor latencia para el usuario

- menos errores visibles en frontend

- reintentos si falla el SMTP

- trazabilidad del estado del correo

---

## 17. Resumen técnico final

### Al invitar

1. generar código seguro

2. guardar invitación con liga, email, rol y código

3. enviar correo HTML con:

   - liga

   - rol

   - código

   - pasos de acceso

### Al introducir el código en la app

1. buscar invitación

2. validar estado y expiración

3. validar correo

4. crear miembro en la liga con el rol almacenado

5. marcar invitación como aceptada

---

## 18. Decisiones de producto que quedan fijadas con este diseño

- **Convierte la invitación en una entidad propia**

- **El rol queda fijado en backend**

- **La app accede a la liga mediante código, no mediante click directo en el email**

- **El correo tiene función informativa y operativa**

- **El alta real se completa dentro de la app**

---

## 19. Posible siguiente paso

Cuando se aterrice al stack concreto, conviene preparar una versión específica para:

- FastAPI

- Flask

- Django

Con:

- modelos reales

- endpoints reales

- validadores

- servicio SMTP o proveedor externo

- tests de integración
