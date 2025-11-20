import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Components and Pages
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
// අලුත් Batting page එකත් මෙතනට import කරගමු (හදන්න කලින්)
import BattingPerformancePage from './pages/BattingPerformancePage'; 
import BowlingPerformancePage from './pages/BowlingPerformancePage';
import BestXISelectionPage from './pages/BestXISelectionPage';
import ManageDatasetPage from './pages/ManageDatasetPage';
import './App.css'; 

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/batting-performance" element={<BattingPerformancePage />} />
            <Route path="/bowling-performance" element={<BowlingPerformancePage />} />
            <Route path="/best-11-suggestion" element={<BestXISelectionPage />} />
            <Route path="/manage-dataset" element={<ManageDatasetPage />} />
            {/* Players, Matches වගේ අනිත් පිටු වලටත් මෙතන routes දාන්න පුළුවන් */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;