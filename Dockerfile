FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY config.yaml .

# Create output directory
RUN mkdir -p /app/output

# Default: run with interactive review
ENTRYPOINT ["python", "-m", "src.main"]
