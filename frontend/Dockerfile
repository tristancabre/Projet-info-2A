FROM python:3.13

RUN pip install uv

WORKDIR /app

COPY frontend/pyproject.toml frontend/uv.lock ./frontend/

RUN uv sync --project frontend --no-install-project

COPY frontend/ ./frontend/

RUN mkdir -p /app/frontend/logs

EXPOSE 8000

WORKDIR /app/frontend
CMD ["uv", "run", "--project", ".", "streamlit", "run", "src/app.py"]