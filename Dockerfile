FROM python:3.9-slim

WORKDIR /app

# Copier les requirements et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Set the entrypoint to run the update_news.py and build_static.py scripts
CMD ["python", "run_update_and_build.py"]
