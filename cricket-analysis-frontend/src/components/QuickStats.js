import React from 'react';
import '../styles/QuickStats.css';

function QuickStats() {
  return (
    <section className="quick-stats-section">
      <div className="stat-card">
        <span className="stat-number">250+</span>
        <p className="stat-label">Players Profiled</p>
      </div>
      <div className="stat-card">
        <span className="stat-number">1000+</span>
        <p className="stat-label">Matches Analyzed</p>
      </div>
      <div className="stat-card">
        <span className="stat-number">10,000+</span>
        <p className="stat-label">Data Points</p>
      </div>
    </section>
  );
}

export default QuickStats;