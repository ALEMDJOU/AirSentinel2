# --- Base Image ---
FROM python:3.12-slim

# --- Variables d'environnement ---
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# --- Installation des dépendances système ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- Répertoire de travail ---
WORKDIR /app

# --- Installation des dépendances Python ---
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Copie du code source et des ressources ---
# On copie sélectivement selon la structure attendue
COPY ./api ./api
COPY ./data/processed ./data/processed
COPY ./models ./models
# Optionnel: copies additionnelles si dossiers présents
# COPY ./pwa ./pwa

# --- Sécurité : Utilisateur non-root ---
RUN useradd -m apiuser && chown -R apiuser:apiuser /app
USER apiuser

# --- Exposition du port ---
EXPOSE 8000

# --- Healthcheck ---
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# --- Commande de démarrage ---
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
