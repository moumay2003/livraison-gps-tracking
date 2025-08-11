# 🚚 Livraison GPS - Real-Time Delivery Tracking System

A modern, real-time GPS tracking system for delivery drivers built with Django, MongoDB, Redis, and WebSockets. This application provides live tracking capabilities with an intuitive web interface for monitoring delivery personnel.

![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![Django](https://img.shields.io/badge/django-v5.2+-green.svg)
![MongoDB](https://img.shields.io/badge/mongodb-latest-green.svg)
![Redis](https://img.shields.io/badge/redis-latest-red.svg)
![WebSocket](https://img.shields.io/badge/websockets-enabled-orange.svg)

## 🌟 Features

### Core Functionality
- **Real-time GPS tracking** of delivery drivers
- **Live position updates** via WebSockets
- **Interactive map interface** with Leaflet.js
- **Driver management** (CRUD operations)
- **Position history** and route visualization
- **Zone-based tracking** for different areas of Paris

### Technical Features
- **MongoDB integration** for scalable data storage
- **Redis-powered** real-time messaging
- **RESTful API** for mobile app integration
- **WebSocket support** for instant updates
- **Responsive design** for desktop and mobile
- **GPS simulation** for testing and development

## 🏗️ Architecture

```
livraison_gps/
├── tracking/           # Core tracking functionality
│   ├── models.py       # MongoDB data models
│   ├── views.py        # REST API endpoints
│   ├── consumers.py    # WebSocket consumers
│   ├── mongodb.py      # Database connection
│   └── serializers.py  # GPS simulation script
├── frontend/           # Web interface
│   └── templates/      # HTML templates
├── livraison_gps/      # Django project settings
└── test.py            # Advanced testing simulator
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- MongoDB
- Redis
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/moumay2003/livraison-gps-tracking.git
cd livraison-gps-tracking
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install django djangorestframework channels channels-redis pymongo djongo corsheaders
```

4. **Start MongoDB and Redis**
```bash
# Start MongoDB (default port 27017)
mongod

# Start Redis (default port 6379)
redis-server
```

5. **Run Django development server**
```bash
python manage.py runserver
```

6. **Access the application**
- Web Interface: `http://localhost:8000/frontend/`
- API Documentation: `http://localhost:8000/api/`

## 📱 API Endpoints

### Drivers Management
```http
GET    /api/livreurs/                    # List all drivers
POST   /api/livreurs/                    # Create new driver
GET    /api/livreurs/{id}/               # Get driver details
PUT    /api/livreurs/{id}/               # Update driver
DELETE /api/livreurs/{id}/               # Delete driver
```

### Position Tracking
```http
GET    /api/positions/?latest=true       # Get latest positions
POST   /api/positions/                   # Create new position
GET    /api/livreurs/{id}/positions/     # Get driver's position history
```

### WebSocket Connection
```javascript
ws://localhost:8000/ws/tracking/
```

## 🧪 Testing & Simulation

### GPS Simulation
Run the built-in GPS simulator to test the system:

```bash
python test.py --interval 10 --debug
```

**Simulator Features:**
- Simulates 5 delivery drivers across Paris zones
- Realistic GPS movements with zone boundaries
- Configurable update intervals
- Movement logging and statistics
- Visual movement tracking in console

**Command Line Options:**
```bash
python test.py --help
  --url URL          API base URL (default: http://localhost:8000/api)
  --interval FLOAT   Update interval in seconds (default: 10)
  --debug           Enable debug mode with detailed logs
```

## 🗺️ Coverage Areas

The system covers 5 zones in Paris:
- **Nord Paris** - Northern districts
- **Sud Paris** - Southern districts  
- **Est Paris** - Eastern districts
- **Ouest Paris** - Western districts
- **Centre Paris** - Central districts

Each zone has realistic GPS boundaries and movement patterns.

## 🔧 Configuration

### MongoDB Settings
```python
# tracking/mongodb.py
client = MongoClient('mongodb://localhost:27017/')
db = client['livreurs_gps_db']
```

### Redis Configuration
```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

## 🌐 Web Interface Features

### Dashboard
- **Real-time map** with driver positions
- **Driver list** with search functionality
- **Position details** with coordinates and timestamps
- **Route history** visualization

### Interactive Elements
- Click drivers to view details
- Toggle between individual and all drivers view
- Show/hide historical routes
- Real-time position updates without page refresh

## 📊 Data Models

### Driver (Livreur)
```json
{
  "livreur_id": "LIV001",
  "nom": "Jean Dupont", 
  "telephone": "0612345678",
  "actif": true,
  "created_at": "2025-01-01T10:00:00Z"
}
```

### Position
```json
{
  "position_id": "uuid-here",
  "livreur_id": "LIV001",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "timestamp": "2025-01-01T10:00:00Z"
}
```

## 🔌 WebSocket Events

### Position Updates
```javascript
{
  "livreur_id": "LIV001",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "timestamp": "2025-01-01T10:00:00Z"
}
```

## 🛠️ Development

### Project Structure
- **tracking/** - Core GPS tracking logic
- **frontend/** - Web interface components  
- **livraison_gps/** - Django project configuration
- **test.py** - Advanced testing and simulation tools

### Key Technologies
- **Backend**: Django 5.2, Django REST Framework
- **Database**: MongoDB with PyMongo
- **Real-time**: Redis + Django Channels
- **Frontend**: Leaflet.js, HTML5, CSS3, JavaScript
- **Testing**: Custom GPS simulation framework

## 🚀 Deployment

### Production Considerations
1. Configure MongoDB with authentication
2. Set up Redis with password protection
3. Use environment variables for sensitive settings
4. Enable HTTPS for secure WebSocket connections
5. Configure reverse proxy (Nginx recommended)

### Environment Variables
```bash
export MONGODB_URI="mongodb://username:password@host:port/database"
export REDIS_URL="redis://username:password@host:port"
export DJANGO_SECRET_KEY="your-secret-key"
export DJANGO_DEBUG="False"
```

## 📈 Performance

- **Real-time updates**: Sub-second position updates
- **Concurrent users**: Supports multiple simultaneous tracking
- **Data storage**: Efficient MongoDB indexing for fast queries
- **Memory usage**: Optimized Redis channel management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Mouad (moumay2003)** - *Initial work*

## 🙏 Acknowledgments

- Leaflet.js for the interactive mapping
- Django community for the excellent framework
- MongoDB for scalable document storage
- Redis for real-time messaging capabilities

---

⭐ **Star this repository if you find it useful!**