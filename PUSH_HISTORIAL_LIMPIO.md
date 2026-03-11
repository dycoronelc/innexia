# Push con historial limpio (un solo commit sin secretos)

Tu repo local sigue teniendo todos los commits antiguos; al hacer push, GitHub escanea ese historial y detecta el secreto. Hay que crear una **rama nueva sin historial** y subir solo eso.

Ejecuta estos comandos **en la raíz del proyecto** (donde está la carpeta `.git`).

---

## 1. Crear una rama nueva sin historial

```bash
git checkout --orphan temp_main
```

Esto crea una rama `temp_main` que no tiene commits previos; los archivos del último commit quedan en "staging".

---

## 2. Añadir todo excepto lo que debe ignorarse

```bash
git add -A
git reset -- backend/.env
git reset -- .env
```

(El `.gitignore` ya evita que `.env` se trackee al hacer `git add -A`, pero por si acaso lo quitamos del índice.)

---

## 3. Verificar que backend/.env no está en el commit

```bash
git status
```

No debe aparecer `backend/.env` en la lista de "Changes to be committed". Si aparece, ejecuta otra vez:

```bash
git reset -- backend/.env
```

---

## 4. Primer (y único) commit en esta rama

```bash
git commit -m "Initial commit - InnovAI platform"
```

---

## 5. Sustituir main por esta rama

```bash
git branch -D main
git branch -m main
```

Ahora tu rama `main` local tiene un solo commit, sin historial anterior.

---

## 6. Push al repo de GitHub

```bash
git push -u origin main --force
```

Como el repo en GitHub es nuevo (o está vacío), el `--force` reemplaza su contenido con tu nueva `main`. GitHub solo recibe ese único commit, sin el que contenía el secreto.

---

## Si algo falla

- Si aún detecta secreto: asegúrate de que en "Changes to be committed" no esté `backend/.env` (paso 2 y 3).
- Si el remote no es el correcto: `git remote -v` y, si hace falta, `git remote set-url origin https://github.com/dycoronelc/innexia.git`.
