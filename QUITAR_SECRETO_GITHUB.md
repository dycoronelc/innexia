# Quitar el secreto del historial para poder hacer push a GitHub

GitHub bloqueó el push porque en el commit `5b3e34ff` está el archivo `backend/.env` con una clave (OpenAI API Key). Ese archivo **no debe estar en el repositorio**.

Ya se añadieron `.env` y `backend/.env` al `.gitignore`. Falta **sacar el archivo del historial** y volver a intentar el push.

---

## Opción A: El commit con el secreto es el último (o son pocos commits)

Si `5b3e34ff` es tu último commit (o los que tienen el .env son los últimos), puedes hacer:

```bash
# 1. Dejar de trackear backend/.env (el archivo sigue en tu disco, solo deja de estar en Git)
git rm --cached backend/.env

# 2. Añadir el .gitignore actualizado
git add .gitignore

# 3. Hacer un commit que quite .env y añada .gitignore
git commit -m "chore: remove .env from repo, add to .gitignore"
```

Si con eso **el .env ya no está en ningún commit que vayas a subir** (porque nunca llegaste a hacer push), intenta de nuevo:

```bash
git push origin main
```

Si GitHub **sigue diciendo que el secreto está en el commit 5b3e34ff**, ese commit sigue en la rama y hay que reescribir historial (Opción B).

---

## Opción B: Reescribir historial para quitar backend/.env del commit 5b3e34ff

Tienes que **modificar ese commit** para que no contenga `backend/.env`.

### B1. Ver en qué posición está el commit

```bash
git log --oneline
```

Busca el commit `5b3e34ff`. Si está, por ejemplo, 3 commits por debajo del HEAD, anota ese número.

### B2. Rebase interactivo para editar ese commit

```bash
# Sustituye N por cuántos commits hay POR ENCIMA de 5b3e34ff (si 5b3e34ff es el 3º desde arriba, N=4)
git rebase -i 5b3e34ff^
```

En el editor que se abre, localiza la línea del commit `5b3e34ff` y cambia `pick` por **`edit`**. Guarda y cierra.

### B3. En ese commit: quitar backend/.env y seguir

```bash
git rm --cached backend/.env
git add .gitignore
git commit --amend --no-edit
git rebase --continue
```

Si hay más commits que toquen `.env`, el rebase puede parar en cada uno; repite `git rm --cached backend/.env` y `git commit --amend --no-edit` y luego `git rebase --continue` hasta que termine.

### B4. Push (reescritura de historial)

```bash
git push origin main --force-with-lease
```

`--force-with-lease` es más seguro que `--force`: solo hace force si nadie ha subido otros cambios a `main`.

---

## Después del push

- Las **claves y variables sensibles** (OpenAI, DB, JWT, etc.) deben ir solo en **variables de entorno** en DigitalOcean App Platform, no en el repo.
- En el repo puedes dejar un **`backend/env.example`** (sin valores reales) para documentar qué variables necesita el backend. Ese archivo sí puede estar en Git y está excluido del secret scanning porque no lleva secretos.

Si quieres, en el siguiente paso podemos definir juntos el contenido de `backend/env.example` y qué variables configurar en DigitalOcean.
