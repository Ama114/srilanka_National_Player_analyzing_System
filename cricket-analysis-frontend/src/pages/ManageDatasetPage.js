import React, { useState } from 'react';
import axios from 'axios';
import '../styles/ManageDatasetPage.css';

function ManageDatasetPage() {
  const [pitchTypes] = useState(['Batting Friendly', 'Bowling Friendly', 'Spin Friendly', 'Balanced']);
  const ROLE_OPTIONS = ['Batsman', 'Bowler', 'All-Rounder', 'Wicket Keeper'];

  const [datasetForm, setDatasetForm] = useState({
    Player_Name: '',
    Player_Type: 'Batsman',
    Role: 'Batsman',
    Opponent_Team: '',
    Pitch_Type: '',
    Weather: 'Balanced',
    Runs: 0,
    Balls_Faced: 0,
    Strike_Rate: 0,
    Wickets_Taken: 0,
    Overs_Bowled: 0,
    Runs_Conceded: 0
  });
  const [datasetFeedback, setDatasetFeedback] = useState({ type: '', message: '' });
  const [conditionExists, setConditionExists] = useState(null);
  const [checkingCondition, setCheckingCondition] = useState(false);
  
  const API_BASE_URL = 'http://127.0.0.1:5000/api';

  const handleDatasetFormChange = (e) => {
    const { name, value } = e.target;
    setDatasetForm(prev => {
      const updated = { ...prev, [name]: value };
      if (name === 'Player_Type' && !prev.Role) {
        updated.Role = value;
      }
      return updated;
    });
  };

  const checkCondition = async () => {
    if (!datasetForm.Player_Name || !datasetForm.Opponent_Team || !datasetForm.Pitch_Type || !datasetForm.Weather) {
      setDatasetFeedback({ type: 'error', message: 'Please fill Player Name, Opponent Team, Pitch Type, and Weather.' });
      return;
    }

    setCheckingCondition(true);
    setDatasetFeedback({ type: '', message: '' });
    try {
      const res = await axios.get(`${API_BASE_URL}/dataset/check-condition`, {
        params: {
          player_name: datasetForm.Player_Name,
          opposition: datasetForm.Opponent_Team,
          pitch: datasetForm.Pitch_Type,
          weather: datasetForm.Weather
        }
      });
      setConditionExists(res.data.exists);
      if (res.data.exists) {
        setDatasetFeedback({ type: 'info', message: 'This condition already exists. You can update it below.' });
      } else {
        setDatasetFeedback({ type: 'info', message: 'This condition does not exist. You can add it below.' });
      }
    } catch (err) {
      console.error("Error checking condition:", err);
      setDatasetFeedback({ type: 'error', message: 'Failed to check condition.' });
    } finally {
      setCheckingCondition(false);
    }
  };

  const handleDatasetSubmit = async (e) => {
    e.preventDefault();
    setDatasetFeedback({ type: '', message: '' });

    if (!datasetForm.Player_Name || !datasetForm.Opponent_Team || !datasetForm.Pitch_Type || !datasetForm.Weather) {
      setDatasetFeedback({ type: 'error', message: 'Please fill all required fields.' });
      return;
    }

    try {
      if (conditionExists) {
        // Update existing record
        await axios.put(`${API_BASE_URL}/dataset/update-record`, datasetForm);
        setDatasetFeedback({ type: 'success', message: 'Record updated successfully in CSV dataset!' });
      } else {
        // Add new record
        await axios.post(`${API_BASE_URL}/dataset/add-record`, datasetForm);
        setDatasetFeedback({ type: 'success', message: 'Record added successfully to CSV dataset!' });
        setConditionExists(true);
      }
      
      // Reload dataset
      await axios.post(`${API_BASE_URL}/dataset/reload`);
      
      // Reset form
      setDatasetForm({
        Player_Name: '',
        Player_Type: 'Batsman',
        Role: 'Batsman',
        Opponent_Team: '',
        Pitch_Type: '',
        Weather: 'Balanced',
        Runs: 0,
        Balls_Faced: 0,
        Strike_Rate: 0,
        Wickets_Taken: 0,
        Overs_Bowled: 0,
        Runs_Conceded: 0
      });
      setConditionExists(null);
    } catch (err) {
      console.error("Error saving dataset record:", err);
      setDatasetFeedback({ type: 'error', message: 'Failed to save record. ' + (err.response?.data?.error || err.message) });
    }
  };

  return (
    <div className="manage-dataset-container">
      <div className="manage-dataset-header">
        <h1>Manage CSV Dataset</h1>
        <p className="subtitle">Add or update player performance data for specific conditions (Opposition, Pitch, Weather).</p>
      </div>

      <section className="dataset-manager">
        <div className="dataset-content">
          <form className="dataset-form" onSubmit={handleDatasetSubmit}>
            <h3>Add/Update Dataset Record</h3>
            
            <div className="form-row-group">
              <label>
                Player Name *
                <input
                  type="text"
                  name="Player_Name"
                  placeholder="e.g. Pathum Nissanka"
                  value={datasetForm.Player_Name}
                  onChange={handleDatasetFormChange}
                  required
                />
              </label>
              <label>
                Player Type *
                <select name="Player_Type" value={datasetForm.Player_Type} onChange={handleDatasetFormChange} required>
                  {ROLE_OPTIONS.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </label>
              <label>
                Role
                <select name="Role" value={datasetForm.Role} onChange={handleDatasetFormChange}>
                  {ROLE_OPTIONS.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </label>
            </div>

            <div className="form-row-group">
              <label>
                Opponent Team *
                <input
                  type="text"
                  name="Opponent_Team"
                  placeholder="e.g. India"
                  value={datasetForm.Opponent_Team}
                  onChange={handleDatasetFormChange}
                  required
                />
              </label>
              <label>
                Pitch Type *
                <select name="Pitch_Type" value={datasetForm.Pitch_Type} onChange={handleDatasetFormChange} required>
                  <option value="" disabled>Select Pitch</option>
                  {pitchTypes.map(pt => (
                    <option key={pt} value={pt}>{pt}</option>
                  ))}
                </select>
              </label>
              <label>
                Weather *
                <select name="Weather" value={datasetForm.Weather} onChange={handleDatasetFormChange} required>
                  <option value="Balanced">Balanced</option>
                  <option value="Cloudy">Cloudy</option>
                  <option value="Dry">Dry</option>
                  <option value="Hot">Hot</option>
                  <option value="Rainy">Rainy</option>
                </select>
              </label>
            </div>

            <div className="form-row-group">
              <label>
                Runs
                <input
                  type="number"
                  name="Runs"
                  value={datasetForm.Runs}
                  onChange={handleDatasetFormChange}
                  min="0"
                />
              </label>
              <label>
                Balls Faced
                <input
                  type="number"
                  name="Balls_Faced"
                  value={datasetForm.Balls_Faced}
                  onChange={handleDatasetFormChange}
                  min="0"
                />
              </label>
              <label>
                Strike Rate
                <input
                  type="number"
                  name="Strike_Rate"
                  value={datasetForm.Strike_Rate}
                  onChange={handleDatasetFormChange}
                  min="0"
                  step="0.01"
                />
              </label>
            </div>

            <div className="form-row-group">
              <label>
                Wickets Taken
                <input
                  type="number"
                  name="Wickets_Taken"
                  value={datasetForm.Wickets_Taken}
                  onChange={handleDatasetFormChange}
                  min="0"
                />
              </label>
              <label>
                Overs Bowled
                <input
                  type="number"
                  name="Overs_Bowled"
                  value={datasetForm.Overs_Bowled}
                  onChange={handleDatasetFormChange}
                  min="0"
                  step="0.1"
                />
              </label>
              <label>
                Runs Conceded
                <input
                  type="number"
                  name="Runs_Conceded"
                  value={datasetForm.Runs_Conceded}
                  onChange={handleDatasetFormChange}
                  min="0"
                />
              </label>
            </div>

            <div className="form-actions">
              <button type="button" className="ghost-btn" onClick={checkCondition} disabled={checkingCondition}>
                {checkingCondition ? 'Checking...' : 'Check if Exists'}
              </button>
              <button type="submit">
                {conditionExists ? 'Update Record' : 'Add Record'}
              </button>
            </div>

            {conditionExists !== null && (
              <p className={`condition-status ${conditionExists ? 'exists' : 'not-exists'}`}>
                {conditionExists ? '✓ Condition exists in dataset' : '✗ Condition does not exist'}
              </p>
            )}

            {datasetFeedback.message && (
              <p className={`pool-feedback ${datasetFeedback.type}`}>{datasetFeedback.message}</p>
            )}
          </form>
        </div>
      </section>
    </div>
  );
}

export default ManageDatasetPage;

