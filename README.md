# ENSAI-2A-projet-info-template

![CI](https://github.com/ludo2ne/ENSAI-2A-projet-info-template/actions/workflows/ci.yml/badge.svg)

Template for the ENSAI 2nd year IT project.

This very simple application includes a few elements that may help with the info 2A project:

- Creating a webservice with FastAPI
- Layer programming (DAO, service, view, business_object)
- Connection to a database
- Calling a Webservice
- Interface with Streamlit

## :arrow_forward: Quick launch with SSP Cloud

Needed: [SSP Cloud](https://datalab.sspcloud.fr/) account.

### Start a service and import the project

- [ ] Launch a **VSCode-python** service (including Visual Studio Code, Python 3.13, Git)
  - Open ports 5000 and 8000 (Otherwise, you won't be able to access your application from the web)
- [ ] Open a terminal
- [ ] Clone the repository
  - `git clone https://github.com/ludo2ne/ENSAI-2A-projet-info-template.git`
- [ ] Open Folder of the repository
  - `code-server ENSAI-2A-projet-info-template` or File > Open Folder
  - *ENSAI-2A-projet-info-template* should be the root directory of your Explorer
  - :warning: if not the application will not launch. Retry open folder

### Install required packages

Install and manage all dependencies with [uv](https://docs.astral.sh/uv/):

```bash
# curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --project backend
uv sync --project frontend
```

### Environment variables

Define environment variables to declare the database and webservice to which you are going to connect your python application.

- [ ] Launch a [PostreSQL](https://www.postgresql.org/) database
- [ ] Create a file called `.env` in the project's root directory
- [ ] Paste in and complete the elements below

```default
POSTGRES_HOST=postgresql-cnpg-<suffixe>
POSTGRES_PORT=5432
POSTGRES_DATABASE=defaultdb
POSTGRES_USER=user-<username>
POSTGRES_PASSWORD=<password>
POSTGRES_SCHEMA=project

UVICORN_HOST=0.0.0.0
UVICORN_PORT=5000

BACKEND_URL=http://localhost:5000
BACKEND_TIMEOUT=5

ELO_K_FACTOR=32
```

### Launch applications

Open two terminals:

- Backend FastApi: `uv run --project backend python backend/src/main.py`
- Frontend Streamlit: `cd frontend` and `uv run --project . streamlit run src/app.py`

:bulb: First Launch: Click on **Reset Database** to initialize it.

:warning: **After launching, do not click on the link in the pop-up!**


### Accessing the application from the web

Since the application runs inside a cloud container, the services are not directly accessible via *localhost* from your local browser. You must use the public URLs provided by Onyxia.

To get the public URL for your services (Frontend or Backend):

- [ ] Go to your [Onyxia services](https://datalab.sspcloud.fr/my-services)
- [ ] Click on the **"Open"** button, you will see links to access the api and/or the gui


### Endpoints

Documentation : `/docs` or `/redoc`

Examples of endpoints, assuming that the environment variable `$API_URL` (e.g. `export API_URL=http://localhost:5000`) contains the URL of the web service:

- `curl -L -X GET $API_URL/player | jq .`
- `curl -L -X GET $API_URL/player/3 | jq .`
- ```
  curl -L -X POST "$API_URL/player" \
    -H "Content-Type: application/json" \
    -d '{
      "username": "patapouf",
      "password": "123456789abcdefghijklmnopqrstuvwxyz",
      "elo": 1500,
      "email": "patapouf@mail.fr",
      "pokemon_fan": true
    }' | jq .
  ```
- ```
  curl -L -X PUT "$API_URL/player/3" \
    -H "Content-Type: application/json" \
    -d '{
      "username": "maurice_new",
      "password": "123456789abcdefghijklmnopqrstuvwxyz",
      "elo": 1400,
      "email": "maurice@ensai.fr",
      "pokemon_fan": true
    }' | jq .
  ```
- `curl -L -X DELETE "$API_URL/player/5" | jq .`


## :arrow_forward: Project structure

### Folders

| Item                       | Description                                                              |
| -------------------------- | ------------------------------------------------------------------------ |
| `data`                     | SQL script to create the tables and insert some data                     |
| `doc`                      | Report, tracking, UML diagrams, etc.                                     |
| `backend`                  | API code organized using a layered architecture                          |
| `frontend`                 | GUI code (graphical user interface)                                      |


### Files

| Item                       | Description                                                                          |
| -------------------------- | -------------------------------------------------------------------------------------|
| `README.md`                | Provides useful information to present, install, and use the application             |
| `LICENSE`                  | Specifies the usage rights and licensing terms for the repository                    |
| `.github/workflows/ci.yml` | Automated workflow that runs predefined tasks (like testing, linting, or deploying)  |
| `.vscode/settings.json`    | VSCode settings specific to this project                                             |
| `.gitignore`               | Lists files and folders that should not be tracked by Git                            |


## :arrow_forward: Continuous integration (CI)

The repository contains a `.github/workflow/main.yml` file.

When you *push* on GitHub, it triggers a pipeline that will perform the following steps:

- Creating a container from an Ubuntu (Linux) image
  - In other words, it creates a virtual machine with just a Linux kernel.
- Install Python
- Install the required packages
- Run the unit tests (only the service tests, as it's more complicated to run the dao tests)
- Analyse the code with *pylint*
  - If the score is less than 7.5, the step will fail

You can check how this pipeline is progressing on your repository's GitHub page, *Actions* tab.


## :arrow_forward: Quick launch with Docker

Prerequisites: [Docker Desktop](https://docs.docker.com/desktop/).

**Dockerfile**: A text document containing all the commands a user could call to assemble a specific image (the blueprint of your application and its environment).

**Docker Compose**: A tool for defining and running multi-container applications, using a YAML file to configure how different services (like your backend, frontend, and database) interact and start together.

- [ ] Build containers:  `docker compose up --build -d`
- [ ] See running processes: `docker compose ps`

To see logs:

- `docker compose logs -f` for all containers
- `docker compose logs -f backend` only for backend

**Backend API:** http://localhost:5000
**Frontend UI:** http://localhost:8000

- [ ]  `docker compose down` to remove conainers
  - `docker compose stop` to simply stop

[How it works](https://github.com/olevitt/kubernetes)