# AI Document Search (RAG Chatbot)

A production-ready Retrieval-Augmented Generation (RAG) chatbot system that allows you to upload documents and ask questions about their content using natural language.

## ✨ Features

- 📄 **Document Upload**: Support for PDF, TXT, and Markdown files with validation
- 🔍 **Semantic Search**: Advanced vector-based document retrieval using Pinecone
- 💬 **Chat Interface**: Natural language question answering with citations
- 📚 **Namespace Support**: Organize documents by categories
- 🛡️ **Production Ready**: Rate limiting, input validation, logging, health checks
- 🚀 **Easy Setup**: Simple local development setup
- 🔒 **Secure**: CORS protection, file size limits, error handling

## 🏗️ Tech Stack

- **Frontend**: React with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python 3.11
- **AI**: OpenAI GPT models for chat completion
- **Vector DB**: Pinecone for semantic search
- **Embeddings**: OpenAI text-embedding models
- **Deployment**: Railway (Production) + Local Development

## 🚀 Quick Start

### **Railway Deployment (Production)**
1. **Connect to Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Configure Environment Variables**:
   - Go to your project → Variables
   - Add all required environment variables:
     ```
     OPENAI_API_KEY=your_openai_api_key
     PINECONE_API_KEY=your_pinecone_api_key
     PINECONE_ENV=your_pinecone_environment
     PINECONE_INDEX=documents
     ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
     ```

3. **Deploy**:
   - Railway will automatically detect Python and install dependencies
   - Your backend will be available at: `https://your-project.railway.app`

### **Local Development Setup**
```bash
# Clone the repository
git clone <your-repo>
cd rag-project

# Backend Setup
cd backend
pip install -r requirements.txt

# Create environment file
cp env.example .env
# Edit .env with your API keys

# Start backend server
python -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8000

# Frontend Setup (new terminal)
cd frontend
npm install
npm run dev
```

## 🔧 Environment Setup

### **Required Environment Variables**
Create `backend/.env` file with:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENV=your_pinecone_environment
PINECONE_INDEX=documents
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 📋 API Endpoints

- `POST /api/chat` - Chat with the AI
- `GET /api/health` - Health check
- `POST /api/upload` - Upload documents

## 🎯 **Project Features**

### **Core Functionality**
- ✅ **Full-Stack Application**: React Frontend + FastAPI Backend
- ✅ **AI Integration**: OpenAI GPT + Pinecone vector search
- ✅ **Modern Stack**: React, TypeScript, FastAPI, Python
- ✅ **Production Ready**: Error handling, validation, logging
- ✅ **Document Processing**: PDF, TXT, Markdown support

### **Technical Stack**
- **Frontend**: React, TypeScript, Tailwind CSS, Vite
- **Backend**: FastAPI, Python, REST APIs
- **AI/ML**: OpenAI API, Vector Embeddings, Semantic Search
- **Database**: Pinecone Vector Database
- **Deployment**: Railway (Production) + Local Development
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
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is this document about?",
    "namespace": "default",
    "top_k": 5
  }'
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Upload Document
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@document.pdf" \
  -F "namespace=default"
```

## 🚨 **Important Notes**

### **Local Development**
- Full file upload functionality available
- All production features enabled
- Easy setup with pip and npm
- Complete document processing pipeline

## 🔒 Security Features

- ✅ **Input Validation**: Message length, file type validation
- ✅ **CORS Protection**: Configurable allowed origins
- ✅ **Error Handling**: Comprehensive error responses
- ✅ **Rate Limiting**: Request throttling (local deployment)
- ✅ **Health Monitoring**: System status checks

## 📈 Performance

- ✅ **Fast API**: High-performance Python web framework
- ✅ **Optimized Builds**: Vite for fast frontend builds
- ✅ **Vector Search**: Efficient semantic search with Pinecone
- ✅ **Caching**: Efficient API responses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📞 Support

- **Local Development**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health
- **Issues**: [GitHub Issues](https://github.com/yourusername/rag-project/issues)

## 📝 License

This project is for educational and personal use.

---

**🎉 Project Complete!** This demonstrates full-stack development, AI integration, and modern development practices.