# Crypto Tracker Bot - Docker Deployment

Production-ready Telegram bot for tracking cryptocurrency prices with AI analysis.

## 📋 Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Google Gemini API Key (from [Google AI Studio](https://makersuite.google.com/app/apikey))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd crypto-tracker-bot
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Add your tokens:
```env
API_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
TZ=UTC
```

### 3. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the bot
docker-compose up -d

# Check logs
docker-compose logs -f crypto-bot
```

## 🛠️ Makefile Commands

The project includes a Makefile for easier management:

```bash
# Show all available commands
make help

# Build the image
make build

# Start the bot
make up

# Stop the bot
make down

# View logs (follow mode)
make logs

# Restart the bot
make restart

# Open shell in container
make shell

# Check status
make status

# Clean everything
make clean

# Rebuild from scratch
make rebuild
```

## 📁 Project Structure

```
crypto-tracker-bot/
├── bot.py                 # Main bot application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Example environment file
├── .dockerignore         # Files to exclude from Docker image
├── Makefile              # Convenience commands
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_TOKEN` | Telegram Bot Token from BotFather | Yes |
| `GEMINI_API_KEY` | Google Gemini API Key | Yes |
| `TZ` | Timezone (default: UTC) | No |

### Resource Limits

The bot is configured with the following resource limits:

- **CPU Limit**: 1.0 cores
- **Memory Limit**: 1GB
- **CPU Reservation**: 0.5 cores
- **Memory Reservation**: 512MB

Adjust these in `docker-compose.yml` if needed.

## 📊 Monitoring

### View Logs

```bash
# Follow logs in real-time
docker-compose logs -f crypto-bot

# View last 100 lines
docker-compose logs --tail=100 crypto-bot

# Or use make
make logs
```

### Check Container Status

```bash
# View running containers
docker-compose ps

# Or use make
make status
```

### Health Check

The container includes a health check that runs every 30 seconds:

```bash
docker inspect crypto-tracker-bot | grep Health -A 10
```

## 🔄 Updates and Maintenance

### Update the Bot

```bash
# Pull latest code
git pull

# Rebuild and restart
make rebuild
```

### Backup Configuration

```bash
# Backup your .env file
cp .env .env.backup
```

### View Container Stats

```bash
docker stats crypto-tracker-bot
```

## 🐛 Troubleshooting

### Bot Not Starting

1. Check logs:
   ```bash
   make logs
   ```

2. Verify environment variables:
   ```bash
   docker-compose config
   ```

3. Check if ports are available:
   ```bash
   docker-compose ps
   ```

### High Memory Usage

- Adjust memory limits in `docker-compose.yml`
- Monitor with: `docker stats crypto-tracker-bot`

### Connection Issues

1. Verify internet connectivity inside container:
   ```bash
   docker-compose exec crypto-bot ping -c 3 api.telegram.org
   ```

2. Check firewall rules
3. Verify API tokens are correct

## 🔒 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use strong API tokens** and rotate them regularly
3. **Run as non-root user** (already configured in Dockerfile)
4. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   ```
5. **Monitor logs** for suspicious activity
6. **Use private Docker registries** for production images

## 🚀 Production Deployment

### Using a VPS/Cloud Server

1. **Install Docker and Docker Compose**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

2. **Clone and configure**:
   ```bash
   git clone <your-repo>
   cd crypto-tracker-bot
   cp .env.example .env
   nano .env
   ```

3. **Start with auto-restart**:
   ```bash
   docker-compose up -d
   ```

### Using Docker Swarm (for scaling)

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml crypto-bot

# Scale service
docker service scale crypto-bot_crypto-bot=3
```

### Using Kubernetes

Create a deployment and service (example provided upon request).

## 📝 Logging

Logs are configured with rotation:
- **Max size**: 10MB per file
- **Max files**: 3 files kept
- **Format**: JSON

Logs are stored in Docker's default location. To persist logs:

```yaml
# Add to docker-compose.yml volumes
volumes:
  - ./logs:/app/logs
```

## 🔗 Useful Commands

```bash
# View Docker images
docker images | grep crypto-bot

# Remove old images
docker image prune -a

# Export container logs
docker-compose logs crypto-bot > bot-logs.txt

# Inspect container
docker inspect crypto-tracker-bot

# Execute command in container
docker-compose exec crypto-bot python --version
```

## 📞 Support

For issues and questions:
1. Check the logs: `make logs`
2. Review this documentation
3. Check GitHub Issues
4. Contact the development team

## 📄 License

[Your License Here]

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Note**: Always test changes in a development environment before deploying to production.