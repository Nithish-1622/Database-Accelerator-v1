import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import Home from './pages/Home'
import UploadPage from './pages/UploadPage'
import DatasetPage from './pages/DatasetPage'
import BenchmarkPage from './pages/BenchmarkPage'
import ArtifactPage from './pages/ArtifactPage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/home" element={<Home />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/datasets" element={<DatasetPage />} />
          <Route path="/benchmark" element={<BenchmarkPage />} />
          <Route path="/artifacts" element={<ArtifactPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
