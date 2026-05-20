# API REST

Una API REST (Representational State Transfer) es un estilo arquitectural para servicios web que usa HTTP como protocolo de comunicación.

## Principios clave

- **Sin estado (stateless)**: cada petición contiene toda la información necesaria; el servidor no guarda estado de sesión entre peticiones.
- **Interfaz uniforme**: los recursos se identifican con URLs; las operaciones se expresan con verbos HTTP.
- **Representaciones**: los recursos se transfieren en JSON, XML u otros formatos. JSON es el estándar de facto.

## Verbos HTTP principales

| Verbo  | Acción CRUD | Idempotente | Seguro |
|--------|-------------|-------------|--------|
| GET    | Read        | Sí          | Sí     |
| POST   | Create      | No          | No     |
| PUT    | Update (completo) | Sí   | No     |
| PATCH  | Update (parcial)  | No   | No     |
| DELETE | Delete      | Sí          | No     |

## Códigos de estado HTTP más comunes

- **200 OK** — petición procesada correctamente.
- **201 Created** — recurso creado; se devuelve en la cabecera `Location`.
- **204 No Content** — éxito sin cuerpo de respuesta (típico en DELETE).
- **400 Bad Request** — petición mal formada o con datos inválidos.
- **401 Unauthorized** — falta autenticación.
- **403 Forbidden** — autenticado pero sin permiso.
- **404 Not Found** — el recurso no existe.
- **422 Unprocessable Entity** — datos sintácticamente correctos pero semánticamente inválidos.
- **429 Too Many Requests** — límite de tasa superado.
- **500 Internal Server Error** — error inesperado en el servidor.
- **503 Service Unavailable** — servidor sobrecargado o en mantenimiento.

## Diseño de URLs

- Usar sustantivos en plural: `/users`, `/orders`.
- Anidar recursos relacionados: `/users/{id}/orders`.
- Evitar verbos en la URL: usar `DELETE /users/{id}` en lugar de `/deleteUser/{id}`.
- Versionar la API en el path: `/v1/users` o en la cabecera `Accept`.

## Buenas prácticas

1. Devolver siempre un cuerpo JSON estructurado, también en errores.
2. Usar HTTPS en producción.
3. Incluir un campo `request_id` en la respuesta para trazabilidad.
4. Documentar con OpenAPI/Swagger.
5. Implementar paginación para listados (`limit`, `offset` o cursores).
