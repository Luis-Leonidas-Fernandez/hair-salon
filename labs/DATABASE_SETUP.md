# Database setup — After Look

Esta guía prepara PostgreSQL para el proyecto **After Look** en **Windows** y **macOS**.

Al finalizar deberías tener:

```text
PostgreSQL instalado
PostgreSQL iniciado
base de datos afterlook creada
archivo .env configurado
proyecto listo para conectarse a PostgreSQL
```

> La base de datos se llama `afterlook`. Usá siempre ese nombre en los comandos y en `DATABASE_URL`.

---

## 1. Requisitos

Necesitás:

- PostgreSQL instalado;
- Python instalado;
- una terminal: PowerShell en Windows o Terminal en macOS;
- acceso a la carpeta raíz del proyecto.

La aplicación usa:

```text
PostgreSQL + asyncpg + SQLAlchemy + Alembic
```

---

## 2. Verificar la instalación de PostgreSQL

### Windows — PowerShell

```powershell
psql --version
```

### macOS — Terminal

```bash
psql --version
```

Resultado esperado:

```text
psql (PostgreSQL) 18.x
```

Si `psql` no se reconoce:

- en Windows, agregá la carpeta `bin` de PostgreSQL al `PATH`, normalmente similar a `C:\Program Files\PostgreSQL\18\bin`;
- en macOS con Homebrew, instalá PostgreSQL con `brew install postgresql@18` y agregá su carpeta `bin` al `PATH` si fuera necesario.

La versión puede ser diferente. Lo importante es que el comando `psql` funcione.

---

## 3. Iniciar PostgreSQL

### Windows

En PowerShell:

```powershell
Get-Service *postgres*
```

Buscá un servicio cuyo estado sea `Running`. Si está detenido, abrí PowerShell como administrador y ejecutá el comando usando el nombre real del servicio:

```powershell
Start-Service -Name "postgresql-x64-18"
```

> El nombre puede cambiar según la versión instalada. Usá exactamente el valor que aparece en la columna `Name`.

También podés iniciar PostgreSQL desde **Services** de Windows buscando un servicio que comience con `postgresql`.

### macOS con Homebrew

```bash
brew services list
brew services start postgresql@18
```

Si instalaste otra versión, reemplazá `postgresql@18` por el nombre correspondiente. Para detenerlo:

```bash
brew services stop postgresql@18
```

Verificá que PostgreSQL responda:

```bash
pg_isready
```

Resultado esperado:

```text
localhost:5432 - accepting connections
```

---

## 4. Crear la base de datos `afterlook`

La forma más portable es crearla desde la terminal con `createdb`.

### Windows — PowerShell

```powershell
createdb -U postgres afterlook
```

### macOS — Terminal

Como tu usuario macOS es `luis`, `psql` intenta buscar inicialmente una base llamada `luis`. Si esa base no existe, usá `template1` como base administrativa:

```bash
createdb -d template1 afterlook
```

Si la base ya existe, PostgreSQL mostrará un aviso. En ese caso no la borres: verificá que sea la base correcta.

También podés entrar al cliente SQL.

Windows:

```powershell
psql -U postgres
```

macOS con Homebrew:

```bash
psql -d template1
```

Y ejecutar:

```sql
CREATE DATABASE afterlook;
```

Para salir:

```sql
\q
```

> En macOS con Homebrew, PostgreSQL normalmente crea un rol con el mismo nombre que tu usuario del sistema. En tu caso, el rol es `luis`, pero la base `luis` todavía no existe. Por eso se usa `template1` como base administrativa al crear `afterlook`.

---

## 5. Verificar que la base exista

En Windows:

```powershell
psql -U postgres -l
```

En macOS con Homebrew:

```bash
psql -d template1 -l
```

Buscá:

```text
afterlook
```

También podés comprobar la conexión directamente:

```bash
psql -d afterlook -c "SELECT current_database();"
```

Resultado esperado:

```text
 current_database
------------------
 afterlook
```

---

## 6. Configurar el archivo `.env`

Desde la raíz del proyecto, copiá el archivo de ejemplo.

### Windows — PowerShell

```powershell
Copy-Item .env.example .env
```

### macOS — Terminal

```bash
cp .env.example .env
```

El archivo `.env` debe contener:

```env
APP_NAME=After Look
ENVIRONMENT=development
# macOS con PostgreSQL instalado mediante Homebrew
DATABASE_URL=postgresql+asyncpg://luis@localhost:5432/afterlook
SECRET_KEY=replace-this-value
```

