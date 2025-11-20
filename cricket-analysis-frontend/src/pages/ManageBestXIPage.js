import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../styles/ManageBestXIPage.css';

const ROLE_OPTIONS = ['Batsman', 'Bowler', 'All-Rounder', 'Wicket Keeper'];
const TYPE_OPTIONS = ['Batsman', 'Bowler', 'All-Rounder', 'Wicket Keeper'];
const API_BASE_URL = 'http://127.0.0.1:5000/api';

function ManageBestXIPage() {
  const [players, setPlayers] = useState([]);
  const [formData, setFormData] = useState({
    player_name: '',
    player_type: '',
    role: ''
  });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchPlayers();
  }, []);

  const fetchPlayers = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.get(`${API_BASE_URL}/best-xi/players`);
      setPlayers(res.data);
    } catch (err) {
      console.error('Failed to load Best XI players', err);
      setError('Could not load players. Please check the backend server.');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({ player_name: '', player_type: '', role: '' });
    setEditingId(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    if (!formData.player_name || !formData.player_type || !formData.role) {
      setError('Please fill in player name, type and role.');
      setSaving(false);
      return;
    }

    try {
      if (editingId) {
        await axios.put(`${API_BASE_URL}/best-xi/players/${editingId}`, formData);
        setSuccess('Player updated successfully.');
      } else {
        await axios.post(`${API_BASE_URL}/best-xi/players`, formData);
        setSuccess('Player added successfully.');
      }
      resetForm();
      fetchPlayers();
    } catch (err) {
      console.error('Failed to save player', err);
      setError('Could not save player. Make sure the name is unique.');
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (player) => {
    setFormData({
      player_name: player.player_name,
      player_type: player.player_type,
      role: player.role
    });
    setEditingId(player.id);
    setSuccess('');
    setError('');
  };

  const handleDelete = async (playerId) => {
    const confirm = window.confirm('Remove this player from the Best XI pool?');
    if (!confirm) return;

    setError('');
    setSuccess('');

    try {
      await axios.delete(`${API_BASE_URL}/best-xi/players/${playerId}`);
      setSuccess('Player removed.');
      if (editingId === playerId) {
        resetForm();
      }
      fetchPlayers();
    } catch (err) {
      console.error('Failed to delete player', err);
      setError('Could not delete player.');
    }
  };

  return (
    <div className="manage-bestxi-container">
      <header>
        <h1>Manage Best XI Players</h1>
        <p>Any change you make here updates the Suggested XI instantly.</p>
      </header>

      <section className="manage-bestxi-panel">
        <h2>{editingId ? 'Edit Player' : 'Add Player'}</h2>
        <form onSubmit={handleSubmit} className="manage-bestxi-form">
          <div className="form-row">
            <label>Player Name</label>
            <input
              type="text"
              name="player_name"
              placeholder="e.g. Wanindu Hasaranga"
              value={formData.player_name}
              onChange={handleChange}
            />
          </div>

          <div className="form-row">
            <label>Player Type</label>
            <select name="player_type" value={formData.player_type} onChange={handleChange}>
              <option value="" disabled>Select Type</option>
              {TYPE_OPTIONS.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label>Role (displayed on card)</label>
            <select name="role" value={formData.role} onChange={handleChange}>
              <option value="" disabled>Select Role</option>
              {ROLE_OPTIONS.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>

          <div className="form-actions">
            <button type="submit" disabled={saving}>
              {saving ? 'Saving...' : editingId ? 'Update Player' : 'Add Player'}
            </button>
            {editingId && (
              <button type="button" className="ghost-btn" onClick={resetForm}>
                Cancel
              </button>
            )}
          </div>
        </form>
        {error && <p className="status error">{error}</p>}
        {success && <p className="status success">{success}</p>}
      </section>

      <section className="manage-bestxi-list">
        <div className="list-header">
          <h2>Current Player Pool</h2>
          <button className="refresh-btn" onClick={fetchPlayers} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        {loading ? (
          <div className="skeleton-table"></div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Role</th>
                <th className="actions-col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {players.length === 0 ? (
                <tr>
                  <td colSpan="4" className="empty-state">
                    No players in the database yet.
                  </td>
                </tr>
              ) : (
                players.map((player) => (
                  <tr key={player.id}>
                    <td>{player.player_name}</td>
                    <td>{player.player_type}</td>
                    <td>
                      <span className={`role-chip role-${player.role?.toLowerCase().replace(' ', '-')}`}>
                        {player.role}
                      </span>
                    </td>
                    <td className="actions-col">
                      <button className="ghost-btn" onClick={() => handleEdit(player)}>
                        Edit
                      </button>
                      <button className="danger-btn" onClick={() => handleDelete(player.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}

export default ManageBestXIPage;

