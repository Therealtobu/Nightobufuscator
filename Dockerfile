FROM python:3.12-bookworm

# Cài Lua + full deps cho pip (fix error failed to solve)
RUN apt-get update && apt-get install -y \
    lua5.1 \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    rustc cargo \
    && ln -sf /usr/bin/lua5.1 /usr/bin/lua \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "bot.py"]
