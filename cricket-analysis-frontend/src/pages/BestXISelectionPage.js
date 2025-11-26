import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/BestXISelectionPage.css';

function BestXISelectionPage() {
  const [matchType, setMatchType] = useState('ODI');
  const [opposition, setOpposition] = useState('Bangladesh');
  const [oppositions, setOppositions] = useState([]);
  const [pitchType, setPitchType] = useState('Balanced');
  const [weather, setWeather] = useState('Balanced');
  
  const [bestTeam, setBestTeam] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const MATCH_TYPES = ['ODI', 'T20', 'Test'];
  const PITCH_TYPES = ['Batting Friendly', 'Bowling Friendly', 'Spin Friendly', 'Balanced'];
  const WEATHER_TYPES = ['Balanced', 'Sunny', 'Cloudy', 'Humid', 'Rainy'];
  
  const API_BASE_URL = 'http://127.0.0.1:5000/api';

  // Load oppositions when component mounts
  useEffect(() => {
    const loadOppositions = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/ml/oppositions`);
        setOppositions(response.data);
      } catch (err) {
        console.error('Error loading oppositions:', err);
        setOppositions(['Bangladesh', 'India', 'Australia', 'England']);
      }
    };
    loadOppositions();
  }, []);

  // Generate Best XI
  const generateBestXI = async () => {
    if (!opposition || !pitchType || !weather || !matchType) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError('');
    setBestTeam([]);

    try {
      const response = await axios.get(`${API_BASE_URL}/best-xi/generate`, {
        params: {
          opposition: opposition,
          pitch_type: pitchType,
          weather: weather,
          match_type: matchType
        }
      });

      setBestTeam(response.data);
      if (response.data.length === 0) {
        setError('No players found for the selected conditions');
      }
    } catch (err) {
      console.error('Error generating Best XI:', err);
      setError(err.response?.data?.error || 'Could not generate team. Please check the backend.');
    } finally {
      setLoading(false);
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'Wicket Keeper':
        return '#FFD700';
      case 'Batsman':
        return '#4CAF50';
      case 'Bowler':
        return '#FF6B6B';
      case 'All-Rounder':
        return '#9C27B0';
      default:
        return '#999';
    }
  };

  return (
    <div className="selection-page-container">
      <h1>Best XI Selection</h1>
      <p className="subtitle">Select match conditions to generate the best playing XI</p>

      <div className="condition-selector">
        <div className="form-group">
          <label>Match Type</label>
          <select value={matchType} onChange={(e) => setMatchType(e.target.value)}>
            {MATCH_TYPES.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Opposition</label>
          <select value={opposition} onChange={(e) => setOpposition(e.target.value)}>
            <option value="">Select Opposition</option>
            {oppositions.map(opp => (
              <option key={opp} value={opp}>{opp}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Pitch Type</label>
          <select value={pitchType} onChange={(e) => setPitchType(e.target.value)}>
            {PITCH_TYPES.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Weather</label>
          <select value={weather} onChange={(e) => setWeather(e.target.value)}>
            {WEATHER_TYPES.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <button 
          onClick={generateBestXI} 
          disabled={loading}
          className="suggest-btn"
        >
          {loading ? 'Generating...' : 'Generate Best XI'}
        </button>
      </div>

      {error && <p className="error-message">{error}</p>}

      {loading && <div className="skeleton-loader"></div>}

      {bestTeam.length > 0 && !loading && (
        <div className="team-display-container">
          <h2>Best XI for {matchType} vs {opposition}</h2>
          <p className="team-info">
            {matchType} Match | {pitchType} Pitch | {weather} Weather
          </p>
          
          {/* Cricket Field Formation */}
          <div className="field-formation">
            {/* Wicket Keepers */}
            {bestTeam.filter(p => p.role === 'Wicket Keeper').length > 0 && (
              <div className="formation-section wicket-keeper-section">
                <h4>Wicket Keeper</h4>
                <div className="players-row">
                  {bestTeam.filter(p => p.role === 'Wicket Keeper').map((player, index) => (
                    <div key={index} className="field-player-card">
                      <div className="role-badge" style={{ backgroundColor: getRoleColor(player.role) }}>
                        {player.role}
                      </div>
                      <p className="player-name">{player.player_name}</p>
                      <p className="player-type">{player.player_type}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Batsmen */}
            {bestTeam.filter(p => p.role === 'Batsman').length > 0 && (
              <div className="formation-section batsman-section">
                <h4>Batsmen</h4>
                <div className="players-row">
                  {bestTeam.filter(p => p.role === 'Batsman').map((player, index) => (
                    <div key={index} className="field-player-card">
                      <div className="role-badge" style={{ backgroundColor: getRoleColor(player.role) }}>
                        {player.role}
                      </div>
                      <p className="player-name">{player.player_name}</p>
                      <p className="player-type">{player.player_type}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* All-Rounders */}
            {bestTeam.filter(p => p.role === 'All-Rounder').length > 0 && (
              <div className="formation-section all-rounder-section">
                <h4>All-Rounders</h4>
                <div className="players-row">
                  {bestTeam.filter(p => p.role === 'All-Rounder').map((player, index) => (
                    <div key={index} className="field-player-card">
                      <div className="role-badge" style={{ backgroundColor: getRoleColor(player.role) }}>
                        {player.role}
                      </div>
                      <p className="player-name">{player.player_name}</p>
                      <p className="player-type">{player.player_type}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Bowlers */}
            {bestTeam.filter(p => p.role === 'Bowler').length > 0 && (
              <div className="formation-section bowler-section">
                <h4>Bowlers</h4>
                <div className="players-row">
                  {bestTeam.filter(p => p.role === 'Bowler').map((player, index) => (
                    <div key={index} className="field-player-card">
                      <div className="role-badge" style={{ backgroundColor: getRoleColor(player.role) }}>
                        {player.role}
                      </div>
                      <p className="player-name">{player.player_name}</p>
                      <p className="player-type">{player.player_type}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="team-summary">
            <h3>Team Summary:</h3>
            <ul>
              <li>Wicket Keepers: {bestTeam.filter(p => p.role === 'Wicket Keeper').length}</li>
              <li>Batsmen: {bestTeam.filter(p => p.role === 'Batsman').length}</li>
              <li>Bowlers: {bestTeam.filter(p => p.role === 'Bowler').length}</li>
              <li>All-Rounders: {bestTeam.filter(p => p.role === 'All-Rounder').length}</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default BestXISelectionPage;