# Ecommerce Reina Backend API

Este repositorio contiene el backend para el proyecto **Ecommerce Reina**, desarrollado con Django REST Framework.

## 🚀 Tecnologías

* **Python** 3.12
* **Django** 5.2
* **Django REST Framework**
* **Poetry** (Gestión de dependencias)
* **Docker & Docker Compose**
* **PostgreSQL**

---

## 📋 Pre-requisitos

Asegúrate de tener instalado lo siguiente antes de comenzar:

1.  [Docker Desktop](https://www.docker.com/products/docker-desktop)
2.  [Python 3.12+](https://www.python.org/downloads/)
3.  [Poetry](https://python-poetry.org/docs/#installation) (No usamos pip/virtualenv directamente)

---

## ⚙️ Configuración del Entorno (.env)

El proyecto requiere variables de entorno para funcionar. Crea un archivo llamado `.env` en la raíz del proyecto (al mismo nivel que `manage.py`) y pega el siguiente contenido:

```properties
# Configuración de Django
DEBUG=True
SECRET_KEY=tu_clave_secreta_super_segura_aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de Datos (Configuración para Docker)
# Si corres local sin Docker, cambia el HOST a 'localhost'
DB_NAME=ecommerceReinadb
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=db
DB_PORT=5432
Nota: La contraseña y usuario de base de datos coinciden con lo definido en el archivo docker-compose.yml.

🐳 Ejecución con Docker (Recomendado)
La forma más rápida de levantar el proyecto completo (Base de datos + Backend) es usando Docker Compose.

Construir y levantar los contenedores:

Bash

docker-compose up --build
Entrar al contenedor (opcional, para ejecutar comandos):

Bash

docker-compose exec web bash
El servidor estará corriendo en: http://localhost:8000

🛠️ Desarrollo Local (Sin Docker para el Backend)
Si prefieres correr el backend directamente en tu máquina (usando Poetry) pero manteniendo la base de datos en Docker (o una local):

1. Instalar dependencias
Usa Poetry para instalar todo lo definido en pyproject.toml:

Bash

poetry install
2. Activar el entorno virtual
Bash

poetry shell
3. Configurar la Base de Datos
Asegúrate de que la variable DB_HOST en tu archivo .env sea localhost si estás corriendo la base de datos localmente o si expusiste el puerto de Docker.

4. Aplicar Migraciones
Crea las tablas en la base de datos:

Bash

python manage.py migrate
5. Crear Superusuario (Admin)
Para acceder al panel de administración de Django:

Bash

python manage.py createsuperuser
6. Correr el Servidor
Bash

python manage.py runserver
📚 Documentación de la API
Gracias a drf-spectacular, la documentación interactiva se genera automáticamente. Una vez el servidor esté corriendo, visita:

Swagger UI: http://localhost:8000/api/docs/

Redoc: http://localhost:8000/api/redoc/

Archivo Schema (YAML): http://localhost:8000/api/schema/


📝 Changelog y Versionamiento
El proyecto usa Semantic Release para el versionamiento automático. Consulta el archivo CHANGELOG.md para ver el historial de cambios.

Actual versión: v1.2.0
