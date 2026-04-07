# Implementaciones Futuras

Lista de implementaciones pendientes para el proyecto GoalApp.

---

## 1. Devolver rol del usuario en endpoint /auth/me

**Estado:** Pendiente  
**Prioridad:** Media  
**Fecha:** 2026-04-03

### Problema

El frontend espera el campo `rol_principal` en la respuesta del endpoint `/auth/me`, pero el backend no lo está devolviendo.

**Frontend (`authApi.ts`):**
```typescript
export interface User {
  id_usuario: number;
  nombre: string;
  email: string;
  telefono?: string;
  fecha_nacimiento?: string;
  rol_principal?: string;  // ← Esperado pero no devuelto
}
```

**Backend (`UsuarioResponse` en `schemas/usuario.py`):**
- No incluye ningún campo de roles
- El modelo `Usuario` tiene `roles` (relación N:N con tabla `roles`)

### Solución propuesta

1. Añadir campo `rol_principal` al schema `UsuarioResponse`:

```python
# app/schemas/usuario.py

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    genero: GeneroEnum | None = None
    telefono: str | None = None
    fecha_nacimiento: date | None = None
    imagen_url: str | None = None
    created_at: datetime
    updated_at: datetime
    rol_principal: str | None = None  # ← Nuevo campo

    class Config:
        from_attributes = True
```

2. Modificar el endpoint `/auth/me` para calcular el rol principal:

```python
# app/api/routers/auth.py

@router.get("/me", response_model=UsuarioResponse)
def obtener_usuario_actual(current_user = Depends(get_current_user)):
    # Obtener el primer rol como rol_principal
    rol_principal = None
    if current_user.roles:
        rol_principal = current_user.roles[0].nombre
    
    # Crear respuesta con el rol
    return UsuarioResponse(
        **current_user.__dict__,
        rol_principal=rol_principal
    )
```

### Archivos afectados

- `GoalApp_Backend/app/schemas/usuario.py`
- `GoalApp_Backend/app/api/routers/auth.py`

### Notas adicionales

- El modelo `Usuario` ya tiene la relación `roles` cargada con `lazy="selectin"`
- Considerar qué hacer si el usuario tiene múltiples roles (devolver lista completa en otro endpoint)