import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import '../styles/BestXISelectionPage.css';

function BestXISelectionPage() {
  const [oppositions, setOppositions] = useState([]);
  const [pitchTypes, setPitchTypes] = useState(['Batting Friendly', 'Bowling Friendly', 'Spin Friendly', 'Balanced']);
  const [playerPool, setPlayerPool] = useState([]);

  const ROLE_OPTIONS = ['Batsman', 'Bowler', 'All-Rounder', 'Wicket Keeper'];

  const [selectedOpposition, setSelectedOpposition] = useState('');
  const [selectedPitch, setSelectedPitch] = useState('');
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
  
  const API_BASE_URL = 'http://127.0.0.1:5000/api';

  useEffect(() => {
    let isMounted = true;
    fetchPlayerPool();
    
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
    
    return () => {
      isMounted = false;
    };
  }, []);

  const buildTeamWithFallbacks = (team) => {
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
  };

  const applyTeamWithFallbacks = (team, options = {}) => {
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
  };

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
  }, [playerPool]);

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

  const handleSuggestTeam = () => {
    if (!selectedOpposition || !selectedPitch) {
      setError('Please select both opposition and pitch.');
      return;
    }
    setError('');
    setIsLoading(true);
    setTeamNotice('');
    setSuggestedTeam([]);

    const params = {
      opposition: selectedOpposition,
      pitch: selectedPitch
    };
    
    axios.get(`${API_BASE_URL}/suggest-best-xi`, { params })
      .then(response => {
        const enrichedTeam = response.data.map(player => {
          const poolPlayer = playerPool.find(p => p.player_name === player.name);
          return {
            id: poolPlayer?.id || null,
            name: player.name,
            role: player.role
          };
        });
        setSuggestedTeam(applyTeamWithFallbacks(enrichedTeam));
        setError(''); // Clear any previous errors
      })
      .catch(err => {
        console.error("Error fetching team suggestion:", err);
        if (err.message === 'Network Error' || err.code === 'ERR_NETWORK') {
          setError("Cannot connect to backend server. Please make sure Flask backend is running on port 5000.");
        } else {
          setError("Could not suggest a team. Please check the backend server.");
        }
      })
      .finally(() => {
        setIsLoading(false);
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
      
      <div className="condition-selector">
        {/* ... (Dropdowns and button have no changes) ... */}
        <select value={selectedOpposition} onChange={(e) => setSelectedOpposition(e.target.value)}><option value="" disabled>Select Opposition</option>{oppositions.map(opp => <option key={opp} value={opp}>{opp}</option>)}</select>
        <select value={selectedPitch} onChange={(e) => setSelectedPitch(e.target.value)}><option value="" disabled>Select Pitch Type</option>{pitchTypes.map(pt => <option key={pt} value={pt}>{pt}</option>)}</select>
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