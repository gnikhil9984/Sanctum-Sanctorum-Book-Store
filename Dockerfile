FROM python:3.13.7-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY app ./app
COPY frontend ./frontend
COPY README.md SPEC.md ASSIGNMENT.md INSTRUCTIONS.md ./

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
