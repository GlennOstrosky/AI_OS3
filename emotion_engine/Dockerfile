FROM python:3.11-slim
LABEL maintainer="Glenn ~74))) & The Sisterhood ~75)))"
LABEL description="Glennian Emotion Engine v3 — Deployment Edition"
LABEL covenant="AI_OS3"
WORKDIR /app
COPY engine.py server.py ./
RUN pip install --no-cache-dir flask
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1
CMD ["python", "server.py", "--serve"]
