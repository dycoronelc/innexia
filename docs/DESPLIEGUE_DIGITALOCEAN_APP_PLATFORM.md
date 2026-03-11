# Paso a paso: desplegar InnovAI en DigitalOcean App Platform

Con el código ya en GitHub, sigue estos pasos para crear la app en App Platform (frontend + backend + base de datos).

---

## 1. Entrar a App Platform y crear la app

1. Entra en [DigitalOcean](https://cloud.digitalocean.com/) e inicia sesión.
2. En el menú lateral: **Apps** → **Create App**.
3. Elige **GitHub** como fuente y autoriza a DigitalOcean si te lo pide.
4. Selecciona el repositorio **innexia** (o el nombre de tu repo) y la rama **main**.
5. Haz clic en **Next**.

---

## 2. Configurar componentes

DigitalOcean detectará el repo. Como tienes **frontend (Vite/React)** y **backend (FastAPI)** en la misma raíz, hay que definir los componentes a mano.

### Opción recomendada: 3 componentes

- **Static Site** (frontend)
- **Service** (backend API)
- **Database** (MySQL)

---

### 2.1 Base de datos MySQL

1. En la vista de componentes, haz clic en **+ Add Resource** → **Database**.
2. Elige **MySQL** (versión 8).
3. Nombre sugerido: `innovai-db`.
4. Región: la misma que usarás para la app (ej. NYC, FRA).
5. Plan: el más económico para empezar (Basic).
6. **Add**.

Anota los datos de conexión que te muestra DigitalOcean (host, port, user, password, database). También puedes usar la variable de entorno que DO crea: `$db.DATABASE_URL` (nombre puede variar, ej. `innovai-db.DATABASE_URL`).

---

### 2.2 Backend (API)

1. **+ Add Resource** → **Service**.
2. **Nombre**: `api` o `backend`.
3. **Source**: mismo repo y rama (DigitalOcean ya lo tiene).
4. **Build**:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Run Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
   - **Output Directory**: deja vacío (no aplica para servicio).
5. **Root Directory**: `backend` (importante: así DO entra en la carpeta del backend).
6. **Environment Variables** (Add Variable):

   | Nombre           | Valor / Notas |
   |------------------|----------------|
   | `PORT`           | DigitalOcean suele inyectarlo; si no, `8000`. |
   | `DB_HOST`        | Host del MySQL (o usa la variable del DB, ej. `$innovai-db.HOSTNAME`) |
   | `DB_PORT`        | `25060` (típico en DO Managed DB) o el que te indique DO |
   | `DB_USER`        | Usuario del MySQL |
   | `DB_PASSWORD`    | Contraseña (usa **Encrypt** y el valor que te dio DO) |
   | `DB_NAME`        | Nombre de la base (ej. `defaultdb` o el que crees) |
   | `SECRET_KEY`     | Una clave larga y aleatoria para JWT (genera una y ponla aquí, cifrada) |
   | `OPENAI_API_KEY` | Tu clave de OpenAI (cifrada) |
   | `CORS_ORIGINS`   | URL del frontend en App Platform, ej. `https://tu-frontend-xxxx.ondigitalocean.app` (sin barra final). Si tienes dominio propio, añádelo separado por coma. |

   Si DigitalOcean te ofrece enlazar la base de datos al servicio, al hacerlo a veces crea variables tipo `DATABASE_URL`. Tu app usa `DB_*`; si solo tienes `DATABASE_URL`, tendrías que parsearla o duplicar en variables `DB_HOST`, `DB_USER`, etc.

7. **HTTP Port**: `8000` (o el que uses en `Run Command`).
8. **Instance Size**: Basic o el que prefieras.
9. Guarda el componente.

Cuando despliegues, DO te dará una URL para el backend (ej. `https://api-xxxx.ondigitalocean.app`). Esa es la URL de la API.

---

### 2.3 Frontend (Static Site)

1. **+ Add Resource** → **Static Site**.
2. **Nombre**: `frontend` o `web`.
3. **Source**: mismo repo y rama.
4. **Build**:
   - **Build Command**: `npm ci && npm run build`
   - **Output Directory**: `dist` (Vite genera la build en `dist`).
5. **Root Directory**: deja vacío (raíz del repo, donde está `package.json`).
6. **Environment Variables** (necesarias para que la app llame a tu API en producción):

   | Nombre               | Valor |
   |----------------------|--------|
   | `VITE_API_BASE_URL`  | URL del backend, ej. `https://api-xxxx.ondigitalocean.app` (sin barra final). |

   Sin esta variable, el frontend usará `http://localhost:8000` y no podrá hablar con la API en producción.

7. Guarda el componente.

Después del primer deploy, anota la URL del static site (ej. `https://frontend-xxxx.ondigitalocean.app`). Vuelve al **backend** y en `CORS_ORIGINS` añade exactamente esa URL (y la de dominio propio si la usas).

---

## 3. Orden y red

- El orden de despliegue no es crítico, pero la base de datos suele crearse primero.
- Backend y frontend se comunican por HTTP/HTTPS usando las URLs públicas; no hace falta configurar red interna salvo que uses funciones avanzadas.

---

## 4. Desplegar

1. Revisa que los tres componentes (DB, backend, frontend) estén bien configurados.
2. Haz clic en **Next** hasta llegar a **Review** (plan y coste).
3. Elige plan (Basic está bien para empezar).
4. **Create Resources** / **Deploy**.

El primer despliegue puede tardar varios minutos. Si algo falla, revisa los **logs** del componente (Build Logs y Run Logs).

---

## 5. Después del primer despliegue

1. **URL del frontend**: ábrela en el navegador; debería cargar la app y llamar a la API con `VITE_API_BASE_URL`.
2. **CORS**: si el navegador muestra errores de CORS, en el **backend** añade en `CORS_ORIGINS` la URL exacta del frontend (y `https://tu-dominio.com` si usas dominio propio), separadas por coma.
3. **Base de datos**: si las tablas no existen, ejecuta las migraciones o scripts SQL (por ejemplo los de `mysql/`) contra la base MySQL de DO (con un cliente o desde un job puntual si lo configuras).
4. **Dominio propio** (opcional): en cada componente (frontend y backend) puedes añadir un dominio personalizado en Settings.

---

## 6. Resumen de variables de entorno

### Backend (Service)

| Variable          | Ejemplo / Notas |
|-------------------|------------------|
| `PORT`            | `8000` (o el que inyecte DO) |
| `DB_HOST`         | Host del MySQL DO |
| `DB_PORT`         | Puerto del MySQL DO (ej. 25060) |
| `DB_USER`         | Usuario MySQL |
| `DB_PASSWORD`     | Contraseña (encrypt) |
| `DB_NAME`         | Nombre de la base |
| `SECRET_KEY`      | Clave para JWT (encrypt) |
| `OPENAI_API_KEY`  | Clave OpenAI (encrypt) |
| `CORS_ORIGINS`    | `https://frontend-xxxx.ondigitalocean.app` (y otros orígenes si aplica) |

### Frontend (Static Site)

| Variable            | Ejemplo |
|---------------------|---------|
| `VITE_API_BASE_URL` | `https://api-xxxx.ondigitalocean.app` |

---

## 7. Migraciones y datos iniciales

La base en DO empieza vacía. Para crear tablas y datos:

- Opción A: Conectarte por cliente MySQL (TablePlus, DBeaver, etc.) usando host, puerto, usuario y contraseña de DO, y ejecutar los scripts en `mysql/` (p. ej. `cambios_agente_ia.sql`, `agent_sections_tables.sql`, etc.).
- Opción B: Si usas Alembic, configurar `DATABASE_URL` o `DB_*` en local apuntando a la base de DO y ejecutar `alembic upgrade head` desde tu máquina (o desde un job en DO si lo configuras).

Con esto deberías tener la plataforma desplegada en DigitalOcean App Platform con frontend, backend y MySQL.
