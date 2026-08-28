# 🎨 Frontend - Player Dashboard

This is the graphical user interface of the application. It is an interactive web dashboard built with **Streamlit**, designed to consume the backend API.

## 🚀 Run the application

- [ ] Install all dependencies: `uv sync --project frontend --all-extras`

Then you have to be in the *frontend* folder to launch:

- [ ] `cd frontend`
- [ ] `uv run --project . streamlit run src/app.py`


## 🏛️ Architecture

The frontend follows a modular structure to separate UI components from API interaction:

- **Pages** (`pages/`) : Individual views and user interfaces (Home, Player List, Game Play, etc.)
- **API Client** (`utils/api_client.py`) : Centralized logic for communicating with the FastAPI backend
- **Security** (`utils/auth_guard.py`) : Manages session security and token validation
- **Utilities** (`utils/`) : Helpers for logging, initialization, and common UI tasks


## ⚒️ Debugging & Logs

### Logs

The frontend maintains its own logging system to track user interactions and API communication errors.

- Logs are written to the `frontend/logs/` directory.
- The logging format is configured via `logging_config.yml`.

### Code quality

The **format on save** with [Ruff](https://docs.astral.sh/ruff/) is enabled by default in the workspace (cf. *.vscode/settings.json*).
