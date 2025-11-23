import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import '../styles/BestXISelectionPage.css';

function BestXISelectionPage() {
  const [oppositions, setOppositions] = useState([]);
  const [pitchTypes] = useState(['Batting Friendly', 'Bowling Friendly', 'Spin Friendly', 'Balanced']);
  const [weatherTypes, setWeatherTypes] = useState([]);
  const [matchTypes] = useState(['ODI', 'T20', 'Test']);
  const [playerPool, setPlayerPool] = useState([]);

  const ROLE_OPTIONS = ['Batsman', 'Bowler', 'All-Rounder', 'Wicket Keeper'];

  const [selectedOpposition, setSelectedOpposition] = useState('Bangladesh');
  const [selectedPitch, setSelectedPitch] = useState('Balanced');
  const [selectedWeather, setSelectedWeather] = useState('Balanced');
  const [selectedMatchType, setSelectedMatchType] = useState('ODI');
  const [autoGenerateTriggered, setAutoGenerateTriggered] = useState(false);
  
  // Default example values for dropdowns
  const DEFAULT_OPPOSITION = 'Bangladesh';
  const DEFAULT_PITCH = 'Balanced';
  const DEFAULT_WEATHER = 'Balanced';
  const DEFAULT_MATCH_TYPE = 'ODI';
  const [playerForm, setPlayerForm] = useState({ player_name: '', player_type: '', role: '' });
  const [editingPlayerId, setEditingPlayerId] = useState(null);
  const [editingPlayerOriginalName, setEditingPlayerOriginalName] = useState('');
  const [poolLoading, setPoolLoading] = useState(false);
  const [poolFeedback, setPoolFeedback] = useState({ type: '', message: '' });
  const [teamNotice, setTeamNotice] = useState('');
  const playerFormRef = useRef(null);

  // suggestedTeam state එකේ දැන් objects තියෙන්නේ
  const [suggestedTeam, setSuggestedTeam] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [generatedTeams, setGeneratedTeams] = useState([]);
  const [loadingTeams, setLoadingTeams] = useState(false);
  
  const API_BASE_URL = 'http://127.0.0.1:5000/api';

  const loadGeneratedTeams = React.useCallback(() => {
    // Load the most recent team automatically only if no team is currently displayed
    setLoadingTeams(true);
    axios.get(`${API_BASE_URL}/best-xi/generated-teams`)
      .then(res => {
        setGeneratedTeams(res.data);
        setSuggestedTeam(prev => {
          if (prev.length === 0 && res.data.length > 0) {
            const latestTeam = res.data[0];
            // Set dropdown values from the loaded team only if they exist
            if (latestTeam.opposition) setSelectedOpposition(latestTeam.opposition);
            if (latestTeam.pitch_type) setSelectedPitch(latestTeam.pitch_type);
            if (latestTeam.weather) setSelectedWeather(latestTeam.weather);
            if (latestTeam.match_type) setSelectedMatchType(latestTeam.match_type);
            setTeamNotice(`Loaded previously generated team: ${latestTeam.team_name}`);
            setAutoGenerateTriggered(true); // Prevent auto-generate if we loaded a previous team
            return latestTeam.players || [];
          }
          // Keep existing default values, don't overwrite if no previous team
          return prev;
        });
      })
      .catch(err => {
        console.error("Error loading generated teams:", err);
        // On error, keep existing values - don't overwrite
      })
      .finally(() => {
        setLoadingTeams(false);
      });
  }, []);

  useEffect(() => {
    let isMounted = true;
    fetchPlayerPool();
    loadGeneratedTeams();
    
    // Load oppositions with error handling
    axios.get(`${API_BASE_URL}/ml/oppositions`)
      .then(res => {
        if (isMounted) {
          setOppositions(res.data);
          setError(''); // Clear error on success
        }
      })
      .catch(err => {
        console.error("Error loading oppositions:", err);
        if (isMounted) {
          setError("Cannot connect to backend server. Please make sure Flask backend is running on port 5000.");
        }
      });
    
    // Load weather types
    axios.get(`${API_BASE_URL}/ml/weather-types`)
      .then(res => {
        if (isMounted) {
          setWeatherTypes(res.data);
        }
      })
      .catch(err => {
        console.error("Error loading weather types:", err);
        // Set default weather types if API fails
        if (isMounted) {
          setWeatherTypes(['Balanced', 'Cloudy', 'Dry', 'Hot', 'Rainy']);
        }
      });
    
    return () => {
      isMounted = false;
    };
  }, [loadGeneratedTeams]);

  const buildTeamWithFallbacks = React.useCallback((team) => {
    const uniqueTeam = [];
    const seenNames = new Set();

    team.forEach((player) => {
      if (!player || !player.name) return;
      if (!seenNames.has(player.name)) {
        uniqueTeam.push(player);
        seenNames.add(player.name);
      }
    });

    if (uniqueTeam.length >= 11) {
      return { team: uniqueTeam.slice(0, 11), notice: '' };
    }

    const needed = 11 - uniqueTeam.length;
    const fallbackCandidates = playerPool.filter((candidate) => !seenNames.has(candidate.player_name));
    const fallbackPlayers = fallbackCandidates.slice(0, needed).map((player) => ({
      id: player.id,
      name: player.player_name,
      role: player.role
    }));

    const totalCount = uniqueTeam.length + fallbackPlayers.length;
    const notice = fallbackPlayers.length < needed
      ? `Only ${totalCount} player${totalCount === 1 ? '' : 's'} available. Add more players using the form below to unlock the full XI.`
      : 'Filled remaining slots with available players from the pool.';

    return { team: uniqueTeam.concat(fallbackPlayers), notice };
  }, [playerPool]);

  const applyTeamWithFallbacks = React.useCallback((team, options = {}) => {
    const { defaultNotice = '', forceNotice = false } = options;
    const { team: fullTeam, notice } = buildTeamWithFallbacks(team);

    if (notice) {
      setTeamNotice(notice);
    } else if (defaultNotice && (forceNotice || team.length !== fullTeam.length)) {
      setTeamNotice(defaultNotice);
    } else {
      setTeamNotice('');
    }

    return fullTeam;
  }, [buildTeamWithFallbacks]);

  const handleSuggestTeam = React.useCallback(() => {
    if (!selectedOpposition || !selectedPitch || !selectedWeather || !selectedMatchType) {
      setError('Please select opposition, pitch type, weather, and match type.');
      return;
    }
    setError('');
    setIsLoading(true);
    setTeamNotice('');
    setSuggestedTeam([]);

    const params = {
      opposition: selectedOpposition,
      pitch: selectedPitch,
      weather: selectedWeather,
      match_type: selectedMatchType
    };
    
    axios.get(`${API_BASE_URL}/suggest-best-xi`, { params })
      .then(response => {
        if (!response.data || !Array.isArray(response.data)) {
          setError('Invalid response from server. Please try again.');
          setIsLoading(false);
          return;
        }

        if (response.data.length === 0) {
          setError('No players found. Please check the dataset.');
          setIsLoading(false);
          return;
        }

        const enrichedTeam = response.data.map(player => {
          const poolPlayer = playerPool.find(p => p.player_name === player.name);
          return {
            id: poolPlayer?.id || null,
            name: player.name || player.Player_Name || 'Unknown',
            role: player.role || player.Role || 'Player'
          };
        });
        
        setSuggestedTeam(applyTeamWithFallbacks(enrichedTeam));
        setError(''); // Clear any previous errors
        
        // Show success message
        if (enrichedTeam.length === 11) {
          setTeamNotice(`Successfully generated Best XI for ${selectedMatchType} match against ${selectedOpposition} on ${selectedPitch} pitch (${selectedWeather} weather).`);
        }
        
        // Reload generated teams list
        loadGeneratedTeams();
      })
      .catch(err => {
        console.error("Error fetching team suggestion:", err);
        setSuggestedTeam([]);
        
        if (err.response?.data?.error) {
          setError(`Error: ${err.response.data.error}`);
        } else if (err.message === 'Network Error' || err.code === 'ERR_NETWORK') {
          setError("Cannot connect to backend server. Please make sure Flask backend is running on port 5000.");
        } else {
          setError("Could not suggest a team. Please check the backend server and try again.");
        }
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [selectedOpposition, selectedPitch, selectedWeather, selectedMatchType, playerPool, loadGeneratedTeams, applyTeamWithFallbacks]);

  // Auto-generate team when all values are set and data is loaded
  useEffect(() => {
    // Only auto-generate if:
    // 1. Not already triggered
    // 2. All dropdowns have values
    // 3. Oppositions and weather types are loaded
    // 4. No previous team was loaded
    if (!autoGenerateTriggered && 
        selectedOpposition && 
        selectedPitch && 
        selectedWeather && 
        selectedMatchType &&
        oppositions.length > 0 &&
        weatherTypes.length > 0 &&
        suggestedTeam.length === 0 &&
        !isLoading &&
        !loadingTeams) {
      setAutoGenerateTriggered(true);
      // Small delay to ensure everything is ready
      setTimeout(() => {
        handleSuggestTeam();
      }, 500);
    }
  }, [selectedOpposition, selectedPitch, selectedWeather, selectedMatchType, oppositions.length, weatherTypes.length, suggestedTeam.length, isLoading, loadingTeams, autoGenerateTriggered, handleSuggestTeam]);

  const fetchPlayerPool = () => {
    setPoolLoading(true);
    axios.get(`${API_BASE_URL}/best-xi/players`)
      .then(res => {
        setPlayerPool(res.data);
        setPoolLoading(false);
      })
      .catch(err => {
        console.error("Error loading player pool:", err);
        setPoolLoading(false);
        setPoolFeedback({ type: 'error', message: 'Could not load player pool.' });
      });
  };

  useEffect(() => {
    if (!playerPool.length) return;
    setSuggestedTeam(prevTeam =>
      applyTeamWithFallbacks(
        prevTeam.map(member => {
          if (member.id) return member;
          const match = playerPool.find(p => p.player_name === member.name);
          return match ? { ...member, id: match.id } : member;
        })
      )
    );
  }, [playerPool, applyTeamWithFallbacks]);

  const scrollToPlayerForm = () => {
    if (playerFormRef.current) {
      playerFormRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      const input = playerFormRef.current.querySelector('input[name="player_name"]');
      if (input) {
        setTimeout(() => input.focus(), 250);
      }
    }
  };

  const resetPlayerForm = () => {
    setPlayerForm({ player_name: '', player_type: '', role: '' });
    setEditingPlayerId(null);
    setEditingPlayerOriginalName('');
  };

  const handleAddNewPlayer = () => {
    resetPlayerForm();
    setPoolFeedback({ type: '', message: '' });
    scrollToPlayerForm();
  };

  const handlePlayerFormChange = (e) => {
    const { name, value } = e.target;
    setPlayerForm(prev => ({ ...prev, [name]: value }));
  };

  const handlePlayerSubmit = (e) => {
    e.preventDefault();
    setPoolFeedback({ type: '', message: '' });

    if (!playerForm.player_name || !playerForm.player_type || !playerForm.role) {
      setPoolFeedback({ type: 'error', message: 'Please fill in player name, type and role.' });
      return;
    }

    const request = editingPlayerId
      ? axios.put(`${API_BASE_URL}/best-xi/players/${editingPlayerId}`, playerForm)
      : axios.post(`${API_BASE_URL}/best-xi/players`, playerForm);

    request
      .then((response) => {
        const savedPlayer = response.data;

        if (editingPlayerId) {
          setPlayerPool(prev => prev.map(player => player.id === savedPlayer.id ? savedPlayer : player));
          setSuggestedTeam(prev =>
            applyTeamWithFallbacks(
              prev.map(member => {
                if (member.id === savedPlayer.id || (!member.id && member.name === editingPlayerOriginalName)) {
                  return { ...member, id: savedPlayer.id, name: savedPlayer.player_name, role: savedPlayer.role };
                }
                return member;
              })
            )
          );
        } else {
          setPlayerPool(prev => [...prev, savedPlayer]);
          setSuggestedTeam(prev => {
            const exists = prev.some(member => member.id === savedPlayer.id || member.name === savedPlayer.player_name);
            if (exists) return applyTeamWithFallbacks(prev);
            return applyTeamWithFallbacks([...prev, { id: savedPlayer.id, name: savedPlayer.player_name, role: savedPlayer.role }]);
          });
        }

        setPoolFeedback({ type: 'success', message: editingPlayerId ? 'Player updated.' : 'Player added.' });
        resetPlayerForm();
      })
      .catch(err => {
        console.error("Error saving player:", err);
        setPoolFeedback({ type: 'error', message: 'Unable to save player. Make sure the name is unique.' });
      });
  };

  const handleEditPlayer = (player) => {
    setPlayerForm({
      player_name: player.player_name,
      player_type: player.player_type,
      role: player.role
    });
    setEditingPlayerId(player.id);
    setEditingPlayerOriginalName(player.player_name);
    setPoolFeedback({ type: '', message: '' });
  };

  const handleQuickEdit = (playerName) => {
    const player = playerPool.find((p) => p.player_name === playerName);
    if (!player) {
      setPoolFeedback({ type: 'error', message: 'Player is not yet in the editable pool. Add them below.' });
      scrollToPlayerForm();
      return;
    }
    handleEditPlayer(player);
    scrollToPlayerForm();
  };

  const handleDeletePlayer = (playerId, playerName = '') => {
    if (!window.confirm('Remove this player permanently from the dataset?')) return;
    setPoolFeedback({ type: '', message: '' });
    setTeamNotice('');
    axios.delete(`${API_BASE_URL}/best-xi/players/${playerId}`)
      .then(() => {
        setPoolFeedback({ type: 'success', message: 'Player removed.' });
        if (editingPlayerId === playerId) {
          resetPlayerForm();
        }
        setPlayerPool(prev => prev.filter(player => player.id !== playerId));
        setSuggestedTeam(prev =>
          applyTeamWithFallbacks(
            prev.filter(member => {
              if (member.id) {
                return member.id !== playerId;
              }
              return member.name !== playerName;
            })
          )
        );
      })
      .catch(err => {
        console.error("Error deleting player:", err);
        setPoolFeedback({ type: 'error', message: 'Unable to delete player.' });
      });
  };

  const handleQuickDelete = (playerName) => {
    setSuggestedTeam(prev => {
      const filtered = prev.filter(member => member.name !== playerName);
      const remaining = filtered.length;
      if (remaining < 11) {
        setTeamNotice(`Player removed. ${remaining}/11 players. Click "Suggest Best XI" again to regenerate a full team.`);
      } else {
        setTeamNotice('Player removed from this suggestion.');
      }
      return filtered;
    });
  };

  // Role එකට ගැලපෙන class එකක් return කරන function එක
  const getRoleClassName = (role) => {
    if (role === 'Wicket Keeper') return 'role-wk';
    if (role === 'Batsman') return 'role-bat';
    if (role === 'Bowler') return 'role-bowl';
    if (role === 'All-Rounder') return 'role-ar';
    return '';
  };

  return (
    <div className="selection-page-container">
      <h1>Best XI Suggestion Team</h1>
      <p className="subtitle">Select the conditions to get a predicted best playing XI</p>
      

      {!suggestedTeam.length && !isLoading && (
        <div className="instruction-box">
          <h3>📋 How to Use:</h3>
          <ol>
            <li>Select <strong>Opposition</strong> team (e.g., Bangladesh, India, Australia)</li>
            <li>Select <strong>Pitch Type</strong> (Batting Friendly, Bowling Friendly, Spin Friendly, or Balanced)</li>
            <li>Select <strong>Weather</strong> condition (Balanced, Cloudy, Dry, Hot, or Rainy)</li>
            <li>Select <strong>Match Type</strong> (ODI, T20, or Test)</li>
            <li>Click <strong>"Suggest Best XI"</strong> button to generate the team</li>
            <li>Or click on a <strong>Previously Generated Team</strong> above to load it</li>
          </ol>
        </div>
      )}
      
      <div className="condition-selector">
        <select value={selectedOpposition} onChange={(e) => setSelectedOpposition(e.target.value)}>
          <option value="" disabled>Select Opposition</option>
          {oppositions.map(opp => <option key={opp} value={opp}>{opp}</option>)}
        </select>
        <select value={selectedPitch} onChange={(e) => setSelectedPitch(e.target.value)}>
          <option value="" disabled>Select Pitch Type</option>
          {pitchTypes.map(pt => <option key={pt} value={pt}>{pt}</option>)}
        </select>
        <select value={selectedWeather} onChange={(e) => setSelectedWeather(e.target.value)}>
          <option value="" disabled>Select Weather</option>
          {weatherTypes.map(wt => <option key={wt} value={wt}>{wt}</option>)}
        </select>
        <select value={selectedMatchType} onChange={(e) => setSelectedMatchType(e.target.value)}>
          {matchTypes.map(mt => <option key={mt} value={mt}>{mt}</option>)}
        </select>
        <button onClick={handleSuggestTeam} disabled={isLoading}>{isLoading ? 'Analyzing...' : 'Suggest Best XI'}</button>
      </div>

      {error && <p className="error-message">{error}</p>}
      {isLoading && <div className="skeleton-loader team-loader"></div>}

      {suggestedTeam.length > 0 && !isLoading && (
        <div className="team-display-container">
          <div className="team-display-header">
            <h2>Suggested Playing XI</h2>
            <button className="add-player-btn" type="button" onClick={handleAddNewPlayer}>
              + Add Player
            </button>
          </div>
          {teamNotice && <p className="team-notice">{teamNotice}</p>}
          <ul className="team-list">
            {/* --- මෙතන තමයි UI එකේ වෙනස තියෙන්නේ --- */}
            {suggestedTeam.map((player, index) => (
              <li key={index}>
                <div className="team-card-info">
                  <span className="player-name">{player.name}</span>
                  <span className={`player-role ${getRoleClassName(player.role)}`}>
                    {player.role}
                  </span>
                </div>
                <div className="team-card-actions">
                  <button
                    type="button"
                    className="ghost-btn"
                    onClick={() => handleQuickEdit(player.name)}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="danger-btn"
                    onClick={() => handleQuickDelete(player.name)}
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <section className="player-pool-manager">
        <div className="player-pool-header">
          <div>
            <h2>Manage Player Pool</h2>
            <p>Add, edit or remove players used for the Best XI suggestion.</p>
          </div>
          <button className="refresh-btn" onClick={fetchPlayerPool} disabled={poolLoading}>
            {poolLoading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        <div className="player-pool-content single-column">
          <form className="player-form" ref={playerFormRef} onSubmit={handlePlayerSubmit}>
            <h3>{editingPlayerId ? 'Edit Player' : 'Add Player'}</h3>
            <label>
              Player Name
              <input
                type="text"
                name="player_name"
                placeholder="e.g. Kusal Mendis"
                value={playerForm.player_name}
                onChange={handlePlayerFormChange}
              />
            </label>
            <label>
              Player Type
              <select name="player_type" value={playerForm.player_type} onChange={handlePlayerFormChange}>
                <option value="" disabled>Select type</option>
                {ROLE_OPTIONS.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <label>
              Role (shown on card)
              <select name="role" value={playerForm.role} onChange={handlePlayerFormChange}>
                <option value="" disabled>Select role</option>
                {ROLE_OPTIONS.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <div className="form-actions">
              <button type="submit">{editingPlayerId ? 'Update Player' : 'Add Player'}</button>
              {editingPlayerId && (
                <button type="button" className="ghost-btn" onClick={resetPlayerForm}>Cancel</button>
              )}
              {editingPlayerId && (
                <button
                  type="button"
                  className="danger-btn"
                  onClick={() => handleDeletePlayer(editingPlayerId, editingPlayerOriginalName)}
                >
                  Delete from Dataset
                </button>
              )}
            </div>
            {poolFeedback.message && (
              <p className={`pool-feedback ${poolFeedback.type}`}>{poolFeedback.message}</p>
            )}
          </form>
        </div>
      </section>
    </div>
  );
}

export default BestXISelectionPage;