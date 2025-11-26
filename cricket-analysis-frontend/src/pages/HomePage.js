import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import '../styles/HomePage.css'; 

// ODI Images
const odiImages = [
  '/images/sri-lanka-odi-team.jpg',
  '/images/pathum.jpg',
  '/images/sadeera.jpg',
  '/images/wanindu.jpg'
];

// T20 Images (placeholder - will use generic T20 cricket images)
const t20Images = [
  '/images/sri-lanka-odi-team.jpg',
  '/images/pathum.jpg',
  '/images/sadeera.jpg',
  '/images/wanindu.jpg'
];

// Test Images (placeholder - will use generic Test cricket images)
const testImages = [
  '/images/sri-lanka-odi-team.jpg',
  '/images/pathum.jpg',
  '/images/sadeera.jpg',
  '/images/wanindu.jpg'
];

const imagesByMatchType = {
  ODI: odiImages,
  T20: t20Images,
  Test: testImages
};

function HomePage() {
  const [stats, setStats] = useState({
    ODI: null,
    T20: null,
    Test: null
  });
  const [loading, setLoading] = useState(true);
  const [activeMatchType, setActiveMatchType] = useState('ODI');

  // Homepage eke stats load kirima
  useEffect(() => { 
    // Backend eken dynamic stats gannawa
    axios.get('http://127.0.0.1:5000/api/homepage-stats')
      .then(response => {
        setStats(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching homepage stats:", error);
        setLoading(false);
      });
  }, []);

  return (
    <div className="homepage-main-container">
      {/* --- 1. Hero Section saha Image Slider --- */}
      <section className="hero-slider-container">
        <div className="slider">
          {imagesByMatchType[activeMatchType].map((image, index) => (
            <img key={index} src={image} alt={`${activeMatchType} Cricket`} />
          ))}
        </div>
        <div className="hero-content">
          <h1>Sri Lanka National Cricket Analysis Dashboard</h1>
          <p className="hero-subtitle">{activeMatchType} Format - Comprehensive Player Performance Analysis</p>
          <p>The ultimate platform for in-depth player analysis, performance tracking, and AI-powered team suggestions.</p>
        </div>
      </section>

      {/* --- 2. Dynamic Stats Dashboard --- */}
      <section className="stats-dashboard-container">
        <h2>Project at a Glance</h2>
        
        {/* Match Type Tabs */}
        <div className="match-type-tabs">
          {['ODI', 'T20', 'Test'].map(matchType => (
            <button
              key={matchType}
              className={`tab-button ${activeMatchType === matchType ? 'active' : ''}`}
              onClick={() => setActiveMatchType(matchType)}
            >
              {matchType}
            </button>
          ))}
        </div>

        {/* Stats Grid for Active Match Type */}
        <div className="stats-grid">
          <div className="stat-card">
            <h3>{loading ? '...' : stats[activeMatchType]?.totalRuns.toLocaleString()}</h3>
            <p>Total Runs Analyzed</p>
          </div>
          <div className="stat-card">
            <h3>{loading ? '...' : stats[activeMatchType]?.totalWickets.toLocaleString()}</h3>
            <p>Total Wickets Taken</p>
          </div>
          <div className="stat-card">
            <h3>{loading ? '...' : stats[activeMatchType]?.topScorer.name}</h3>
            <p>Top Scorer ({loading ? '...' : stats[activeMatchType]?.topScorer.stat})</p>
          </div>
          <div className="stat-card">
            <h3>{loading ? '...' : stats[activeMatchType]?.topBowler.name}</h3>
            <p>Top Bowler ({loading ? '...' : stats[activeMatchType]?.topBowler.stat})</p>
          </div>
        </div>
      </section>

      {/* --- 3. Feature Portals --- */}
      <section className="portals-container">
        <h2>Explore Features</h2>
        <div className="portals-grid">
          <Link to="/batting-performance" className="portal-card">
            <span className="portal-icon" role="img" aria-label="Bat">🏏</span>
            <h3>Batting Analysis</h3>
            <p>Analyze player batting statistics by ground and opposition.</p>
          </Link>
          <Link to="/bowling-performance" className="portal-card">
            <span className="portal-icon" role="img" aria-label="Ball">⚾</span>
            <h3>Bowling Analysis</h3>
            <p>Dive into detailed bowling metrics, economy rates, and averages.</p>
          </Link>
          <Link to="/best-11-suggestion" className="portal-card portal-ml">
            <span className="portal-icon" role="img" aria-label="Robot">🤖</span>
            <h3>Best XI Suggestion</h3>
            <p>Get AI-powered team recommendations based on match conditions.</p>
          </Link>
        </div>
      </section>

      {/* --- 4. Video Section --- */}
      <section className="video-section-container">
        <div className="video-content">
          <h2>See Our Project in Action</h2>
          <p>Watch a quick overview of how our platform works, from in-depth analysis to our powerful machine learning model that suggests the perfect team for any condition.</p>
          <Link to="/best-11-suggestion" className="portal-button">Try the ML Model</Link>
        </div>
        <div className="video-player">
          <iframe 
            src="https://www.youtube.com/embed/nC4-5I-8__A"
            title="Project Demo Video" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowFullScreen>
          </iframe>
        </div>
      </section>
    </div>
  );
}

export default HomePage;
