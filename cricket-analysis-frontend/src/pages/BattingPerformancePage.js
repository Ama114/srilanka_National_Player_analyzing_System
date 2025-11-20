import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom'; // useLocation ඉවත් කළා
import '../styles/BattingPerformancePage.css';

function BattingPerformancePage() {
  const [players, setPlayers] = useState([]);
  const [grounds, setGrounds] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState('');
  const [selectedGround, setSelectedGround] = useState('');
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const API_BASE_URL = 'http://127.0.0.1:5000/api';

  // Player list එක load කරනවා
  useEffect(() => {
    axios.get(`${API_BASE_URL}/players`)
      .then(response => {
        setPlayers(response.data);
      })
      .catch(err => console.error("Error fetching players:", err));
  }, []);

  // Player තේරුවම grounds load කරනවා
  useEffect(() => {
    if (selectedPlayer) {
      setGrounds([]);
      setSelectedGround('');
      setStats(null);
      axios.get(`${API_BASE_URL}/grounds-for-player?player=${selectedPlayer}`)
        .then(response => setGrounds(response.data))
        .catch(err => console.error("Error fetching grounds:", err));
    }
  }, [selectedPlayer]);

  // URL query එකෙන් player load කරන useEffect එක මෙතනින් ඉවත් කළා

  const handleFetchStats = async () => {
    if (!selectedPlayer || !selectedGround) {
      setError('Please select both a player and a ground.');
      return;
    }
    setError('');
    setIsLoading(true);
    setStats(null);

    try {
      const statsResponse = await axios.get(`${API_BASE_URL}/player-ground-stats?player=${selectedPlayer}&ground=${selectedGround}`);
      setStats(statsResponse.data);
    } catch (err) {
      setError('Failed to fetch stats. Please try again.');
      console.error("Error fetching stats:", err);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleImageError = (e) => {
    e.target.src = '/images/players/default-avatar.png';
  };

  return (
    <div className="performance-page-container">
      <h1>Player Performance by Ground</h1>
      <p className="subtitle">Select a player and a ground to see detailed batting statistics.</p>
      
      <div className="selection-container">
        <select value={selectedPlayer} onChange={(e) => setSelectedPlayer(e.target.value)}>
          <option value="" disabled>Select a Player</option>
          {players.map(player => <option key={player} value={player}>{player}</option>)}
        </select>
        <select value={selectedGround} onChange={(e) => setSelectedGround(e.target.value)} disabled={!selectedPlayer}>
          <option value="" disabled>Select a Ground</option>
          {grounds.map(ground => <option key={ground} value={ground}>{ground}</option>)}
        </select>
        <button onClick={handleFetchStats} disabled={isLoading || !selectedGround}>
          {isLoading ? 'Analyzing...' : 'Analyze Stats'}
        </button>
      </div>

      {error && <p className="error-message">{error}</p>}
      {isLoading && <div className="skeleton-loader"></div>}

      {/* Results Layout */}
      {stats && !isLoading && (
        <div className="results-container">
          <div className="results-header">
            <h2>{selectedPlayer}</h2>
            <p>{selectedGround}</p>
          </div>
          <div className="results-layout-container">
            <div className="player-image-section">
              <img 
                src={`/images/players/${selectedPlayer}.png`} 
                alt={selectedPlayer}
                onError={handleImageError}
              />
            </div>
            <div className="stats-section">
              <h3>Key Statistics</h3>
              <div className="stats-grid-2-col">
                <div className="stat-card"><h4>Batting Average</h4><p>{stats.average}</p></div>
                <div className="stat-card"><h4>Strike Rate</h4><p>{stats.strikeRate}</p></div>
                <div className="stat-card"><h4>Matches Played</h4><p>{stats.matches}</p></div>
                <div className="stat-card"><h4>Total Runs</h4><p>{stats.totalRuns}</p></div>
                <div className="stat-card"><h4>Total 4s</h4><p>{stats.total4s}</p></div>
                <div className="stat-card"><h4>Total 6s</h4><p>{stats.total6s}</p></div>
                <div className="stat-card"><h4>Recommended Position</h4><p>#{stats.recommendedPosition}</p></div>
                <div className="stat-card"><h4>Most Frequent Dismissal</h4><p>{stats.mostFrequentDismissal}</p></div>
                <div className="stat-card full-width"><h4>Best Opposition (by Runs)</h4><p>{stats.bestOpposition}</p></div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default BattingPerformancePage;