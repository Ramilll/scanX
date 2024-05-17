# ScanX

## Usage

1. Create a `.env` file
```bash
RABBITMQ_USER=
RABBITMQ_PASS=
RABBITMQ_HOST=
RABBITMQ_PORT=
BOT_TOKEN=
POSTGRES_USER=
POSTGRES_HOST=
POSTGRES_PASSWORD=
POSTGRES_DB=
```

2. Build the docker image
```bash
docker build -t scanx-worker .
```

3. Run the docker compose
```bash
docker-compose up -d
```

## Web Interfaces

- Flower: http://localhost:5555
- RabbitMQ: http://localhost:15672
- Telegram Bot

## Telegram Bot

- `/start`: Start the bot
- `/top`: Top 10 addresses
- `/subscribe`: Subscribe the address
- `/unsubscribe`: Unsubscribe the address
- `/my_subscriptions`: List all subscriptions
