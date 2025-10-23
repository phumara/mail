# Email Marketing System

A production-ready email marketing system built with Django 5, featuring comprehensive SMTP management, campaign automation, and analytics.

## ✨ Features

### 🔧 SMTP Management
- **Multi-provider support**: Gmail, Outlook, SendGrid, Mailgun, Amazon SES, Postmark, Custom SMTP
- **Automatic failover** and load balancing across providers
- **Real-time connection testing** and health monitoring
- **Rate limiting** and throttling controls
- **Comprehensive logging** of all email activities

### 📧 Campaign Management
- **Email template system** with variable support
- **Campaign scheduling** and automation
- **Subscriber segmentation** and targeting
- **Performance analytics** and delivery tracking
- **A/B testing** capabilities

### 🚀 Production Ready
- **Docker containerization** for easy deployment
- **PostgreSQL database** with optimized queries
- **Redis caching** and Celery task processing
- **Comprehensive logging** and monitoring
- **Security hardening** for production use

## 🛠️ Quick Start

### Option 1: Docker (Recommended)

1. **Start the infrastructure:**
   ```bash
   docker-compose up -d
   ```

2. **Run Django migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create admin user:**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Access the application:**
   - Admin interface: http://localhost:8000/admin/
   - SMTP Dashboard: http://localhost:8000/campaigns/smtp-dashboard/

### Option 2: Local Installation

#### Windows
```cmd
install.bat
```

#### Linux/macOS
```bash
chmod +x install.sh
./install.sh
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=mail_db
DB_USER=mail_user
DB_PASSWORD=your-secure-db-password
DB_HOST=localhost

# Email Provider (choose one)

# Gmail:
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# SendGrid:
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# Amazon SES:
EMAIL_BACKEND=django_ses.SESBackend
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
```

## 📧 SMTP Provider Setup

### 1. Gmail Setup
1. Enable 2-factor authentication
2. Generate an App Password
3. Use your email and app password in configuration

### 2. SendGrid Setup
1. Create account at sendgrid.com
2. Get API key from Settings > API Keys
3. Use API key in `EMAIL_HOST_PASSWORD`

### 3. Amazon SES Setup
1. Verify your domain/email in SES console
2. Move out of sandbox if needed
3. Use AWS credentials in configuration

## 🧪 Testing SMTP Connections

Test all configured providers:

```bash
# Test all providers
python manage.py test_smtp

# Test specific provider
python manage.py test_smtp --provider "Gmail"

# JSON output for automation
python manage.py test_smtp --json
```

## 📊 Usage

### Creating an SMTP Provider

1. Go to **Admin > Campaigns > SMTP providers**
2. Click **"Add SMTP Provider"**
3. Configure:
   - Provider name and type
   - SMTP settings (host, port, credentials)
   - Rate limits (daily, hourly, per-second)
   - From email and name

### Creating an Email Campaign

1. **Admin > Campaigns > Campaigns**
2. **"Add Campaign"**
3. Set:
   - Campaign name and subject
   - HTML content
   - Target subscriber lists
   - SMTP provider
   - Schedule (optional)

### Monitoring Performance

- **SMTP Dashboard**: Real-time provider status and delivery rates
- **Campaign Analytics**: Detailed performance metrics
- **Email Logs**: Complete delivery history with filtering

## 🔧 Development

### Project Structure

```
mail/
├── campaigns/              # Email campaign management
│   ├── models.py          # Database models
│   ├── smtp_service.py    # SMTP functionality
│   ├── tasks.py           # Celery tasks
│   └── management/        # Django commands
├── subscribers/           # Subscriber management
├── mail/                  # Django project settings
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Infrastructure stack
└── Dockerfile            # Application container
```

### Adding New Features

1. **Models**: Add to appropriate app's `models.py`
2. **Views**: Create in app's `views.py`
3. **Templates**: Add to app's `templates/` directory
4. **URLs**: Update app's `urls.py`

### Celery Tasks

Background tasks are automatically discovered. Add new tasks to app's `tasks.py`:

```python
from celery import shared_task

@shared_task
def my_background_task():
    # Task logic here
    pass
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure `SECRET_KEY`
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Set up email provider
- [ ] Configure domain and SSL
- [ ] Set up monitoring and logging
- [ ] Configure backups

### Docker Production

```bash
# Build production image
docker-compose -f docker-compose.yml build

# Run with production settings
docker-compose up -d
```

## 🔍 Monitoring

### Logs
- Application logs: `logs/mail_system.log`
- Celery logs: Check worker containers
- Web server logs: Nginx/Django logs

### Health Checks
- Database: PostgreSQL health endpoint
- Redis: Redis ping
- Application: `/health/` endpoint

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check existing documentation
2. Review configuration settings
3. Test SMTP connections
4. Check application logs

Common issues:
- **SMTP connection failed**: Check credentials and firewall
- **Rate limiting**: Adjust provider rate limits
- **Template errors**: Verify template syntax
- **Performance issues**: Check database and Redis status