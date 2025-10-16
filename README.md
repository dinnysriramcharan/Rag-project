# AI Document Search (RAG Chatbot)

A production-ready Retrieval-Augmented Generation (RAG) chatbot system that allows you to upload documents and ask questions about their content using natural language.

## 🚀 **Live Demo**

**[Try the Live Demo on Vercel](https://your-app.vercel.app)** 🌐

*Deployed with Vercel for instant access - no setup required!*

## ✨ Features

- 📄 **Document Upload**: Support for PDF, TXT, and Markdown files with validation
- 🔍 **Semantic Search**: Advanced vector-based document retrieval using Pinecone
- 💬 **Chat Interface**: Natural language question answering with citations
- 📚 **Namespace Support**: Organize documents by categories
- 🛡️ **Production Ready**: Rate limiting, input validation, logging, health checks
- 🌐 **Vercel Deployed**: Live demo accessible worldwide
- 🔒 **Secure**: CORS protection, file size limits, error handling

## 🏗️ Tech Stack

- **Frontend**: React with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python 3.11
- **AI**: OpenAI GPT models for chat completion
- **Vector DB**: Pinecone for semantic search
- **Embeddings**: OpenAI text-embedding models
- **Deployment**: Vercel (Frontend + Serverless Functions)

## 🚀 Quick Start

### **Option 1: Try the Live Demo (Recommended)**
1. Visit: **[https://your-app.vercel.app](https://your-app.vercel.app)**
2. Start chatting with pre-uploaded documents
3. Try asking: "What is this system about?" or "Tell me about the technical stack"

### **Option 2: Local Development**
```bash
# Clone the repository
git clone <your-repo>
cd rag-project

# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## 🌐 Vercel Deployment

### **One-Click Deploy**
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/rag-project)

### **Manual Deploy**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables
vercel env add OPENAI_API_KEY
vercel env add PINECONE_API_KEY
vercel env add PINECONE_ENV
vercel env add PINECONE_INDEX
```

**See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed instructions.**

## 📋 API Endpoints

- `POST /api/chat` - Chat with the AI
- `GET /api/health` - Health check
- `POST /api/upload` - Upload documents (local only)

## 🎯 **Resume Highlights**

### **Live Project**
- ✅ **Deployed Application**: [Live Demo](https://your-app.vercel.app)
- ✅ **Source Code**: [GitHub Repository](https://github.com/yourusername/rag-project)
- ✅ **Full-Stack**: Frontend + Backend deployment
- ✅ **AI Integration**: OpenAI GPT + Pinecone vector search
- ✅ **Modern Stack**: React, TypeScript, FastAPI, Python

### **Technical Skills Demonstrated**
- **Frontend**: React, TypeScript, Tailwind CSS, Vite
- **Backend**: FastAPI, Python, Serverless Functions
- **AI/ML**: OpenAI API, Vector Embeddings, Semantic Search
- **Database**: Pinecone Vector Database
- **Deployment**: Vercel, CI/CD
- **DevOps**: Environment management, Health checks, Monitoring

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | ✅ |
| `PINECONE_API_KEY` | Pinecone API key | ✅ |
| `PINECONE_ENV` | Pinecone environment | ✅ |
| `PINECONE_INDEX` | Pinecone index name | ❌ |
| `ALLOWED_ORIGINS` | CORS allowed origins | ❌ |

## 📊 Usage Examples

### Chat with Documents
```bash
curl -X POST "https://your-app.vercel.app/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is this document about?",
    "namespace": "default",
    "top_k": 5
  }'
```

### Health Check
```bash
curl https://your-app.vercel.app/api/health
```

## 🚨 **Important Notes**

### **Vercel Limitations**
- **File Upload**: Not available in Vercel deployment (serverless limitations)
- **Demo Mode**: Chat functionality works with pre-uploaded documents
- **Full Features**: Use local development for complete functionality

### **Local Development**
- Full file upload functionality available
- All production features enabled
- Easy setup with pip and npm

## 🔒 Security Features

- ✅ **Input Validation**: Message length, file type validation
- ✅ **CORS Protection**: Configurable allowed origins
- ✅ **Error Handling**: Comprehensive error responses
- ✅ **Rate Limiting**: Request throttling (local deployment)
- ✅ **Health Monitoring**: System status checks

## 📈 Performance

- ✅ **Serverless**: Auto-scaling with Vercel
- ✅ **CDN**: Global content delivery
- ✅ **Optimized Builds**: Vite for fast frontend builds
- ✅ **Caching**: Efficient API responses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📞 Support

- **Live Demo**: [https://your-app.vercel.app](https://your-app.vercel.app)
- **Health Check**: [https://your-app.vercel.app/api/health](https://your-app.vercel.app/api/health)
- **Issues**: [GitHub Issues](https://github.com/yourusername/rag-project/issues)

## 📝 License

This project is for educational and personal use.

---

**🎉 Ready for your resume!** This project demonstrates full-stack development, AI integration, and modern deployment practices.