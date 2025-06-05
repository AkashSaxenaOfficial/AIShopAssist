# AI Shop Assist (STATUS: WORK IN PROGRESS)

A modern AI-powered shopping assistant with real-time LLM integration.

## 🚀 Features

- Real-time AI chat with streaming responses
- Multiple LLM provider support (Claude, OpenAI, DeepSeek)
- Product listing and detail pages
- WebSocket-based communication
- Graceful offline mode with mock responses

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- pip or poetry

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AIShopAssist.git
cd AIShopAssist
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env_example.txt .env
# Edit .env with your API keys
```

### Required API Keys

Add at least one of these to your `.env` file:
- `ANTHROPIC_API_KEY` (Claude)
- `OPENAI_API_KEY` (GPT-4)
- `DEEPSEEK_API_KEY` (DeepSeek)

## 🏃‍♂️ Running the Application

Start both servers with a single command:
```bash
python start_servers.py
```

This will start:
- Main application on http://localhost:8080
- WebSocket server on ws://localhost:8081

## 🏗️ Architecture

### Core Components

1. **Main Application** (`main.py`)
   - FastAPI web server
   - Product listing and detail pages
   - WebSocket client integration

2. **WebSocket Server** (`websocket_server.py`)
   - Real-time communication
   - LLM provider management
   - Session handling

3. **AI Service** (`services/websocket_ai_service.py`)
   - LLM provider integration
   - Conversation management
   - Mock response generation

### Data Structure

- Product data stored in `data/` directory
- Environment variables in `.env`
- Configuration in `env_example.txt`

## 🔧 Development

### Project Structure
```
AIShopAssist/
├── data/               # Product data
├── services/          # Core services
├── main.py           # Main application
├── websocket_server.py # WebSocket server
├── start_servers.py   # Server startup script
├── requirements.txt   # Dependencies
└── env_example.txt   # Environment template
```

### Adding New Features

1. **New LLM Provider**
   - Add provider configuration in `services/websocket_ai_service.py`
   - Update environment variables
   - Test with mock responses

2. **New Product Features**
   - Update data structure in `data/`
   - Modify relevant services
   - Update UI components

## 🧪 Testing

Run tests with:
```bash
python -m pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

