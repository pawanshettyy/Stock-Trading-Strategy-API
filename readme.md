# Stock Trading Strategy API

A FastAPI application with PostgreSQL backend for analyzing stock data and implementing a simple Moving Average Crossover Strategy.

## Features

* PostgreSQL database with Prisma ORM
* FastAPI REST API
* Moving Average Crossover Strategy implementation
* Streamlit dashboard for visualization
* Docker containerization
* Unit tests with coverage reporting

## Project Structure

```
├── backend/                  # FastAPI application
│   ├── app/                  # API code
│   │   ├── database.py       # Database connection
│   │   ├── main.py           # FastAPI app initialization
│   │   ├── routes.py         # API routes
│   │   ├── schemas.py        # Pydantic models
│   │   └── strategy.py       # Trading strategy implementation
│   ├── prisma/               # Prisma ORM configuration
│   │   └── schema.prisma     # Database schema
│   ├── tests/                # Unit tests
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Streamlit dashboard
│   ├── app.py                # Dashboard UI
│   └── requirements.txt      # Frontend dependencies
├── Dockerfile                # API Docker configuration
├── docker-compose.yml        # Multi-container setup
├── HINDALCO_1D.xlsx          # Sample stock data
├── seed.js                   # Data seeding script
└── README.md                 # Project documentation
```

## Setup Instructions

### Prerequisites

* Python 3.9+
* Node.js 14+ (for Prisma)
* PostgreSQL 14+
* Docker and Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-trading-strategy
   ```
2. **Set up the database**
   ```bash
   # Create a PostgreSQL database
   createdb stock_data_read

   # Update the DATABASE_URL in backend/.env if needed
   ```
3. **Set up the backend**
   ```bash
   cd backend

   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Install Node.js dependencies for Prisma
   npm install -g prisma
   npm install @prisma/client

   # Generate Prisma client
   npx prisma generate

   # Apply database migrations
   npx prisma migrate dev

   # Test database connection
   python test_db.py
   ```
4. **Seed the database with sample data**
   ```bash
   # Navigate to project root
   cd ..

   # Install Node.js dependencies for the seed script
   npm install @prisma/client xlsx

   # Run the seed script
   node seed.js
   ```
5. **Run the FastAPI application**
   ```bash
   cd backend
   uvicorn app.main:app --reload

   # The API will be available at http://127.0.0.1:8000
   ```
6. **Set up the frontend**
   ```bash
   cd frontend
   pip install -r requirements.txt
   streamlit run app.py

   # The dashboard will be available at http://localhost:8501
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d

   # The API will be available at http://localhost:8000
   ```
2. **Seed the database in Docker**
   ```bash
   # Install Node.js dependencies locally
   npm install @prisma/client xlsx

   # Modify seed.js to use the Docker database URL:
   # DATABASE_URL=postgresql://postgres:8617@localhost:5432/stock_data_read

   # Run the seed script
   node seed.js
   ```
3. **Run the Streamlit dashboard**
   ```bash
   cd frontend
   pip install -r requirements.txt
   streamlit run app.py
   ```

## API Endpoints

* `GET /`: Home endpoint, returns a welcome message
* `GET /data`: Fetch all stock data records
* `POST /data`: Add new stock data records
* `GET /strategy/performance`: Get the performance of the moving average crossover strategy

## Trading Strategy

The application implements a Moving Average Crossover Strategy:

1. Calculate short-term and long-term moving averages
2. Generate buy signals when the short-term MA crosses above the long-term MA
3. Generate sell signals when the short-term MA crosses below the long-term MA
4. Calculate strategy performance metrics:
   * Total returns
   * Win rate
   * Trade count
   * Profit/loss statistics

## Testing

Run the unit tests and generate a coverage report:

```bash
cd backend
pytest --cov=app tests/
```

## Streamlit Dashboard

The frontend provides a visual interface for:

* Viewing stock data with OHLC charts
* Visualizing moving averages and trade signals
* Analyzing strategy performance metrics
* Exploring raw data with filtering options
