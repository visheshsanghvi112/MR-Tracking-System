# Security Policy

## 🔒 Supported Versions

We actively support the latest version of MR Bot. Security updates are provided for:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < 1.0   | :x:                |

## 🛡️ Security Features

### API Key Protection
- All sensitive credentials are stored in environment variables
- Google API keys and service account credentials are excluded from git
- Frontend API keys use `NEXT_PUBLIC_` prefix for client-side access only

### Data Security
- SQLite database is excluded from version control
- Session data is temporary and auto-expires
- Location data is processed securely

### File Security
The following files contain sensitive information and are protected:
- `pharmagiftapp-*.json` - Google service account credentials
- `.env` and `.env.local` - Environment variables
- `*.log` - Log files may contain sensitive data
- `active_sessions.json` - Session data

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. **DO NOT** open a public issue
2. Send an email to: [security@yourcompany.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and provide updates on the progress.

## 🔧 Security Best Practices

### For Developers
- Never commit API keys or credentials
- Use environment variables for all sensitive configuration
- Regularly rotate API keys and credentials
- Follow the `.gitignore` patterns strictly

### For Deployment
- Use HTTPS in production
- Set up proper firewall rules
- Monitor access logs regularly
- Keep dependencies updated

### For API Keys
- Restrict API key permissions to minimum required
- Set up API key usage monitoring
- Use separate keys for development and production
- Regularly audit API key access

## 🔐 Environment Variable Security

### Required Protection
These environment variables contain sensitive data:
- `MR_BOT_TOKEN` - Telegram bot token
- `GOOGLE_SHEETS_CREDENTIALS` - Path to service account JSON
- `GEMINI_API_KEY` - AI service API key
- `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` - Google Maps API key

### Setup Guidelines
1. Copy `.env.example` to `.env` 
2. Fill in actual values (never commit `.env`)
3. For frontend, copy `frontend/.env.example` to `frontend/.env.local`
4. Ensure all sensitive files are in `.gitignore`

## 📋 Security Checklist

Before deploying or contributing:

- [ ] No hardcoded API keys in code
- [ ] All sensitive files in `.gitignore`
- [ ] Environment variables properly configured
- [ ] Service account JSON files secured
- [ ] Database files excluded from git
- [ ] Log files excluded from git
- [ ] Dependencies are up to date
- [ ] HTTPS configured for production

## 🔄 Regular Security Tasks

### Monthly
- [ ] Rotate API keys
- [ ] Review access logs
- [ ] Update dependencies
- [ ] Audit user permissions

### Quarterly
- [ ] Security vulnerability scan
- [ ] Review and update this policy
- [ ] Backup and test restore procedures
- [ ] Review Google Cloud permissions

## 📞 Contact

For security-related questions or concerns:
- Email: security@yourcompany.com
- For urgent security issues: Use encrypted communication

---

**Note**: This security policy is reviewed quarterly and updated as needed.
