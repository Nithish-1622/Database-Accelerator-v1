# Database Accelerator - Architecture

## System Design

### Overview
Database Accelerator is a modular system for intelligent dataset preparation. It follows a layered architecture:

```
┌─────────────────────────────────────────┐
│         Frontend (React/Vite)            │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      API Gateway (Django REST)           │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         Business Logic Layer             │
│  ┌─────────────────────────────────────┐│
│  │ • Upload Module                     ││
│  │ • Analysis Module (Phase 2)         ││
│  │ • Preprocessing Module (Phase 3)    ││
│  │ • Intelligence Module (Phase 4)     ││
│  │ • Report Module (Phase 5)           ││
│  │ • Export Module (Phase 5)           ││
│  └─────────────────────────────────────┘│
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      Data Access Layer (SQLite)          │
└──────────────────────────────────────────┘
```

---

## Module Responsibilities

### Upload Module ✅
- Handles file uploads (CSV, Excel, JSON)
- Parses files and extracts metadata
- Validates file integrity
- Stores metadata in database

### Analysis Module (Phase 2)
- Detects missing values
- Identifies duplicates
- Finds outliers
- Detects sparse rows
- Calculates quality scores

### Preprocessing Module (Phase 3)
- Imputes missing values
- Normalizes numerical data
- Encodes categorical data
- Cleans features
- Eliminates problematic rows

### Intelligence Module (Phase 4)
- Discovers column relationships
- Ranks feature importance
- Detects patterns
- Calculates mutual information

### Report Module (Phase 5)
- Generates health reports
- Creates cleaning logs
- Exports to PDF/JSON

### Export Module (Phase 5)
- Exports cleaned datasets
- Generates metadata
- Produces summary reports

---

## Data Flow

```
1. User uploads file
   ↓
2. Backend validates file
   ↓
3. Parse file (CSV/Excel/JSON)
   ↓
4. Extract metadata and column types
   ↓
5. Store in database
   ↓
6. Return dataset ID and metadata to frontend
   ↓
7. Frontend displays upload confirmation
   ↓
[Phase 2] Start analysis
```

---

## Database Schema

### Dataset Model
```sql
CREATE TABLE dataset (
    id UUID PRIMARY KEY,
    filename VARCHAR(255),
    file_path VARCHAR(500),
    file_type ENUM('csv', 'xlsx', 'json'),
    file_size BIGINT,
    rows INTEGER,
    columns INTEGER,
    column_names JSON,
    column_types JSON,
    status ENUM('uploaded', 'processing', 'ready', 'error'),
    error_message TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## API Contract

### POST /api/upload/upload/
Upload a dataset file

**Request:**
- Content-Type: multipart/form-data
- Body: file (binary)

**Response:**
```json
{
  "id": "uuid",
  "filename": "test.csv",
  "file_type": "csv",
  "file_size": 1024,
  "rows": 100,
  "columns": 5,
  "column_names": ["id", "name", "age", "salary", "department"],
  "column_types": {
    "id": "integer",
    "name": "string",
    "age": "integer",
    "salary": "float",
    "department": "string"
  },
  "status": "ready",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Technology Choices

### Why Django?
- Robust framework with built-in features
- Excellent ORM for database operations
- Great for structured APIs
- Large community and mature ecosystem

### Why React?
- Component-based architecture
- Large ecosystem and community
- Excellent for interactive UIs
- Virtual DOM for performance

### Why SQLite (Phase 1)?
- No external database needed
- Perfect for MVP
- Easy to migrate later
- File-based persistence

### Why Pandas?
- Industry-standard for data manipulation
- Excellent performance
- Great for CSV/Excel/JSON
- Large community

---

## Scalability Considerations

### Phase 1 (Current)
- Single-threaded processing
- Suitable for MVP development

### Phase 2+
Consider:
- Async task processing (Celery)
- Message queue (Redis)
- PostgreSQL for production
- Microservices architecture
- Caching layer

---

## Security Considerations

### Phase 1
- File size validation
- File type validation
- CORS configuration
- HTTPS ready (Django)

### Production (Future)
- User authentication
- API key management
- Role-based access control
- Input sanitization
- SQL injection prevention

---

## Performance Metrics (Phase 1)

### File Size Limits
- Max: 100 MB
- Min: 100 bytes

### Expected Performance
- CSV parsing: < 1 second (100K rows)
- Memory usage: Proportional to file size
- API response time: < 500ms

---

## Error Handling

### File Validation
- Invalid file type → HTTP 400
- File too large → HTTP 413
- Empty file → HTTP 400

### Processing Errors
- Parse error → Status: 'error' + message
- Type inference failure → Default to 'string'

---

## Future Enhancements

1. **Async Processing** - Background jobs for large files
2. **Real-time Collaboration** - WebSocket support
3. **Advanced Analytics** - ML-based anomaly detection
4. **Cloud Storage** - S3/Azure Blob support
5. **API Versioning** - Multiple API versions
6. **GraphQL** - Alternative to REST API

