# Ker-Lann Neo-Watch 

### Start a service and import the project

- [ ] Launch a **VSCode-python** service (including Visual Studio Code, Python 3.13, Git)
  - Open ports 5000 and 8000 (Otherwise, you won't be able to access your application from the web)
- [ ] Clone the following repository : https://github.com/tristancabre/Projet-info-2A.git
- [ ] Launch the service

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

JWT_SECRET=
```

### Launch applications

Open two terminals:

- Backend FastApi: `uv run --project backend python backend/src/main.py`
- Frontend Streamlit: `cd frontend` and `uv run --project . streamlit run src/app.py`

:warning: **After launching, do not click on the link in the pop-up!**


### Accessing the application from the web

Since the application runs inside a cloud container, the services are not directly accessible via *localhost* from your local browser. You must use the public URLs provided by Onyxia.

To get the public URL for your services (Frontend or Backend):

- [ ] Go to your [Onyxia services](https://datalab.sspcloud.fr/my-services)
- [ ] Click on the **"Open"** button, you will see links to access the application
- Port 5000 corresponds to the swagger of the API
- **Backend API:** http://localhost:5000
- Port 8000 corresponds to the actual dashboard
- **Frontend UI:** http://localhost:8000

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
