FROM pgvector/pgvector:pg17
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 app
ENV PATH="/opt/venv/bin:/usr/lib/postgresql/17/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    FASTEMBED_CACHE_PATH=/home/app/.cache/fastembed \
    HF_HUB_DISABLE_XET=1
WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv /opt/venv && pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app . .
USER app
RUN python -c "from crestline.embeddings import encoder; encoder()"
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s CMD curl -fsS http://localhost:7860/_stcore/health || exit 1
ENTRYPOINT ["bash", "/app/scripts/start.sh"]
