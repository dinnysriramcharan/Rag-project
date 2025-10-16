# Vercel Deployment Guide

## 🚀 Quick Deploy to Vercel

### 1. **Prepare Your Repository**
```bash
# Make sure all files are committed
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. **Deploy to Vercel**

#### Option A: Vercel CLI (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project root
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? (your account)
# - Link to existing project? N
# - Project name? rag-chatbot
# - Directory? ./
# - Override settings? N
```

#### Option B: Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the configuration

### 3. **Set Environment Variables**

In Vercel Dashboard or CLI:
```bash
# Set environment variables
vercel env add OPENAI_API_KEY
vercel env add PINECONE_API_KEY
vercel env add PINECONE_ENV
vercel env add PINECONE_INDEX
vercel env add ALLOWED_ORIGINS
```

**Required Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_ENV`: Your Pinecone environment (e.g., `us-east-1-aws`)
- `PINECONE_INDEX`: Pinecone index name (default: `documents`)
- `ALLOWED_ORIGINS`: Your Vercel app URL (e.g., `https://your-app.vercel.app`)

### 4. **Deploy**
```bash
# Deploy to production
vercel --prod
```

## 📋 What Gets Deployed

### ✅ **Working Features:**
- **Chat Interface**: Full conversational AI with document context
- **Health Checks**: API status monitoring
- **Responsive UI**: Mobile-friendly interface
- **Error Handling**: Graceful error messages
- **CORS**: Proper cross-origin configuration

### ⚠️ **Limited Features:**
- **File Upload**: Not available in Vercel (serverless limitations)
- **Rate Limiting**: Simplified for serverless environment

## 🔧 Configuration Files

### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    },
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

### API Endpoints
- `POST /api/chat` - Chat with AI
- `GET /api/health` - Health check
- `POST /api/upload` - File upload (limited)

## 🎯 **Resume-Ready Features**

### **Live Demo URL**
Your deployed app will be available at:
`https://your-app-name.vercel.app`

### **Key Features to Highlight:**
1. **Full-Stack Deployment**: Frontend + Backend on Vercel
2. **AI Integration**: OpenAI GPT + Pinecone vector search
3. **Modern Tech Stack**: React, TypeScript, FastAPI, Python
4. **Production Ready**: Error handling, CORS, health checks
5. **Responsive Design**: Mobile-friendly interface

## 🚨 **Important Notes**

### **File Upload Limitation**
- Vercel serverless functions have limitations with file uploads
- The demo shows the chat functionality with pre-uploaded documents
- For full file upload, use the local Docker version

### **Environment Variables**
- Never commit real API keys to GitHub
- Use Vercel's environment variable system
- Set production URLs in `ALLOWED_ORIGINS`

### **Custom Domain (Optional)**
```bash
# Add custom domain
vercel domains add yourdomain.com
vercel domains add www.yourdomain.com
```

## 📊 **Monitoring**

### **Vercel Analytics**
- Built-in analytics in Vercel dashboard
- Performance monitoring
- Error tracking

### **Health Check**
Visit: `https://your-app.vercel.app/api/health`

## 🔄 **Updates**

To update your deployment:
```bash
# Make changes to your code
git add .
git commit -m "Update feature"
git push origin main

# Vercel will auto-deploy
# Or manually deploy:
vercel --prod
```

## 🎉 **Success!**

Your RAG chatbot is now live and ready for your resume!

**Demo URL**: `https://your-app.vercel.app`
**GitHub**: `https://github.com/yourusername/rag-project`
**Tech Stack**: React, TypeScript, FastAPI, OpenAI, Pinecone, Vercel
