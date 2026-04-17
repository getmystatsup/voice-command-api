# Voice Command API en 4Geeks Academy

<!-- hide -->

Por [@4GeeksAcademy](https://github.com/4GeeksAcademy) y [otros contribuidores](https://github.com/4GeeksAcademy/voice-command-api/graphs/contributors) en [4Geeks Academy](https://4geeksacademy.com/)

[![build by developers](https://img.shields.io/badge/build_by-Developers-blue)](https://4geeks.com)
[![4Geeks Academy](https://img.shields.io/twitter/follow/4geeksacademy?style=social&logo=x)](https://x.com/4geeksacademy)

_These instructions are also available in [English](./README.md)._

**Antes de empezar**: Lee la guia de [como comenzar un proyecto de programacion](https://4geeks.com/lesson/how-to-start-a-project) antes de escribir codigo.

<!-- endhide -->

---

## Tu reto

Este repositorio es el template inicial del proyecto **Voice Command API**.

El frontend ya esta construido. Graba hasta **20 segundos** de audio en el navegador, envia ese audio a tu backend y muestra:

- la transcripcion devuelta por la API
- la respuesta final de tareas devuelta por la API

Tu trabajo es implementar el backend para que todo el flujo de voz a accion funcione de punta a punta.

---

## Como funciona el proyecto

El frontend usa un unico punto de entrada publico:

- `POST /transcribe`

Ese endpoint debe:

1. recibir el audio grabado desde el frontend
2. transcribirlo a texto
3. reutilizar la misma logica de routing que `POST /instruction`
4. ejecutar la accion correspondiente sobre las tareas en memoria
5. devolver la transcripcion, la instruccion y el resultado final

Tu backend tambien debe exponer:

- `POST /instruction` para convertir una transcripcion en un JSON de routing
- `GET /tasks`
- `POST /tasks`
- `PUT /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

Importante:

- Usa **solo almacenamiento en memoria**. No base de datos, no archivos.
- El frontend ya viene dado y no deberias modificarlo como parte del ejercicio.
- El backend incluido en este repositorio es solo un template. Tu debes completar la logica faltante.

---

## Estructura del repositorio

```text
voice-command-api/
├── frontend/                # Frontend ya listo
│   ├── public/
│   └── src/
├── src/
│   └── app/
│       ├── api/routes/      # /transcribe, /instruction, /tasks
│       ├── core/            # Configuracion
│       ├── schemas/         # Contratos de requests/responses
│       ├── services/        # Aqui va tu implementacion
│       └── utils/
├── Pipfile
└── README.es.md
```

---

## Como empezar

Haz fork o usa este repositorio como template y luego clonaló:

```bash
git clone https://github.com/4GeeksAcademy/voice-command-api
cd voice-command-api
```

Crea tu propio repositorio y actualiza el remoto:

```bash
git remote set-url origin https://github.com/TU_USUARIO/TU_REPOSITORIO
```

### Configuracion del backend

Crea un archivo `.env` a partir de `.env.example` y agrega tus credenciales de Groq.

Instala dependencias y ejecuta la API:

```bash
pipenv install
pipenv run uvicorn src.main:app --reload
```

### Configuracion del frontend

Crea `frontend/.env` a partir de `frontend/.env.example`.

Ejecuta el frontend:

```bash
cd frontend
npm install
npm run dev
```

---

## Que necesitas construir

### 1. Almacenamiento de tareas en memoria

- Crea una lista `tasks` a nivel de modulo
- Cada tarea debe incluir `id`, `title` y `done`
- Los IDs deben ser unicos e incrementales

### 2. Endpoints de tareas

- `GET /tasks` devuelve la lista completa
- `POST /tasks` crea una tarea
- `PUT /tasks/{task_id}` reemplaza una tarea
- `PATCH /tasks/{task_id}` actualiza una tarea parcialmente
- `DELETE /tasks/{task_id}` elimina una tarea

### 3. Endpoint de instrucciones

Implementa `POST /instruction` para que:

- reciba `{ "transcription": "..." }`
- llame a la API de Groq
- devuelva solo un JSON con esta forma:

```json
{
  "endpoint": "/tasks",
  "method": "POST",
  "params": { "title": "Buy groceries" }
}
```

No hardcodees el routing con reglas manuales como `if "add" in text`.

### 4. Endpoint de transcripcion

Implementa `POST /transcribe` para que:

- acepte `multipart/form-data` con un archivo de audio
- transcriba el audio
- llame a la misma logica de routing usada por `/instruction`
- ejecute la accion elegida
- devuelva:

```json
{
  "transcription": "add buy groceries to my list",
  "instruction": {
    "endpoint": "/tasks",
    "method": "POST",
    "params": {
      "title": "Buy groceries"
    }
  },
  "result": {
    "id": 1,
    "title": "Buy groceries",
    "done": false
  }
}
```

---

## Que vamos a evaluar

- [ ] `POST /transcribe` recibe audio y devuelve JSON valido
- [ ] `POST /instruction` devuelve un payload de routing valido
- [ ] Los cinco endpoints de tareas estan bien implementados
- [ ] La lista de tareas se maneja en memoria
- [ ] CORS esta configurado correctamente
- [ ] El frontend puede comunicarse con el backend sin errores
- [ ] La transcripcion devuelta se muestra en la app
- [ ] `.env` esta ignorado y los secretos no se suben al repositorio

---

## Tip para depurar

Si la transcripcion que se ve en el frontend ya esta mal, el problema esta en la captura de audio o en el speech-to-text.

Si la transcripcion esta bien pero la accion sale mal, el problema esta en `/instruction`.

---

## Contributors

Este proyecto es mantenido por [4Geeks Academy](https://4geeksacademy.com/) y [otros contribuidores](https://github.com/4GeeksAcademy/voice-command-api/graphs/contributors). Puedes conocer mas sobre nuestros programas de [AI Engineering](https://4geeksacademy.com/en/career-programs/ai-engineering), [Full-Stack Software Developer](https://4geeksacademy.com/en/career-programs/full-stack), [Data Science & Machine Learning](https://4geeksacademy.com/en/career-programs/data-science-ml) y [Cybersecurity](https://4geeksacademy.com/en/career-programs/cybersecurity).