En Windows, o si configuraste un usuario con contraseña, usá:

```env
DATABASE_URL=postgresql+asyncpg://USUARIO:TU_PASSWORD@localhost:5432/afterlook
```

Reemplazá `USUARIO` y `TU_PASSWORD` por los datos reales del usuario de PostgreSQL. En tu macOS, la URL habitual es la mostrada arriba y no necesita contraseña si tu instalación local usa autenticación por usuario del sistema.

Si Alembic muestra: 

```text
asyncpg.exceptions.InvalidAuthorizationSpecificationError: role "postgres" does not exist
```

revisá que tu `.env` no tenga una URL con `postgres:TU_PASSWORD`. Para tu instalación Homebrew, debe quedar así:

```env
DATABASE_URL=postgresql+asyncpg://luis@localhost:5432/afterlook
```

La URL se interpreta así:

```text
postgresql+asyncpg  tipo de base y driver de Python
USUARIO              usuario de PostgreSQL
TU_PASSWORD          contraseña del usuario, si corresponde
localhost            computadora donde corre PostgreSQL
5432                 puerto estándar
afterlook            base de datos del proyecto
```

### Contraseñas con caracteres especiales

Si la contraseña contiene caracteres como `@`, `#`, `:`, `/` o `%`, debe codificarse para usarla dentro de una URL. Para un entorno local de aprendizaje, es más simple usar una contraseña sin esos caracteres.

> Nunca compartas ni subas `.env`. El archivo `.env.example` sí debe permanecer versionado.

---

## 7. Crear y activar el entorno virtual

Ubicate en la raíz del proyecto:

### Windows — PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Después activá nuevamente:

```powershell
.venv\Scripts\Activate.ps1
```

### macOS — Terminal

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Cuando está activo, la terminal suele mostrar `(.venv)` al comienzo de la línea.

---

## 8. Instalar dependencias

Con el entorno virtual activo:

### Windows y macOS

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En macOS, si el comando `python` no existe, usá:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

---

## 9. Estado de las migraciones Alembic

Antes de ejecutar migraciones, verificá que exista esta estructura:

```text
migrations/
├── env.py
├── script.py.mako
└── versions/
```

En el estado actual del proyecto, la carpeta `migrations/` todavía no contiene `env.py` ni una migración inicial. Por eso **todavía no ejecutes**:

```bash
alembic upgrade head
```

Si lo ejecutás antes de inicializar Alembic, vas a recibir un error similar a:

```text
ImportError: Can't find Python file .../migrations/env.py
```

Ese error significa que la base de datos está disponible, pero falta configurar el sistema de migraciones.

### Cuando Alembic esté inicializado

El flujo será:

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

La primera migración debe generarse después de definir los modelos SQLAlchemy y registrar el `target_metadata` en `migrations/env.py`.

Si aparece este error al ejecutar Alembic:

```text
ValueError: the greenlet library is required to use this function
```

instalá nuevamente las dependencias del proyecto, que incluyen `greenlet` para el uso async de SQLAlchemy:

```bash
python -m pip install -r requirements.txt
```

> No crees migraciones vacías para ocultar este error. Primero deben existir los modelos y la configuración de Alembic.

## 10. Iniciar la API

Desde la raíz del proyecto y con `.venv` activo:

### Windows y macOS

```bash
uvicorn app.main:app --reload
```

También podés usar:

```bash
make run
```

> `make` suele estar disponible en macOS. En Windows, usá directamente el comando `uvicorn` o ejecutá el proyecto desde Git Bash/WSL si tenés `make` instalado.

La API estará disponible en:

```text
http://127.0.0.1:8000
```

Documentación interactiva:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```

---

## 11. Lista de verificación

La configuración está correcta si podés confirmar:

```text
[ ] psql --version funciona
[ ] PostgreSQL está iniciado
[ ] pg_isready indica accepting connections
[ ] la base afterlook existe
[ ] SELECT current_database() devuelve afterlook
[ ] .env contiene DATABASE_URL con /afterlook
[ ] el entorno virtual está activo
[ ] las dependencias están instaladas
[ ] Alembic puede ejecutar las migraciones
[ ] la API inicia sin errores
```

---

## 12. Qué enviar si algo falla

No pruebes comandos al azar. Compartí:

```text
Sistema operativo:
Paso donde falló:
Comando ejecutado:
Resultado esperado:
Mensaje de error completo:
```

No incluyas contraseñas, tokens ni el contenido completo de `.env`.
