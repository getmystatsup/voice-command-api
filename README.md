# Voice Command API at 4Geeks Academy

<!-- hide -->

By [@4GeeksAcademy](https://github.com/4GeeksAcademy) and [other contributors](https://github.com/4GeeksAcademy/voice-command-api/graphs/contributors) at [4Geeks Academy](https://4geeksacademy.com/)

[![build by developers](https://img.shields.io/badge/build_by-Developers-blue)](https://4geeks.com)
[![4Geeks Academy](https://img.shields.io/twitter/follow/4geeksacademy?style=social&logo=x)](https://x.com/4geeksacademy)

_Estas instrucciones tambien estan disponibles en [espanol](./README.es.md)._

**Before you start**: Read the [how to start a coding project](https://4geeks.com/lesson/how-to-start-a-project) guide before writing code.

<!-- endhide -->

---

## Your challenge

This repository is the starter template for the **Voice Command API** project.

The frontend is already built. It records up to **20 seconds** of audio in the browser, sends that audio to your backend, and shows:

- the transcription returned by the API
- the final task response returned by the API

Your job is to implement the backend so the full voice-to-action flow works end to end.

---

## How the project works

The frontend uses a single public entry point:

- `POST /transcribe`

That endpoint must:

1. receive recorded audio from the frontend
2. transcribe it to text
3. reuse the same routing logic as `POST /instruction`
4. execute the corresponding task action in memory
5. return the transcription, the instruction payload, and the final result

Your backend must also expose:

- `POST /instruction` to turn a transcription into a JSON routing instruction
- `GET /tasks`
- `POST /tasks`
- `PUT /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

Important:

- Use **in-memory storage only**. No database, no files.
- The frontend is provided and should not be modified as part of the exercise.
- The backend included in this repository is only a template. You must implement the missing logic.

---

## Repository structure

```text
voice-command-api/
├── frontend/                # Ready-made frontend (do not rebuild it from scratch)
│   ├── public/
│   └── src/
├── src/
│   └── app/
│       ├── api/routes/      # /transcribe, /instruction, /tasks
│       ├── core/            # Settings/config
│       ├── schemas/         # Request/response contracts
│       ├── services/        # Your implementation goes here
│       └── utils/
├── Pipfile
└── README.md
```

---

## How to start

Fork or use this repository as a template, then clone it:

```bash
git clone https://github.com/4GeeksAcademy/voice-command-api
cd voice-command-api
```

Create your own repository and update the remote:

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY
```

### Backend setup

Create a `.env` file from `.env.example` and fill in your Groq credentials.

Install dependencies and run the API:

```bash
pipenv install
pipenv run uvicorn src.main:app --reload
```

### Frontend setup

Create `frontend/.env` from `frontend/.env.example`.

Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

---

## What you need to build

### 1. Task storage in memory

- Create a module-level `tasks` list
- Each task must include `id`, `title`, and `done`
- IDs must be unique and increment correctly

### 2. Task endpoints

- `GET /tasks` returns the full list
- `POST /tasks` creates a task
- `PUT /tasks/{task_id}` replaces a task
- `PATCH /tasks/{task_id}` partially updates a task
- `DELETE /tasks/{task_id}` removes a task

### 3. Instruction endpoint

Implement `POST /instruction` so it:

- receives `{ "transcription": "..." }`
- calls the Groq API
- returns only a JSON object with this shape:

```json
{
  "endpoint": "/tasks",
  "method": "POST",
  "params": { "title": "Buy groceries" }
}
```

Do not hardcode intent matching with manual `if "add" in text` rules.

### 4. Transcription endpoint

Implement `POST /transcribe` so it:

- accepts `multipart/form-data` with an audio file
- transcribes the audio
- calls the same instruction-routing logic used by `/instruction`
- executes the selected task action
- returns:

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

## What we will evaluate

- [ ] `POST /transcribe` receives audio and returns valid JSON
- [ ] `POST /instruction` returns a valid routing payload
- [ ] All five task endpoints are implemented correctly
- [ ] The task list is managed in memory
- [ ] CORS is configured correctly
- [ ] The frontend can talk to the backend without errors
- [ ] The returned transcription is visible in the app
- [ ] `.env` is ignored and secrets are not committed

---

## Debugging tip

If the transcription shown in the frontend is already wrong, the problem is in the audio capture or speech-to-text step.

If the transcription is correct but the action is wrong, the problem is in `/instruction`.

---

## Contributors

This project is maintained by [4Geeks Academy](https://4geeksacademy.com/) and [other contributors](https://github.com/4GeeksAcademy/voice-command-api/graphs/contributors). Find out more about our [AI Engineering](https://4geeksacademy.com/en/career-programs/ai-engineering), [Full-Stack Software Developer](https://4geeksacademy.com/en/career-programs/full-stack), [Data Science & Machine Learning](https://4geeksacademy.com/en/career-programs/data-science-ml), and [Cybersecurity](https://4geeksacademy.com/en/career-programs/cybersecurity) programs.
