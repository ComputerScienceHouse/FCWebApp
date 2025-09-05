FROM docker.io/python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY fcwebapp fcwebapp/
COPY config.env.py .
COPY requirements.txt .
RUN uv pip install -r requirements.txt --system
EXPOSE 8000
ENTRYPOINT ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "fcwebapp:app"]