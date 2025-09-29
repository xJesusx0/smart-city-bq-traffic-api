# Traffic API

Este es el componente `traffic-api` para el proyecto "Sistema Inteligente de Gestión de Semáforos".

Esta API actúa como un **Backend For Frontend (BFF)**, gestionando la autenticación, la persistencia de datos y la exposición de información al cliente web de monitoreo y administración.

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instaladas las siguientes herramientas:

- **Python 3.13**. Se recomienda gestionarlo con `pyenv` para facilitar el cambio de versiones:

  ```bash
  # Instalar pyenv (ejemplo para macOS/Linux con Homebrew)
  brew install pyenv

  # Instalar la versión de Python requerida
  pyenv install 3.13
  ```

- **uv**: Un gestor de paquetes y entornos virtuales de Python extremadamente rápido. Puedes instalarlo con:
  ```bash
  pip install uv
  # O con curl/powershell (ver documentación oficial)
  ```

---

## Instalación y Configuración

Sigue estos pasos para levantar el entorno de desarrollo local.

### 1. Clonar el Repositorio

```bash
# (Si aún no lo has hecho)
git clone https://github.com/xJesusx0/smart-city-bq-traffic-api
cd traffic-api
```

### 2. Configurar el Entorno de Python

Activa la versión correcta de Python y crea un entorno virtual con `uv`.

```bash
# Activa la versión local de Python (lee el archivo .python-version)
pyenv local 3.13

# Crea un entorno virtual en la carpeta .venv
uv venv

# Activa el entorno virtual
source .venv/bin/activate
```

### 3. Instalar Dependencias

Usa `uv` para sincronizar las dependencias del proyecto desde `pyproject.toml`.

```bash
# Instalará todas las dependencias listadas en pyproject.toml
uv sync
```

### 4. Configurar Variables de Entorno

La aplicación se configura mediante un archivo `.env`. Crea este archivo en la raíz del proyecto.

```bash
cp .env.example .env  # Si existiera un .env.example, o créalo manualmente
```

Tu archivo `.env` debe contener las siguientes variables. La más importante es `DB_URL`.

```dotenv
# .env

# URL de conexión a la base de datos. Imprescindible.
# Ejemplo para MySQL: "mysql+pymysql://user:password@host:port/database"
DB_URL=

# Entorno de la aplicación (development o production)
ENV=development

# Configuración del servidor de la aplicación
APP_HOST=0.0.0.0
APP_PORT=8080

# Clave secreta para firmar los tokens JWT
JWT_SECRET_KEY="tu-clave-secreta-aqui"

# Algoritmo para los tokens JWT
JWT_ALGORITHM=HS256

# Tiempo de expiración de los tokens (en días)
JWT_EXPIRATION_TIME=1

# Lista de hosts permitidos, separados por comas
ALLOWED_HOSTS="http://localhost:5173,http://127.0.0.1:5173"
```

**Nota:** Asegúrate de reemplazar los valores de ejemplo con tu configuración real, especialmente `DB_URL` y `JWT_SECRET_KEY`.

---

## Cómo Ejecutar la Aplicación

Una vez que el entorno virtual esté activado y el archivo `.env` configurado, puedes iniciar el servidor.

```bash
python src/run.py
```

El servidor se iniciará en la dirección y puerto especificados en tu configuración (por defecto, `http://0.0.0.0:8080`).

Gracias al modo `development`, el servidor se recargará automáticamente cada vez que realices un cambio en el código fuente.
