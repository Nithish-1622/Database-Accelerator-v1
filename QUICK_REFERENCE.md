# Database Accelerator - Quick Reference

## 🚀 Start Application (2 Terminals)

### Terminal 1: Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
**Backend:** http://localhost:8000

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```
**Frontend:** http://localhost:5173

---

## 📍 Key Directories

| Path | Purpose |
|------|---------|
| `backend/database_accelerator/` | Django project |
| `backend/database_accelerator/apps/upload_module/` | Upload functionality ✅ |
| `frontend/src/pages/` | React pages |
| `frontend/src/services/` | API services |
| `docs/` | Documentation |
| `samples/` | Test data files |

---

## 📚 Documentation Quick Links

| File | Purpose |
|------|---------|
| `PHASE_1_COMPLETE.md` | This phase summary |
| `docs/PHASE_1_SETUP.md` | Setup instructions |
| `docs/ARCHITECTURE.md` | System design |
| `docs/API_REFERENCE.md` | API documentation |
| `FILE_INVENTORY.md` | What was created |

---

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/upload/upload/` | Upload dataset |
| GET | `/api/upload/{id}/metadata/` | Get dataset info |
| GET | `/api/upload/list_datasets/` | List all datasets |

---

## 📦 Key Dependencies

### Backend
```
Django==4.2.11
djangorestframework==3.14.0
pandas==2.2.0
openpyxl==3.1.2
```

### Frontend
```
react@^18.2.0
react-router-dom@^6.20.0
axios@^1.6.5
tailwindcss@^3.4.1
```

---

## 🧪 Test Upload

```bash
# Terminal 3: Upload sample file
curl -X POST http://localhost:8000/api/upload/upload/ \
  -F "file=@samples/sample_employees.csv"
```

---

## 📝 Common Commands

### Backend
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Admin panel
http://localhost:8000/admin

# Run tests
python manage.py test
```

### Frontend
```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 🎯 Phase 1 Checklist

- [x] Backend setup
- [x] Frontend setup
- [x] Upload API
- [x] File parsing
- [x] UI components
- [x] Documentation
- [x] Sample data

## ✅ Ready for Phase 2

Once Phase 1 is working:
1. Implement analysis_module
2. Add analysis endpoints
3. Create analysis UI
4. Add visualization components

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS Error | Check CORS_ALLOWED_ORIGINS in settings.py |
| Port in use | Change port in config or kill process |
| Module not found | Run `pip install -r requirements.txt` |
| npm issues | Delete node_modules and run `npm install` |

---

## 📊 File Support

| Type | Extensions | Status |
|------|-----------|--------|
| CSV | .csv | ✅ |
| Excel | .xlsx, .xls | ✅ |
| JSON | .json | ✅ |

**Max Size:** 100 MB per file

---

## 🎨 UI Routes

| Route | Component | Status |
|-------|-----------|--------|
| `/` | Home | ✅ Complete |
| `/upload` | Upload | ✅ Complete |
| `/analysis` (TODO) | Analysis | Coming Phase 2 |
| `/results` (TODO) | Results | Coming Phase 2 |

---

## 🔐 Environment Setup

### Backend (.env)
```
DEBUG=True
SECRET_KEY=your-key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000/api
```

---

## 📈 Next Steps

1. **Verify Setup Works**
   - Start both servers
   - Upload test file
   - Check Recent Uploads

2. **Study Codebase**
   - Read ARCHITECTURE.md
   - Review models.py
   - Check API views

3. **Prepare Phase 2**
   - Read analysis requirements
   - Plan modules
   - Set up feature branches

---

## 🎓 Architecture Highlights

- **Modular Design:** Each module handles one responsibility
- **RESTful API:** Clean, documented endpoints
- **Responsive UI:** Works on desktop and mobile
- **Enterprise Code:** Production-ready quality
- **Comprehensive Docs:** Setup guides, API docs, architecture

---

**Phase:** 1 Complete ✅  
**Next:** Phase 2 (Analysis Engine)  
**Estimated Duration:** 2-3 weeks for Phase 2
