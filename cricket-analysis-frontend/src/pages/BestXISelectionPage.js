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
        {player.player_name ? player.player_name.charAt(0) : '?'}
      </div>
    </div>
    <div className="player-info">
      <h3 className="player-name">{player.player_name}</h3>
      <div className="role-badge" style={{ backgroundColor: color }}>
        {player.role}
      </div>
      <div className="stats-row">
        <span className="score-label">Rating:</span>
        <span className="score-value" style={{ color: color }}>
            {player.predicted_score}
        </span>
      </div>
    </div>
  </div>
);

function BestXISelectionPage() {
  // State
  const [matchType, setMatchType] = useState('');
  const [opposition, setOpposition] = useState('');
  const [pitchType, setPitchType] = useState('');
  const [weather, setWeather] = useState('');
  
  const [dropdownOptions, setDropdownOptions] = useState({
      matchTypes: [],
      oppositions: [],
      pitchTypes: [],
      weatherTypes: []
  });
  
  const [bestTeam, setBestTeam] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const API_BASE_URL = 'http://127.0.0.1:5000/api';

  // --- 1. OPTIMIZED DATA FETCHING (Promise.all) ---
  useEffect(() => {
    const fetchAllDropdowns = async () => {
      try {
        // API Calls 4ම එකවර යවයි (Parallel Requests)
        const [matchRes, oppRes, pitchRes, weatherRes] = await Promise.all([
            axios.get(`${API_BASE_URL}/ml/match-types`),
            axios.get(`${API_BASE_URL}/ml/oppositions`),
            axios.get(`${API_BASE_URL}/ml/pitch-types`),
            axios.get(`${API_BASE_URL}/ml/weather-conditions`)
        ]);

        setDropdownOptions({
            matchTypes: matchRes.data,
            oppositions: oppRes.data,
            pitchTypes: pitchRes.data,
            weatherTypes: weatherRes.data
        });

      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load dropdown options. Check Backend.');
      }
    };
    fetchAllDropdowns();
  }, []);

  // --- 2. INPUT CHANGE HANDLERS (Clear Team on Change) ---
  const handleMatchChange = (e) => { setMatchType(e.target.value); setBestTeam([]); };
  const handleOppChange = (e) => { setOpposition(e.target.value); setBestTeam([]); };
  const handlePitchChange = (e) => { setPitchType(e.target.value); setBestTeam([]); };
  const handleWeatherChange = (e) => { setWeather(e.target.value); setBestTeam([]); };

  // --- 3. TEAM GENERATION LOGIC ---
  const generateBestXI = async () => {
    if (!opposition || !pitchType || !weather || !matchType) {
      setError('Please select all 4 conditions to generate a team.');
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
        setBestTeam(response.data.team || []);
        if (response.data.team.length === 0) {
            setError('No players found in database matching criteria.');
        }
      } else {
        setError(response.data.message || 'Error generating team.');
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || 'Server connection failed.');
    } finally {
      setLoading(false);
    }
  };

  // --- 4. IMPROVED COLOR LOGIC (Including TEST) ---
  const getRoleColor = (role) => {
    if (!role) return '#999';
    const r = role.toLowerCase();

    // TEST Match Colors (Classic Red/White vibe)
    if (matchType === 'TEST') {
        if (r.includes('keeper')) return '#D32F2F'; // Red
        if (r.includes('batsman')) return '#388E3C'; // Green
        if (r.includes('bowler')) return '#C62828'; // Dark Red
        return '#1976D2'; // All Rounder Blue
    }

    // T20 Colors (Vibrant)
    if (matchType === 'T20') {
        if (r.includes('keeper')) return '#FF9800';
        if (r.includes('batsman')) return '#00E676';
        if (r.includes('bowler')) return '#F50057';
        return '#651FFF';
    }

    // ODI Colors (Standard)
    if (r.includes('keeper')) return '#FFC107';
    if (r.includes('batsman')) return '#4CAF50';
    if (r.includes('bowler')) return '#F44336';
    return '#9C27B0';
  };

  return (
    <div className="selection-page-container">
      <h1>Best XI Selector</h1>
      <p className="subtitle">AI-Powered Team Prediction System</p>

      {/* --- INPUT SECTION --- */}
      <div className="condition-selector">
        <div className="form-group">
          <label>Match Format</label>
          <select value={matchType} onChange={handleMatchChange}>
             <option value="">Select Format</option>
            {dropdownOptions.matchTypes.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Opposition</label>
          <select value={opposition} onChange={handleOppChange}>
            <option value="">Select Opposition</option>
            {dropdownOptions.oppositions.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Pitch Condition</label>
          <select value={pitchType} onChange={handlePitchChange}>
             <option value="">Select Pitch</option>
            {dropdownOptions.pitchTypes.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Weather</label>
          <select value={weather} onChange={handleWeatherChange}>
             <option value="">Select Weather</option>
            {dropdownOptions.weatherTypes.map(w => <option key={w} value={w}>{w}</option>)}
          </select>
        </div>
        <button onClick={generateBestXI} disabled={loading} className="suggest-btn">
          {loading ? 'Analyzing Data...' : 'Generate Best XI'}
        </button>
      </div>

      {/* --- STATUS MESSAGES --- */}
      {error && <div className="error-message">⚠️ {error}</div>}
      
      {/* --- RESULTS SECTION --- */}
      {!loading && bestTeam.length > 0 && (
        <div className="team-display-container">
          <div className="results-header">
            <h2 style={{ color: matchType === 'T20' ? '#E65100' : (matchType === 'TEST' ? '#D32F2F' : '#1565C0') }}>
              {matchType} Squad vs {opposition}
            </h2>
            <span className="badge">{pitchType} Pitch</span>
          </div>
          
          <div className="field-formation" style={{ 
            background: matchType === 'T20' 
              ? 'linear-gradient(135deg, #263238 0%, #37474F 100%)' 
              : (matchType === 'TEST' ? 'linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%)' : 'linear-gradient(135deg, #4caf50 0%, #2e7d32 100%)'),
            borderColor: matchType === 'T20' ? '#E65100' : (matchType === 'TEST' ? '#D32F2F' : '#4caf50'),
            borderWidth: '2px',
            borderStyle: 'solid'
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