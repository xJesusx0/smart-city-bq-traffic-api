# Contexto del Proyecto: Traffic API (Smart City)

## 1. Resumen del Proyecto

**Traffic API** es el componente de backend para un sistema de gestión de semáforos inteligentes. Su finalidad es centralizar la autenticación, autorización y orquestación de operaciones relacionadas con el control del tráfico urbano en tiempo real.

- **Objetivos:**
  - Proveer una API segura y escalable para la gestión de usuarios y sistemas (semáforos, sensores).
  - Servir como punto de entrada para la recolección de datos de tráfico.
  - Exponer endpoints para el control y monitoreo remoto de la infraestructura de semáforos.

- **Alcance Actual:** El proyecto se encuentra en su fase inicial, con el módulo de autenticación y autorización (Auth) como principal funcionalidad implementada. El almacén de usuarios es estático y está definido en el código para fines de demostración.

---

## 2. Arquitectura General

Aunque el estado actual es un monolito, la **arquitectura objetivo** se basa en un enfoque de microservicios para garantizar la escalabilidad y resiliencia del sistema.

- **Microservicios Propuestos:**
  - **Auth Service (Actual):** Gestiona la identidad, autenticación (JWT) y permisos de usuarios y otros servicios.
  - **Traffic Control Service:** Lógica de negocio para el control de los semáforos (cambios de estado, planes de tiempo, modo emergencia).
  - **Data Ingestion Service:** Recolecta y procesa datos de sensores de tráfico, cámaras, etc.
  - **Monitoring Service:** Provee datos sobre el estado y rendimiento de la infraestructura.

- **Base de Datos:** No implementada aún. Se recomienda **PostgreSQL** con **PostGIS** para datos relacionales y geoespaciales, y una base de datos de series temporales como **TimescaleDB** o **InfluxDB** para métricas de tráfico.

- **Frontend:** Una aplicación web (no desarrollada) que consumiría esta API para visualizar el estado del tráfico, gestionar la configuración y generar reportes.

- **Flujo de Datos (Objetivo):**
  1. Un usuario (operador) o un sistema se autentica contra el **Auth Service** y obtiene un JWT.
  2. Con el JWT, el cliente realiza peticiones a los microservicios correspondientes (ej. cambiar el estado de un semáforo a través del **Traffic Control Service**).
  3. Los servicios se comunican entre sí de forma asíncrona mediante un **Message Broker** (ej. RabbitMQ) para notificar eventos importantes (ej. alta densidad de tráfico).

---

## 3. Dependencias y Entorno

- **Lenguaje:** Python 3.13
- **Framework Principal:** FastAPI
- **Servidor ASGI:** Uvicorn
- **Autenticación y Seguridad:**
  - `python-jose` y `pyjwt`: Para la creación y validación de JSON Web Tokens (JWT).
  - `bcrypt`: Para el hashing de contraseñas. Se puede considerar migrar a `passlib` para mayor flexibilidad de algoritmos.
  - `OAuth2PasswordBearer`: Implementación del flujo de obtención de tokens.
- **Configuración:** `pydantic-settings` para gestionar variables de entorno (fichero `.env`).
- **Gestor de Paquetes y Entorno:** `uv`.

---

## 4. Estructura de Carpetas

El proyecto sigue una estructura modular y limpia para facilitar el mantenimiento.

```
src/
├── app/
│   ├── __init__.py
│   ├── main.py             # Instancia de FastAPI y routers principales.
│   ├── auth/               # Módulo de autenticación.
│   │   ├── models/         # Modelos Pydantic (User, Token).
│   │   ├── routes/         # Endpoints (/login, /me).
│   │   └── services/       # Lógica de negocio (autenticación de usuario).
│   └── core/               # Componentes transversales.
│       ├── encryption_service.py # Hashing y verificación de contraseñas.
│       ├── jwt_service.py    # Creación y decodificación de JWTs.
│       ├── security.py       # Esquema de seguridad OAuth2.
│       └── settings.py       # Configuración de la aplicación.
└── run.py                  # Punto de entrada para ejecutar la app con Uvicorn.
```

---

## 5. Flujo de Ejecución

1.  **Inicio de la Aplicación:**
    - La aplicación se inicia ejecutando `python src/run.py`.
    - `run.py` utiliza `uvicorn` para levantar el servidor ASGI, cargando la instancia de `FastAPI` definida en `app/main.py`.
    - La configuración (host, puerto, modo debug) se carga desde `app/core/settings.py`.

2.  **Endpoints Principales:**
    - `POST /api/auth/login`:
      - Recibe `username` y `password` en un formulario.
      - `AuthService` valida las credenciales contra el usuario estático.
      - Si son válidas, `JwtService` genera un `access_token` y lo devuelve.
    - `GET /api/auth/me`:
      - Endpoint protegido que requiere un `Authorization: Bearer <token>`.
      - El `token` es validado por la dependencia `get_current_active_user`.
      - Devuelve la información del usuario autenticado.

---

## 6. Notas Importantes

- **Limitación de `bcrypt`:** El algoritmo `bcrypt` tiene una limitación intrínseca: solo procesa los primeros 72 bytes de una contraseña. Cualquier carácter más allá de ese límite es ignorado silenciosamente. Es crucial asegurar que las políticas de contraseñas no excedan este límite o considerar otros algoritmos si se requieren contraseñas más largas.
- **Usuario Estático:** Actualmente, el `AuthService` utiliza un usuario hardcodeado (`find_by_username`). El siguiente paso es conectar el servicio a una base de datos real de usuarios.
- **Gestión de Dependencias:** Se recomienda utilizar un contenedor de inyección de dependencias (ej. `dependency-injector`) a medida que el proyecto crezca para gestionar la creación de instancias de servicios y repositorios de forma centralizada.
- **Despliegue:** Para producción, no se debe usar el modo `reload` de Uvicorn. Se recomienda ejecutar Uvicorn detrás de un servidor proxy inverso como Nginx y usar un gestor de procesos como Gunicorn para manejar los workers de Uvicorn.