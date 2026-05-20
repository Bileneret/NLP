
FROM python:3.12-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY src/ ./src/

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "src/interviewer/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
