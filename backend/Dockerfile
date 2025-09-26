FROM python:3.12-slim

# Install libpq runtime for psycopg
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.wsgi:app

EXPOSE 5000

# Use gunicorn for production
RUN pip install --no-cache-dir gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.wsgi:app"]
