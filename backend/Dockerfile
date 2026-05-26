FROM python:3.11-slim

# System deps: Tesseract + Playwright Chromium dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-hin \
    tesseract-ocr-tam \
    tesseract-ocr-tel \
    tesseract-ocr-kan \
    tesseract-ocr-mal \
    tesseract-ocr-ben \
    tesseract-ocr-guj \
    tesseract-ocr-mar \
    # Chromium deps
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpango-1.0-0 \
    libcairo2 libx11-6 libx11-xcb1 \
    fonts-liberation wget curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright + Chromium browser
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

RUN mkdir -p static/demo

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]