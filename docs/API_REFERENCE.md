# Database Accelerator - API Reference

## Base URL
```
http://localhost:8000/api
```

---

## Endpoints

### 1. Upload Dataset

**Endpoint:** `POST /upload/upload/`

**Description:** Upload a dataset file for processing

**Headers:**
```
Content-Type: multipart/form-data
```

**Request Body:**
```
file: (File) - CSV, XLSX, or JSON file
```

**Success Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "employees.csv",
  "file_type": "csv",
  "file_size": 2048,
  "file_size_mb": 0.00,
  "rows": 25,
  "columns": 5,
  "column_names": ["id", "name", "age", "salary", "department"],
  "column_types": {
    "id": "integer",
    "name": "string",
    "age": "integer",
    "salary": "float",
    "department": "string"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "status": "ready"
}
```

**Error Response (400):**
```json
{
  "error": "File type xlsx not supported. Allowed types: csv, xlsx, xls, json"
}
```

**Error Response (413):**
```json
{
  "error": "File size exceeds maximum allowed size of 100 MB"
}
```

---

### 2. Get Dataset Metadata

**Endpoint:** `GET /upload/{dataset_id}/metadata/`

**Description:** Retrieve metadata for an uploaded dataset

**URL Parameters:**
```
dataset_id (string) - UUID of the dataset
```

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "employees.csv",
  "file_type": "csv",
  "file_size": 2048,
  "file_size_mb": 0.00,
  "rows": 25,
  "columns": 5,
  "column_names": ["id", "name", "age", "salary", "department"],
  "column_types": {
    "id": "integer",
    "name": "string",
    "age": "integer",
    "salary": "float",
    "department": "string"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "status": "ready"
}
```

**Error Response (404):**
```json
{
  "detail": "Not found."
}
```

---

### 3. List All Datasets

**Endpoint:** `GET /upload/list_datasets/`

**Description:** Retrieve all uploaded datasets

**Success Response (200):**
```json
{
  "count": 2,
  "datasets": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "employees.csv",
      "file_type": "csv",
      "file_size": 2048,
      "file_size_mb": 0.00,
      "rows": 25,
      "columns": 5,
      "column_names": ["id", "name", "age", "salary", "department"],
      "column_types": {
        "id": "integer",
        "name": "string",
        "age": "integer",
        "salary": "float",
        "department": "string"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "status": "ready"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "filename": "products.json",
      "file_type": "json",
      "file_size": 1024,
      "file_size_mb": 0.00,
      "rows": 15,
      "columns": 4,
      "column_names": ["id", "name", "price", "stock"],
      "column_types": {
        "id": "integer",
        "name": "string",
        "price": "float",
        "stock": "integer"
      },
      "created_at": "2024-01-14T15:20:00Z",
      "status": "ready"
    }
  ]
}
```

---

## Supported File Types

### CSV
- **Extension:** .csv
- **Content-Type:** text/csv
- **Example:**
```csv
id,name,age,salary
1,John Doe,28,50000
2,Jane Smith,34,65000
```

### Excel
- **Extensions:** .xlsx, .xls
- **Content-Type:** application/vnd.ms-excel
- **Support:** Single sheet only (reads first sheet)

### JSON
- **Extension:** .json
- **Content-Type:** application/json
- **Format:** Array of objects
- **Example:**
```json
[
  {"id": 1, "name": "John Doe", "age": 28},
  {"id": 2, "name": "Jane Smith", "age": 34}
]
```

---

## Column Type Detection

The system automatically detects the following column types:

| Type | Description | Example |
|------|-------------|---------|
| integer | Whole numbers | 42, -17, 0 |
| float | Decimal numbers | 3.14, -2.5, 1.0 |
| string | Text data | "John", "hello world" |
| datetime | Date and time | 2024-01-15, 2024-01-15 10:30:00 |
| boolean | True/False values | True, False, 1, 0 |
| mixed | Multiple types detected | "123", 456, "abc" |

---

## Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | Bad Request | Invalid file type or format |
| 413 | Payload Too Large | File exceeds 100 MB limit |
| 404 | Not Found | Dataset ID doesn't exist |
| 500 | Server Error | Unexpected server error |

---

## Usage Examples

### cURL - Upload File
```bash
curl -X POST http://localhost:8000/api/upload/upload/ \
  -F "file=@employees.csv"
```

### cURL - Get Metadata
```bash
curl http://localhost:8000/api/upload/550e8400-e29b-41d4-a716-446655440000/metadata/
```

### cURL - List Datasets
```bash
curl http://localhost:8000/api/upload/list_datasets/
```

### JavaScript - Upload File
```javascript
const file = document.getElementById('fileInput').files[0];
const formData = new FormData();
formData.append('file', file);

fetch('http://localhost:8000/api/upload/upload/', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

### Python - Upload File
```python
import requests

with open('employees.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/upload/upload/', files=files)
    print(response.json())
```

---

## Response Structure

### Success Response
```json
{
  "id": "string (UUID)",
  "filename": "string",
  "file_type": "csv|xlsx|json",
  "file_size": "integer (bytes)",
  "file_size_mb": "float",
  "rows": "integer",
  "columns": "integer",
  "column_names": ["string"],
  "column_types": {"column_name": "type"},
  "created_at": "ISO 8601 timestamp",
  "status": "ready|processing|error"
}
```

### Error Response
```json
{
  "error": "string (error message)"
}
```

---

## Rate Limiting (Future)

Currently: No rate limiting
Future: 100 requests per minute per IP

---

## Pagination (Phase 2)

Future pagination support:
```
GET /api/upload/list_datasets/?page=1&page_size=20
```

---

**Last Updated:** 2024-01-15  
**API Version:** 1.0.0
