import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/BestXISelectionPage.css';

// --- Sub-Component: Player Card ---
const PlayerCard = ({ player, index, color }) => (
  <div className="field-player-card">
    <div className="card-top">
      <span className="player-rank">#{index + 1}</span>
      <span className="role-dot" style={{ backgroundColor: color }}></span>
    </div>
    <div className="player-avatar">
      <div className="avatar-circle" style={{ borderColor: color, color: color }}>
        {player.player_name.charAt(0)}
      </div>
    </div>
    <div className="player-info">
      <h3 className="player-name">{player.player_name}</h3>
      <div className="role-badge" style={{ backgroundColor: color }}>
        {player.role}
      </div>
      <div className="stats-row">
        <span className="score-label">Rating:</span>
        <span className="score-value" style={{ color: color }}>{player.predicted_score}</span>
      </div>
    </div>
  </div>
);

function BestXISelectionPage() {
  const [matchType, setMatchType] = useState('');
  const [opposition, setOpposition] = useState('');
  const [pitchType, setPitchType] = useState('');
  const [weather, setWeather] = useState('');
  
  const [matchTypes, setMatchTypes] = useState([]);
  const [oppositions, setOppositions] = useState([]);
  const [pitchTypes, setPitchTypes] = useState([]);
  const [weatherTypes, setWeatherTypes] = useState([]);
  
  const [bestTeam, setBestTeam] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const API_BASE_URL = 'http://127.0.0.1:5000/api';

  useEffect(() => {
    const fetchDropdownData = async () => {
      try {
        const matchRes = await axios.get(`${API_BASE_URL}/ml/match-types`);
        setMatchTypes(matchRes.data);
        const oppRes = await axios.get(`${API_BASE_URL}/ml/oppositions`);
        setOppositions(oppRes.data);
        const pitchRes = await axios.get(`${API_BASE_URL}/ml/pitch-types`);
        setPitchTypes(pitchRes.data);
        const weatherRes = await axios.get(`${API_BASE_URL}/ml/weather-conditions`);
        setWeatherTypes(weatherRes.data);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load options. Is backend running?');
      }
    };
    fetchDropdownData();
  }, []);

  const generateBestXI = async () => {
    if (!opposition || !pitchType || !weather || !matchType) {
      setError('Please select all fields.');
      return;
    }
    setLoading(true);
    setError('');
    setBestTeam([]);

    try {
      const response = await axios.post(`${API_BASE_URL}/predict-team`, {
        match_type: matchType,
        opposition: opposition,
        pitch_type: pitchType,
        weather: weather
      });

      if (response.data.status === 'success') {
        setBestTeam(response.data.team);
        if (response.data.team.length === 0) setError('No suitable players found.');
      } else {
        setError(response.data.message || 'Error generating team.');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Server connection error.');
    } finally {
      setLoading(false);
    }
  };

  const getRoleColor = (role) => {
    if (!role) return '#999';
    const r = role.toLowerCase();
    if (r.includes('keeper')) return matchType === 'T20' ? '#FF9800' : '#FFC107';
    if (r.includes('batsman')) return '#4CAF50';
    if (r.includes('bowler')) return matchType === 'T20' ? '#E91E63' : '#F44336';
    if (r.includes('all')) return matchType === 'T20' ? '#673AB7' : '#9C27B0';
    return '#607D8B';
  };

  return (
    <div className="selection-page-container">
      <h1>Best XI Selection</h1>
      <p className="subtitle">AI-Powered Team Prediction</p>

      <div className="condition-selector">
        <div className="form-group">
          <label>Match Format</label>
          <select value={matchType} onChange={(e) => setMatchType(e.target.value)}>
             <option value="">Select Format</option>
            {matchTypes.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Opposition</label>
          <select value={opposition} onChange={(e) => setOpposition(e.target.value)}>
            <option value="">Select Opposition</option>
            {oppositions.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Pitch</label>
          <select value={pitchType} onChange={(e) => setPitchType(e.target.value)}>
             <option value="">Select Pitch</option>
            {pitchTypes.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Weather</label>
          <select value={weather} onChange={(e) => setWeather(e.target.value)}>
             <option value="">Select Weather</option>
            {weatherTypes.map(w => <option key={w} value={w}>{w}</option>)}
          </select>
        </div>
        <button onClick={generateBestXI} disabled={loading} className="suggest-btn">
          {loading ? 'Analyzing...' : 'Generate Best XI'}
        </button>
      </div>

      {error && <div className="error-message">⚠️ {error}</div>}
      {loading && <div className="skeleton-loader"><div className="spinner"></div><p>Processing...</p></div>}

      {!loading && bestTeam.length > 0 && (
        <div className="team-display-container">
          <div className="results-header">
            <h2 style={{ color: matchType === 'T20' ? '#E65100' : '#1565C0' }}>
              {matchType} Recommended XI
            </h2>
            <span className="badge">vs {opposition}</span>
          </div>
          
          <div className="field-formation" style={{ 
            background: matchType === 'T20' 
              ? 'linear-gradient(135deg, #263238 0%, #37474F 100%)' 
              : 'linear-gradient(135deg, #4caf50 0%, #2e7d32 100%)',
            borderColor: matchType === 'T20' ? '#E65100' : '#4caf50'
          }}>
            <div className="players-grid">
               {bestTeam.map((player, index) => (
                  <PlayerCard 
                    key={index} 
                    player={player} 
                    index={index} 
                    color={getRoleColor(player.role)} 
                  />
               ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default BestXISelectionPage;