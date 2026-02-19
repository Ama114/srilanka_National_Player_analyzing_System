import React, { useState, useEffect } from 'react';
import axios from 'axios';
// URL query eka (search query) eka ganna import karanava
import { useLocation, useNavigate } from 'react-router-dom';
import '../styles/BowlingPerformancePage.css'; // Aluth CSS file ekata path eka

const MATCH_TYPES = ['ODI', 'T20', 'Test'];

// URL query eka parse karana helper function ekak
function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function BowlingPerformancePage() {
  const [players, setPlayers] = useState([]);
  const [grounds, setGrounds] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState('');
  const [selectedGround, setSelectedGround] = useState('');
  const [matchType, setMatchType] = useState(MATCH_TYPES[0]);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const query = useQuery();
  const navigate = useNavigate();
  const location = useLocation();

  const API_BASE_URL = 'http://127.0.0.1:5000/api/bowling'; // Bowling API path

  // 1. Players list eka load karanava
  useEffect(() => {
    setGrounds([]);
    setSelectedGround('');
    setStats(null);
    setError('');

    axios.get(`${API_BASE_URL}/players`, {
      params: { matchType }
    })
      .then(response => {
        const playerList = response.data;
        setPlayers(playerList);
      })
      .catch(err => console.error("Error fetching players:", err));
  }, [matchType]); // Match type venas unaama player list eka update karanava

  // 3. 'selectedPlayer' state eka venas veddi, e playerge grounds load karanava
  useEffect(() => {
    if (selectedPlayer) {
      setIsLoading(true);
      setGrounds([]);
      setSelectedGround('');
      setStats(null);
      axios.get(`${API_BASE_URL}/grounds-for-player`, {
        params: { player: selectedPlayer, matchType }
      })
        .then(response => {
          setGrounds(response.data);
          setIsLoading(false);
        })
        .catch(err => {
          console.error("Error fetching grounds:", err);
          setIsLoading(false);
        });
    }
  }, [selectedPlayer, matchType]); // Match type eka venas unaath data tika reset karanava

  const handleFetchStats = async () => {
    if (!selectedPlayer || !selectedGround) {
      setError('Please select both a player and a ground.');
      return;
    }
    setError('');
    setIsLoading(true);
    setStats(null);

    try {
      const response = await axios.get(`${API_BASE_URL}/player-ground-stats`, {
        params: { player: selectedPlayer, ground: selectedGround, matchType }
      });
      setStats(response.data);
    } catch (err) {
      setError('Failed to fetch stats. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Image eka nethnam default image eka load karana function eka
  const handleImageError = (e) => {
    e.target.src = '/images/players/default-avatar.png';
  };

  // Dropdown eken player venas karama URL ekath update karanava
  const updateUrlParams = (playerValue, matchTypeValue) => {
    const params = new URLSearchParams();
    if (playerValue) params.set('player', playerValue);
    if (matchTypeValue) params.set('matchType', matchTypeValue);
    const searchString = params.toString();
    navigate(`/bowling-performance${searchString ? `?${searchString}` : ''}`);
  };

  const handlePlayerChange = (e) => {
    const newPlayer = e.target.value;
    setSelectedPlayer(newPlayer);
    updateUrlParams(newPlayer, matchType);
  };

  const handleMatchTypeChange = (e) => {
    const newMatchType = e.target.value;
    setMatchType(newMatchType);
    updateUrlParams(selectedPlayer, newMatchType);
  };

  useEffect(() => {
    const playerFromUrl = query.get('player');
    if (playerFromUrl && players.includes(playerFromUrl)) {
      if (playerFromUrl !== selectedPlayer) {
        setSelectedPlayer(playerFromUrl);
      }
    }
    if (!playerFromUrl) {
      setSelectedPlayer('');
      setSelectedGround('');
      setStats(null);
    }
  }, [location.search, players, selectedPlayer]);

  useEffect(() => {
    const typeFromUrl = query.get('matchType');
    if (typeFromUrl && MATCH_TYPES.includes(typeFromUrl) && typeFromUrl !== matchType) {
      setMatchType(typeFromUrl);
    }
    if (!typeFromUrl && matchType !== MATCH_TYPES[0]) {
      setMatchType(MATCH_TYPES[0]);
    }
  }, [location.search, matchType]);

  return (
    <div className="performance-page-container">
      <h1>Player Bowling Performance by Ground</h1>
      <p className="subtitle">Select a player and a ground to see detailed bowling statistics.</p>

      <div className="selection-container">
        <select value={matchType} onChange={handleMatchTypeChange}>
          {MATCH_TYPES.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        <select value={selectedPlayer} onChange={handlePlayerChange}>
          <option value="" disabled>Select a Player</option>
          {players.map(player => <option key={player} value={player}>{player}</option>)}
        </select>
        <select value={selectedGround} onChange={(e) => setSelectedGround(e.target.value)} disabled={!selectedPlayer || isLoading}>
          <option value="" disabled>Select a Ground</option>
          {isLoading && !stats && <option>Loading grounds...</option>}
          {grounds.map(ground => <option key={ground} value={ground}>{ground}</option>)}
        </select>
        <button onClick={handleFetchStats} disabled={isLoading || !selectedGround}>
          {isLoading ? 'Analyzing...' : 'Analyze Stats'}
        </button>
      </div>

      {error && <p className="error-message">{error}</p>}

      {isLoading && !stats && <div className="skeleton-loader"></div>}

      {/* --- Aluth [Image | Stats] Layout eka --- */}
      {stats && !isLoading && (
        <div className="results-container">

          <div className="results-header">
            <h2>{selectedPlayer}</h2>
            <p>{selectedGround}</p>
          </div>

          <div className="results-layout-container">

            {/* Wam paththa: Player Image eka */}
            <div className="player-image-section">
              <img
                src={`/images/players/${selectedPlayer}.png`}
                alt={selectedPlayer}
                onError={handleImageError} // Image eka nethnam
              />
            </div>

            {/* Dakunu paththa: Stats tika */}
            <div className="stats-section">
              <h3>Key Statistics</h3>
              {/* Stats tika columns dekaka grid ekaka pennanava */}
              <div className="stats-grid-2-col">
                <div className="stat-card"><h4>Bowling Average</h4><p>{stats.average}</p></div>
                <div className="stat-card"><h4>Economy Rate</h4><p>{stats.economy}</p></div>
                <div className="stat-card"><h4>Matches Played</h4><p>{stats.matches}</p></div>
                <div className="stat-card"><h4>Total Wickets</h4><p>{stats.wickets}</p></div>
                <div className="stat-card"><h4>Runs Conceded</h4><p>{stats.runsConceded}</p></div>
                <div className="stat-card full-width"><h4>Best Opposition (by Wickets)</h4><p>{stats.bestOpposition}</p></div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default BowlingPerformancePage;