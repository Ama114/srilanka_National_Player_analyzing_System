import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import '../styles/HomePage.css'; 

// Image slider eka sadaha images - using public folder
const slide1 = '/images/sri-lanka-odi-team.jpg';
const slide2 = '/images/pathum.jpg';
const slide3 = '/images/sadeera.jpg';
const slide4 = '/images/wanindu.jpg';

function HomePage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

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
  }, []); // Me effect eka page eka load weddi ekaparayi run wenne

  return (
    <div className="homepage-main-container">
      {/* --- 1. Hero Section saha Image Slider --- */}
      <section className="hero-slider-container">
        <div className="slider">
          {/* Apey slider images */}
          <img src={slide1} alt="Cricket Stadium" />
          <img src={slide2} alt="Sri Lankan Team" />
          <img src={slide3} alt="Cricket Action" />
          <img src={slide4} alt="Fans Celebrating" />
        </div>
        <div className="hero-content">
          <h1>Sri Lanka National Cricket Analysis Dashboard</h1>
          <p>The ultimate platform for in-depth player analysis, performance tracking, and AI-powered team suggestions.</p>
          {/* Search bar eka methanin ayin kala */}
        </div>
      </section>

      {/* --- 2. Dynamic Stats Dashboard --- */}
      <section className="stats-dashboard-container">
        <h2>Project at a Glance</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <h3>{loading ? '...' : stats?.totalRuns.toLocaleString()}</h3>
            <p>Total Runs Analyzed</p>
          </div>
          <div className="stat-card">
            <h3>{loading ? '...' : stats?.totalWickets.toLocaleString()}</h3>
            <p>Total Wickets Taken</p>
          </div>
          <div className="stat-card">
            <h3>{loading ? '...' : stats?.topScorer.name}</h3>
            <p>Top Scorer ({loading ? '...' : stats?.topScorer.stat})</p>
          </div>
          <div className="stat-card">
            <h3>{loading ? '...' : stats?.topBowler.name}</h3>
            <p>Top Bowler ({loading ? '...' : stats?.topBowler.stat})</p>
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
          {/* Obata puluwan me 'src' link eka obage project demo video eke link eken maaru karanna */}
          <iframe 
            src="https://www.youtube.com/embed/nC4-5I-8__A" // Placeholder video
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