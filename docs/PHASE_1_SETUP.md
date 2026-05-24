# Database Accelerator - Phase 1 Setup Guide

## 🎯 Quick Start

This guide will help you set up and run the Database Accelerator MVP locally.

---

## ✅ Phase 1 Deliverables

### Backend ✅
- Django REST API with dataset upload
- CSV, Excel, JSON file parsing
- Database schema for datasets
- File validation and metadata extraction

### Frontend ✅
- React application with Vite
- Home page with project overview
- Upload page with drag-and-drop
- Responsive design with Tailwind CSS

### API ✅
- POST `/api/upload/upload/` - Upload dataset
- GET `/api/upload/{id}/metadata/` - Get metadata
- GET `/api/upload/list_datasets/` - List datasets

---

## 🔧 Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Python Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Backend
```bash
python manage.py runserver
```

**Backend runs on:** `http://localhost:8000`

**No SQLite database is required.** Dataset files, metadata, reports, and exports are stored on the filesystem.

---

## 🎨 Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Node Dependencies
```bash
npm install
```

### 3. Run Development Server
```bash
npm run dev
```

**Frontend runs on:** `http://localhost:5173`

---

## 🚀 Using the Application

### Step 1: Open Frontend
Navigate to `http://localhost:5173`

### Step 2: Click "Upload Dataset"
- Drag and drop a CSV, XLSX, or JSON file
- Or click "Browse Files" to select

### Step 3: Review File Info
- File name
- File size
- Expected rows/columns

### Step 4: Upload
- Click the "Upload Dataset" button
- Wait for processing

### Step 5: Success
- See uploaded dataset in "Recent Uploads"
- View dataset metadata

---

## 📊 Example Test Files

Create test files to upload:

### Example CSV (test.csv)
```csv
name,age,salary,department
John Doe,28,50000,Engineering
Jane Smith,34,65000,Marketing
Bob Johnson,45,75000,Engineering
Alice Williams,29,55000,Sales
```

### Example JSON (test.json)
```json
[
  {"name": "John Doe", "age": 28, "salary": 50000, "department": "Engineering"},
  {"name": "Jane Smith", "age": 34, "salary": 65000, "department": "Marketing"},
  {"name": "Bob Johnson", "age": 45, "salary": 75000, "department": "Engineering"}
]
```

---

## 🔌 API Testing

### Upload Dataset (cURL)
```bash
curl -X POST http://localhost:8000/api/upload/upload/ \
  -F "file=@test.csv"
```

### Response Example
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "test.csv",
  "file_type": "csv",
  "file_size": 1024,
  "file_size_mb": 0.00,
  "rows": 4,
  "columns": 4,
  "column_names": ["name", "age", "salary", "department"],
  "column_types": {
    "name": "string",
    "age": "integer",
    "salary": "integer",
    "department": "string"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "status": "ready"
}
```

### Get Dataset Metadata
```bash
curl http://localhost:8000/api/upload/{dataset-id}/metadata/
```

### List All Datasets
```bash
curl http://localhost:8000/api/upload/list_datasets/
```

---

## 📁 Project Structure

```
database-accelerator/
│
├── frontend/                          # React application
│   ├── src/
│   │   ├── components/               # React components
│   │   ├── pages/                    # Page components
│   │   │   ├── Home.jsx             # Landing page
│   │   │   └── UploadPage.jsx       # Upload page
│   │   ├── services/                # API services
│   │   │   ├── api.js              # Axios client
│   │   │   └── uploadService.js    # Upload functions
│   │   ├── App.jsx                 # Root component
│   │   └── main.jsx                # Entry point
│   ├── package.json                # NPM dependencies
│   ├── vite.config.js              # Vite configuration
│   └── tailwind.config.js          # Tailwind CSS config
│
├── backend/                          # Django application
│   ├── database_accelerator/        # Django project
│   │   ├── apps/
│   │   │   ├── upload_module/       # ✅ IMPLEMENTED - File upload
│   │   │   ├── analysis_module/     # Phase 2 - Data analysis
│   │   │   ├── preprocessing_module/ # Phase 3 - Data cleaning
│   │   │   ├── intelligence_module/  # Phase 4 - Pattern discovery
│   │   │   ├── report_module/        # Phase 5 - Report generation
│   │   │   └── export_module/        # Phase 5 - Data export
│   │   ├── settings.py              # Django settings
│   │   ├── urls.py                  # URL routing
│   │   ├── wsgi.py                  # WSGI config
│   │   └── asgi.py                  # ASGI config
│   ├── manage.py                    # Django CLI
│   ├── requirements.txt             # Python dependencies
│   └── .env.example                 # Environment variables
│
├── docs/                             # Documentation
├── samples/                          # Sample datasets
├── exports/                          # Exported cleaned data
├── reports/                          # Generated reports
└── README.md                         # Project overview
```

---

## 🔑 Key Features (Phase 1)

### Upload Module ✅
- **File Upload:** POST endpoint for file uploads
- **File Parsing:** Parse CSV, XLSX, JSON files
- **Schema Detection:** Automatically detect column types
- **Metadata Extraction:** Extract dataset metadata
- **Validation:** Validate file size and format

### File Type Support
- CSV (Comma-Separated Values)
- XLSX/XLS (Excel files)
- JSON (Tabular format)

### Column Type Detection
- Integer
- Float
- String
- DateTime
- Boolean
- Mixed

---

## 🧪 Testing

### Test Backend
```bash
cd backend
python manage.py test
```

### Test Frontend
```bash
cd frontend
npm run test
```

---

## ⚙️ Configuration

### Backend Environment (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend Configuration (vite.config.js)
```javascript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

---

## 🚨 Troubleshooting

### Backend Issues

**CORS Error**
- Make sure backend is running on port 8000
- Check CORS_ALLOWED_ORIGINS in settings.py

**Database Error**
```bash
python manage.py migrate
```

**Module Not Found**
```bash
pip install -r requirements.txt
```

### Frontend Issues

**API Connection Error**
- Ensure backend is running on port 8000
- Check proxy settings in vite.config.js

**Module Not Found**
```bash
npm install
```

**Port Already in Use**
```bash
# Change port in vite.config.js or use different port
npm run dev -- --port 3000
```

---

## 📝 Next Steps (Phase 2)

After Phase 1 is working:

1. **Data Analysis Module**
   - Missing value detection
   - Duplicate detection
   - Outlier detection
   - Quality scoring

2. **Analysis UI**
   - Display analysis results
   - Show data quality metrics
   - Visualize distributions

3. **API Endpoints**
   - POST `/api/analyze/{id}` - Run analysis
   - GET `/api/report/{id}` - Get analysis report
  - POST `/api/preprocess/{id}` - Run preprocessing
  - POST `/api/export/{id}` - Export cleaned CSV

---

## 📚 File Sizes & Limits

- **Max upload:** 100 MB
- **Min file size:** 100 bytes
- **Supported formats:** CSV, XLSX, JSON

---

## 🎓 Development Best Practices

### Backend
- Use Django migrations for database changes
- Keep business logic in models/services
- Use serializers for API responses
- Follow DRY principle

### Frontend
- Use functional components with hooks
- Keep components small and reusable
- Use services for API calls
- Follow CSS modules pattern

---

## 📞 Support & Documentation

- See README.md for project overview
- Check API endpoints documentation
- Review module documentation in docs/

---

**Current Version:** 0.1.0  
**Phase:** 1 (Upload & Basic Infrastructure) ✅  
**Status:** Ready for Testing
