FROM python:3.12

# Cài Lua 5.1 + symlink
RUN apt-get update && apt-get install -y lua5.1 \
    && ln -sf /usr/bin/lua5.1 /usr/bin/lua \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "bot.py"]
