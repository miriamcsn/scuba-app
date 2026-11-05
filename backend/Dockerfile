# Etapa base: dependências e código do app
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/

# Etapa de testes: se algum teste falhar, o build para aqui e nenhuma imagem é gerada.
# Os testes usam SQLite, então não precisam de MySQL durante o build.
FROM base AS tests
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests/ ./tests/
RUN python -m pytest -q tests && touch /tmp/tests-ok

# Imagem final: só o necessário para rodar, sem pytest e sem os testes.
FROM base AS final
# Copiar o marcador obriga o build a passar pela etapa de testes.
COPY --from=tests /tmp/tests-ok /tmp/tests-ok
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
# UID numérico: permite ao Kubernetes confirmar o runAsNonRoot.
USER 1000
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
