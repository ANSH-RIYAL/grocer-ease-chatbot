# GrocerEase Chatbot Deployment Guide

This guide covers deploying the GrocerEase Chatbot to various cloud platforms.

## 🚀 Quick Deploy Options

### 1. Railway (Recommended)

Railway is the easiest option for this application with excellent MongoDB integration.

#### Prerequisites
- Railway account (free tier available)
- MongoDB Atlas connection string
- Gemini API key
- Structured Prompting API key

#### Deployment Steps

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Deploy using the script**
   ```bash
   # Set your environment variables
   export MONGO_URI="your_mongodb_connection_string"
   export GEMINI_API_KEY="your_gemini_api_key"
   export STRUCTURED_PROMPTING_API_KEY="your_structured_prompting_api_key"
   
   # Run deployment script
   ./scripts/deploy.sh
   ```

4. **Manual Deployment**
   ```bash
   # Initialize project
   railway init
   
   # Set environment variables
   railway variables set MONGO_URI="your_mongodb_connection_string"
   railway variables set DB_NAME="chatbot_db"
   railway variables set GEMINI_API_KEY="your_gemini_api_key"
   railway variables set GEMINI_MODEL_NAME="gemini-1.5-pro"
   railway variables set CLASSIFIER_TYPE="bart"
   railway variables set PREFERENCE_MODEL_TYPE="bart"
   railway variables set STRUCTURED_PROMPTING_API_KEY="your_structured_prompting_api_key"
   
   # Deploy
   railway up
   ```

### 2. Render

Render offers a generous free tier and easy deployment.

#### Deployment Steps

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Configure the service:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3.11

4. **Set Environment Variables:**
   ```
   MONGO_URI=your_mongodb_connection_string
   DB_NAME=chatbot_db
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL_NAME=gemini-1.5-pro
   CLASSIFIER_TYPE=bart
   PREFERENCE_MODEL_TYPE=bart
   STRUCTURED_PROMPTING_API_KEY=your_structured_prompting_api_key
   ```

### 3. Heroku

Heroku is a classic choice with good Python support.

#### Prerequisites
- Heroku CLI installed
- Heroku account

#### Deployment Steps

1. **Install Heroku CLI**
   ```bash
   # Ubuntu/Debian
   sudo snap install heroku --classic
   
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables**
   ```bash
   heroku config:set MONGO_URI="your_mongodb_connection_string"
   heroku config:set DB_NAME="chatbot_db"
   heroku config:set GEMINI_API_KEY="your_gemini_api_key"
   heroku config:set GEMINI_MODEL_NAME="gemini-1.5-pro"
   heroku config:set CLASSIFIER_TYPE="bart"
   heroku config:set PREFERENCE_MODEL_TYPE="bart"
   heroku config:set STRUCTURED_PROMPTING_API_KEY="your_structured_prompting_api_key"
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

### 4. DigitalOcean App Platform

DigitalOcean offers good performance and reasonable pricing.

#### Deployment Steps

1. **Connect your GitHub repository**
2. **Create a new App**
3. **Configure the app:**
   - **Source:** Your GitHub repository
   - **Branch:** main
   - **Build Command:** `pip install -r requirements.txt`
   - **Run Command:** `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables** (same as Render)

## 🔧 Environment Variables

All deployments require these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `DB_NAME` | Database name | `chatbot_db` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `GEMINI_MODEL_NAME` | Gemini model to use | `gemini-1.5-pro` |
| `CLASSIFIER_TYPE` | Message classifier type | `bart` |
| `PREFERENCE_MODEL_TYPE` | Preference model type | `bart` |
| `STRUCTURED_PROMPTING_API_KEY` | Structured Prompting API key | `sk-...` |

## 🧪 Pre-Deployment Testing

Before deploying, run the test suite:

```bash
# Run all tests
./scripts/run_tests.sh

# Or run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
```

## 📊 Monitoring and Health Checks

### Health Check Endpoint
All deployments include a health check endpoint:
```
GET /health
```

### Expected Response
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### Monitoring Setup

#### Railway
- Built-in monitoring dashboard
- Automatic health checks
- Log streaming

#### Render
- Built-in monitoring
- Custom health check URL
- Log access via dashboard

#### Heroku
```bash
# View logs
heroku logs --tail

# Monitor dyno status
heroku ps
```

#### DigitalOcean
- Built-in monitoring dashboard
- Custom health check configuration
- Log access via console

## 🔄 Continuous Deployment

### GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        uses: railway/deploy@v1
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: ${{ secrets.RAILWAY_SERVICE }}
```

### Environment Setup for CI/CD

1. **Railway Token:** Get from Railway dashboard
2. **Service Name:** Your Railway service name
3. **Secrets:** Add to GitHub repository secrets

## 🚨 Troubleshooting

### Common Issues

1. **Port Configuration**
   - Ensure your app uses `$PORT` environment variable
   - Railway/Render/Heroku set this automatically

2. **Database Connection**
   - Verify MongoDB URI is correct
   - Check network access from deployment platform
   - Ensure database exists

3. **API Keys**
   - Verify all API keys are valid
   - Check API quotas and limits
   - Ensure keys have correct permissions

4. **Dependencies**
   - All dependencies are in `requirements.txt`
   - Check for platform-specific issues

### Debug Commands

```bash
# Check application logs
railway logs
heroku logs --tail
render logs

# Test locally with production settings
MONGO_URI="your_uri" GEMINI_API_KEY="your_key" uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Run health check
curl https://your-app-url.railway.app/health
```

## 📈 Performance Optimization

### Production Settings

1. **Worker Processes**
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port $PORT --workers 4
   ```

2. **Database Connection Pooling**
   - Configure MongoDB connection pooling
   - Monitor connection usage

3. **Caching**
   - Implement Redis for session storage
   - Cache frequently accessed data

4. **Rate Limiting**
   - Implement API rate limiting
   - Monitor usage patterns

## 🔒 Security Considerations

1. **Environment Variables**
   - Never commit API keys to version control
   - Use platform-specific secret management

2. **CORS Configuration**
   - Configure CORS for your frontend domain
   - Restrict unnecessary origins

3. **Input Validation**
   - All endpoints validate input
   - Sanitize user data

4. **Database Security**
   - Use MongoDB Atlas security features
   - Enable network access restrictions

## 📞 Support

For deployment issues:
1. Check platform-specific documentation
2. Review application logs
3. Test locally with production settings
4. Open an issue in the GitHub repository

## 🎯 Next Steps

After successful deployment:
1. Set up monitoring and alerting
2. Configure custom domain (optional)
3. Set up SSL certificates
4. Implement CI/CD pipeline
5. Add performance monitoring 