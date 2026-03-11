# Paso a paso: desplegar InnovAI en Railway

Con el código en GitHub, sigue estos pasos para tener la app en Railway (frontend + backend). La **base de datos MySQL** estará en tu servidor de **GoDaddy** (u otro hosting que ya tengas).

---

## Requisitos previos

- Cuenta en [Railway](https://railway.app/) (puedes usar GitHub para registrarte).
- Repositorio **innexia** (o el nombre de tu repo) en GitHub con la rama **main** actualizada.
- **MySQL en GoDaddy** (o en otro servidor) con:
  - Host, puerto, usuario, contraseña y nombre de la base de datos.
  - **Conexiones remotas permitidas** desde fuera del servidor (ver sección 2). En hosting compartido de GoDaddy a veces MySQL solo acepta conexiones desde `localhost`; en ese caso necesitarás un plan que permita acceso remoto (p. ej. VPS o MySQL remoto).

---

## 1. Crear el proyecto y conectar GitHub

1. Entra en [railway.app](https://railway.app/) e inicia sesión.
2. Haz clic en **New Project**.
3. Elige **Deploy from GitHub repo**.
4. Autoriza a Railway con GitHub si te lo pide y selecciona el repositorio **innexia**.
5. Railway creará un **servicio** por defecto a partir del repo. Lo usaremos como backend; luego añadiremos el frontend.

---

## 2. Base de datos MySQL en GoDaddy

La base de datos no se crea en Railway; usarás la que tienes en **GoDaddy** (o en otro servidor).

### 2.1 Obtener los datos de conexión

En el panel de **GoDaddy** (cPanel, Plesk o el que uses):

- Anota **host** (p. ej. `nombre.tu-dominio.com` o la IP del servidor; a veces en hosting compartido es `localhost` solo para conexiones desde el mismo servidor).
- **Puerto**: normalmente `3306`.
- **Usuario** y **contraseña** de MySQL.
- **Nombre de la base de datos** que vayas a usar para InnovAI.

Si GoDaddy te da un host tipo `localhost`, ese solo sirve para conexiones desde el mismo servidor. Para que Railway (en la nube) se conecte, necesitas un host accesible por internet (nombre de dominio del servidor o IP pública) y que el firewall/MySQL permita conexiones remotas.

### 2.2 Permitir conexiones remotas (importante)

Para que el backend en Railway pueda conectarse al MySQL de GoDaddy:

- En GoDaddy/cPanel suele haber una opción tipo **“Remote MySQL”** o **“MySQL remoto”**: añade ahí las IPs que permitan acceso. Railway no tiene IP fija; puedes:
  - **Opción A**: Si tu plan lo permite, autorizar temporalmente todo (`%` como host remoto) para probar (menos seguro).
  - **Opción B**: Revisar en la documentación de Railway si ofrecen IPs de salida o un proxy; si las dan, añade solo esas IPs en Remote MySQL de GoDaddy.

Si tu plan de GoDaddy **no permite MySQL remoto** (común en shared hosting), tendrás que usar otro proveedor para la base de datos (p. ej. Railway MySQL, PlanetScale, o un VPS con MySQL) o un plan GoDaddy que sí permita acceso remoto.

---

## 3. Configurar el servicio Backend (API)

1. En el proyecto, entra al **servicio** que se creó desde GitHub (el primero). Si Railway le puso otro nombre, renómbralo a **backend** o **api** (Settings → Name).
2. Abre **Settings** (o **Variables** y **Settings**).

### 3.1 Root Directory

- **Root Directory**: `backend`  
  Así Railway usa solo la carpeta del backend.

### 3.2 Build & Start

- **Build Command** (opcional si usas Nixpacks/Railway auto-detect):  
  `pip install -r requirements.txt`

- **Start Command**:  
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`  

  Railway inyecta `PORT`; no hace falta poner un número fijo.

- **Watch Paths** (opcional): `backend/**`  
  Para que solo los cambios en `backend` disparen un nuevo deploy.

### 3.3 Variables de entorno (backend)

En **Variables** del servicio backend, añade (usa **Add Variable** o **Raw Editor**):

| Variable          | Valor / Cómo obtenerla |
|-------------------|-------------------------|
| `DB_HOST`         | Host de tu MySQL en GoDaddy (nombre de dominio o IP del servidor, accesible por internet). |
| `DB_PORT`         | Puerto MySQL en GoDaddy (normalmente `3306`). |
| `DB_USER`         | Usuario de la base de datos en GoDaddy. |
| `DB_PASSWORD`     | Contraseña de ese usuario. |
| `DB_NAME`         | Nombre de la base de datos que usarás para InnovAI. |
| `SECRET_KEY`      | Una clave larga y aleatoria para JWT (genera una y pégala). |
| `OPENAI_API_KEY`  | Tu clave de OpenAI. |
| `PORT`            | Railway suele inyectarla; si no, pon `8000`. |
| `CORS_ORIGINS`    | Déjala vacía al principio; después del paso 5 pon aquí la URL del frontend (ej. `https://tu-frontend.up.railway.app`). Si tienes varias, sepáralas por coma. |

Todos los valores `DB_*` deben coincidir con los de tu MySQL en GoDaddy.

### 3.4 Dominio público (backend)

1. En el servicio backend, ve a **Settings** → **Networking** (o **Generate Domain**).
2. Haz clic en **Generate Domain**. Railway te dará una URL tipo `https://backend-xxxx.up.railway.app`.
3. **Cópiala**: la usarás como API en el frontend (`VITE_API_BASE_URL`) y en `CORS_ORIGINS`.

---

## 4. Añadir el servicio Frontend

1. En el mismo proyecto, **+ New** → **GitHub Repo** (o **Empty Service** si prefieres configurar todo a mano).
2. Si eliges **GitHub Repo**, selecciona **el mismo repositorio** (innexia) otra vez. Así tendrás dos servicios del mismo repo: uno con root `backend` y otro con root la raíz (frontend).
3. Entra al **nuevo** servicio y renómbralo a **frontend** o **web**.

### 4.1 Root Directory

- **Root Directory**: déjalo **vacío** (raíz del repo, donde está `package.json`).

### 4.2 Build & Start

- **Build Command**:  
  `npm ci && npm run build`

- **Start Command**:  
  `npx serve -s dist -l $PORT`  

  Esto sirve la carpeta `dist` que genera Vite. Railway asigna `PORT`. Si `npx serve` diera error, añade en tu repo la dependencia `serve` (`npm install serve`) y usa el mismo comando.

- Si Railway no detecta Node bien, en **Settings** puedes fijar **Nixpacks** o añadir un **Dockerfile**; para empezar, el comando anterior suele bastar.

### 4.3 Variables de entorno (frontend) — **MUY IMPORTANTE**

En **Variables** del servicio frontend **debes definir**:

| Variable             | Valor |
|----------------------|--------|
| `VITE_API_BASE_URL`  | URL pública del backend (ej. `https://backend-xxxx.up.railway.app`), **sin** barra final. |

**⚠️ Por qué el frontend llama a localhost:8000:**  
El build del frontend ejecuta `scripts/write-config.cjs`, que lee **`VITE_API_BASE_URL`** y escribe `public/config.js` con la URL de la API. Si esa variable **no está definida** en Railway cuando se hace el build, en Railway el build **fallará** con un mensaje claro; en local se usará `http://localhost:8000`. Si ya desplegaste antes de añadir la variable, el deploy actual sigue usando localhost hasta que **redespliegues**.

**Qué hacer si ya desplegaste y ves `POST http://localhost:8000/api/auth/login-company net::ERR_CONNECTION_REFUSED`:**

1. Entra al **servicio frontend** en Railway → **Variables**.
2. Añade **`VITE_API_BASE_URL`** con la URL pública del backend, por ejemplo:  
   `https://tu-backend.up.railway.app`  
   (sin barra final). Comprueba que el nombre sea exactamente `VITE_API_BASE_URL`.
3. **Redespliega el frontend**: pestaña **Deployments** → **Redeploy** en el último deploy (o haz **push** a la rama).  
   Tiene que ejecutarse un **nuevo build** para que el script vuelva a generar `config.js` con esa URL.
4. Después del deploy, haz **recarga forzada** en el navegador (Ctrl+Shift+R o Cmd+Shift+R) para no usar la caché antigua.

### 4.4 Dominio público (frontend)

1. En el servicio frontend, **Settings** → **Networking** → **Generate Domain**.
2. Si Railway pide **Target Port** (puerto de destino): tu app escucha en la variable **`$PORT`** que Railway inyecta (el comando `npx serve -s dist -l $PORT` usa ese puerto). Railway suele usar **3000** o **8080**. Elige **3000** en el desplegable (o **8080** si es la otra opción). Si ves una opción tipo **“Use PORT”** o que tome el puerto del entorno, selecciónala. Si no estás seguro, en **Variables** del mismo servicio revisa si existe `PORT` y usa ese número como Target Port.
3. Anota la URL que te genere Railway (ej. `https://frontend-xxxx.up.railway.app`).

### 4.5 CORS en el backend

1. Vuelve al servicio **backend** → **Variables**.
2. Edita `CORS_ORIGINS` y pon la URL del frontend (la que generaste en 4.4), por ejemplo:  
   `https://frontend-xxxx.up.railway.app`  
   Si tienes más orígenes, sepáralos por coma.
3. Guarda. Railway redesplegará el backend.

---

## 5. Crear las tablas en MySQL (GoDaddy)

La base de datos en GoDaddy debe tener las tablas de la aplicación. Ejecuta tus scripts SQL contra esa base:

- **Opción A**: Conectarte con un cliente (TablePlus, DBeaver, MySQL Workbench, phpMyAdmin de GoDaddy, etc.) usando **host, puerto, usuario y contraseña de tu MySQL en GoDaddy**, y ejecutar los `.sql` de tu repo (p. ej. los de la carpeta `mysql/`: `cambios_agente_ia.sql`, `agent_sections_tables.sql`, etc.).
- **Opción B**: Si usas Alembic, en local configura temporalmente `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` con los datos de GoDaddy y ejecuta `alembic upgrade head`.

---

## 6. Comprobar el despliegue

1. **Backend**: Abre en el navegador la URL del backend, por ejemplo `https://backend-xxxx.up.railway.app`. Deberías ver algo como `{"message":"Bienvenido a InnovAI API"}` o similar. Prueba también `https://backend-xxxx.up.railway.app/health`.
2. **Frontend**: Abre la URL del frontend. La app debería cargar y las llamadas a la API ir a la URL que configuraste en `VITE_API_BASE_URL`.
3. Si ves errores de CORS, revisa que `CORS_ORIGINS` en el backend contenga **exactamente** la URL del frontend (mismo protocolo, sin barra final).

---

## 7. Resumen de variables

### Backend

| Variable          | Dónde sale / Ejemplo |
|-------------------|----------------------|
| `DB_HOST`         | Host de tu MySQL en GoDaddy (dominio o IP del servidor). |
| `DB_PORT`         | Puerto MySQL en GoDaddy (ej. `3306`). |
| `DB_USER`         | Usuario MySQL en GoDaddy. |
| `DB_PASSWORD`     | Contraseña de ese usuario. |
| `DB_NAME`         | Nombre de la base de datos en GoDaddy. |
| `SECRET_KEY`      | Tú la generas (string largo aleatorio). |
| `OPENAI_API_KEY`  | Tu clave de OpenAI. |
| `CORS_ORIGINS`    | URL del frontend en Railway (ej. `https://frontend-xxxx.up.railway.app`). |

### Frontend

| Variable             | Ejemplo |
|----------------------|---------|
| `VITE_API_BASE_URL`  | `https://backend-xxxx.up.railway.app` |

---

## 8. Deploys automáticos

Cada vez que hagas **push a la rama conectada** (por defecto `main`), Railway volverá a desplegar los servicios que tengan ese repo. Asegúrate de que cada servicio tenga el **Root Directory** correcto (`backend` vs raíz) para que no se mezclen builds.

---

## 9. Si algo falla

- **Logs**: En cada servicio, pestaña **Deployments** → elige el último deploy → **View Logs** (build y runtime).
- **Build falla (backend)**: Revisa que Root Directory sea `backend` y que `requirements.txt` exista ahí.
- **Build falla (frontend)**: Revisa que en la raíz del repo esté `package.json` y que el build sea `npm run build` y la salida en `dist`.
- **Frontend llama a localhost:8000 / ERR_CONNECTION_REFUSED**: El frontend en producción está usando la URL por defecto. (1) En el **servicio frontend** de Railway → **Variables**, define **`VITE_API_BASE_URL`** = URL pública del backend (ej. `https://tu-backend.up.railway.app`, sin barra final). (2) **Redespliega** el frontend (Redeploy o push a la rama) para que se vuelva a hacer el build con esa variable. Si el build del frontend falla con *"ERROR: En Railway debes definir la variable VITE_API_BASE_URL"*, añade esa variable en el servicio frontend y vuelve a desplegar.
- **Error de base de datos / no se puede conectar**: (1) Comprueba que `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` sean los de tu MySQL en GoDaddy. (2) Verifica que en GoDaddy esté permitido el **acceso remoto** a MySQL (Remote MySQL) desde las IPs de Railway o desde cualquier host si tu plan lo permite. (3) Si el host es `localhost`, solo funcionará dentro del mismo servidor; para Railway necesitas un host accesible por internet (dominio o IP pública del servidor GoDaddy).
- **CORS / "No 'Access-Control-Allow-Origin' header"**: (1) En el **servicio backend** → Variables, `CORS_ORIGINS` debe ser **exactamente** la URL del frontend, por ejemplo `https://frontend-production-24735.up.railway.app` (con `https://`, **sin** comillas, **sin** barra final). (2) Si la cambiaste, **redespliega el backend**. (3) En los logs del backend al arrancar verás "CORS allow_origins: [...]" para comprobar qué se cargó.

Con estos pasos deberías tener InnovAI desplegada en Railway (frontend + backend) usando MySQL en GoDaddy.
