import React, { useState } from 'react';
import axios from 'axios';
import '../styles/ManageDatasetPage.css';

function ManageDatasetPage() {
  const [pitchTypes] = useState(['Batting Friendly', 'Bowling Friendly', 'Spin Friendly', 'Balanced', 'Dusty', 'Green', 'Dry']);
  const ROLE_OPTIONS = ['Batsman', 'Bowler', 'All-Rounder', 'Wicket Keeper'];
  const WEATHER_OPTIONS = ['Balanced', 'Sunny', 'Cloudy', 'Overcast', 'Rainy', 'Dry', 'Hot'];

  const [matchType, setMatchType] = useState('ODI');

  // Backend එකේ Models වලට ගැලපෙන විදියට Initial State එක
  const initialFormState = {
    date: '',
    ground: '',
    player_name: '',
    main_role: 'Batsman',
    batting_style: 'Right Hand Bat',
    bowling_style: 'Right Arm Fast',
    opposition: '',
    pitch_type: 'Balanced',
    weather: 'Balanced',
    
    // Batting (Format Specific)
    batting_runs: 0, bf: 0, sr: 0.0,            // ODI
    runs: 0, balls_faced: 0, strike_rate: 0.0, average: 0.0, // T20 & TEST
    fours: 0, sixes: 0, bat_position: 1, dismissal: 'Not Out',

    // Bowling (Format Specific)
    overs: 0.0, mdns: 0, econ: 0.0, wicket_taken: 0, // ODI
    wickets: 0, maidens: 0, economy: 0.0,           // T20 & TEST
    runs_conceded: 0, bowling_pos: 0, notes: ''
  };

  const [datasetForm, setDatasetForm] = useState(initialFormState);
  const [datasetFeedback, setDatasetFeedback] = useState({ type: '', message: '' });
  const [conditionExists, setConditionExists] = useState(null);
  const [checkingCondition, setCheckingCondition] = useState(false);
  
  const API_BASE_URL = 'http://127.0.0.1:5000/api';

  const handleDatasetFormChange = (e) => {
    const { name, value } = e.target;
    setDatasetForm(prev => ({ ...prev, [name]: value }));
  };

  const checkCondition = async () => {
    if (!datasetForm.player_name || !datasetForm.opposition) {
      setDatasetFeedback({ type: 'error', message: 'Please fill Player Name and Opposition.' });
      return;
    }
    setCheckingCondition(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/dataset/check-condition`, {
        params: {
          player_name: datasetForm.player_name,
          opposition: datasetForm.opposition,
          match_type: matchType
        }
      });
      setConditionExists(res.data.exists);
      setDatasetFeedback({ 
        type: 'info', 
        message: res.data.exists ? 'Record exists. Ready to Update.' : 'New entry. Ready to Save.' 
      });
    } catch (err) {
      setDatasetFeedback({ type: 'error', message: 'Failed to check condition.' });
    } finally {
      setCheckingCondition(false);
    }
  };

  const handleDatasetSubmit = async (e) => {
    e.preventDefault();
    setDatasetFeedback({ type: '', message: '' });

    if (!datasetForm.player_name || !datasetForm.opposition || !datasetForm.date || !datasetForm.ground) {
      setDatasetFeedback({ type: 'error', message: 'Please fill required fields (*).' });
      return;
    }

    try {
      const payload = { ...datasetForm, match_type: matchType };
      
      if (conditionExists) {
        // UPDATE Logic
        await axios.put(`${API_BASE_URL}/dataset/update-record`, payload);
        setDatasetFeedback({ type: 'success', message: `${matchType} Record updated successfully!` });
      } else {
        // ADD Logic
        await axios.post(`${API_BASE_URL}/dataset/add-record`, payload);
        setDatasetFeedback({ type: 'success', message: `New ${matchType} Record added!` });
      }
      
      // Reset Form
      setDatasetForm({ ...initialFormState, date: datasetForm.date, ground: datasetForm.ground });
      setConditionExists(null);
    } catch (err) {
      setDatasetFeedback({ type: 'error', message: 'Error: ' + (err.response?.data?.error || err.message) });
    }
  };

  return (
    <div className="manage-dataset-container">
      <div className="manage-dataset-header">
        <h1>Manage Cricket Dataset</h1>
        <div className="match-type-toggle">
          {['ODI', 'T20', 'TEST'].map((type) => (
            <button 
              key={type}
              className={matchType === type ? 'active' : ''} 
              onClick={() => {setMatchType(type); setConditionExists(null);}}
            >
              {type} Format
            </button>
          ))}
        </div>
      </div>

      <section className="dataset-manager">
        <form className="dataset-form" onSubmit={handleDatasetSubmit}>
          
          {/* --- SECTION 1: MATCH INFO --- */}
          <h4>Match Information ({matchType})</h4>
          <div className="form-row-group">
            <label>Date * <input type="date" name="date" value={datasetForm.date} onChange={handleDatasetFormChange} required /></label>
            <label>Opposition * <input type="text" name="opposition" placeholder="e.g. India" value={datasetForm.opposition} onChange={handleDatasetFormChange} required /></label>
            <label>Ground * <input type="text" name="ground" placeholder="e.g. Colombo" value={datasetForm.ground} onChange={handleDatasetFormChange} required /></label>
          </div>

          <div className="form-row-group">
            <label>Pitch Type
              <select name="pitch_type" value={datasetForm.pitch_type} onChange={handleDatasetFormChange}>
                {pitchTypes.map(pt => <option key={pt} value={pt}>{pt}</option>)}
              </select>
            </label>
            <label>Weather
              <select name="weather" value={datasetForm.weather} onChange={handleDatasetFormChange}>
                {WEATHER_OPTIONS.map(w => <option key={w} value={w}>{w}</option>)}
              </select>
            </label>
          </div>

          {/* --- SECTION 2: PLAYER INFO --- */}
          <h4>Player Details</h4>
          <div className="form-row-group">
            <label>Player Name * <input type="text" name="player_name" value={datasetForm.player_name} onChange={handleDatasetFormChange} required /></label>
            <label>Role <select name="main_role" value={datasetForm.main_role} onChange={handleDatasetFormChange}>{ROLE_OPTIONS.map(opt => <option key={opt}>{opt}</option>)}</select></label>
            <label>Batting Style
              <select name="batting_style" value={datasetForm.batting_style} onChange={handleDatasetFormChange}>
                <option value="Right Hand Bat">Right Hand Bat</option>
                <option value="Left Hand Bat">Left Hand Bat</option>
              </select>
            </label>
          </div>

          {/* --- SECTION 3: BATTING STATS --- */}
          <h4 style={{color: '#007bff'}}>Batting Stats ({matchType})</h4>
          <div className="form-row-group">
            {matchType === 'ODI' ? (
              <>
                <label>Runs <input type="number" name="batting_runs" value={datasetForm.batting_runs} onChange={handleDatasetFormChange} /></label>
                <label>Balls (BF) <input type="number" name="bf" value={datasetForm.bf} onChange={handleDatasetFormChange} /></label>
                <label>SR <input type="number" step="0.01" name="sr" value={datasetForm.sr} onChange={handleDatasetFormChange} /></label>
              </>
            ) : (
              <>
                <label>Runs <input type="number" name="runs" value={datasetForm.runs} onChange={handleDatasetFormChange} /></label>
                <label>Balls faced <input type="number" name="balls_faced" value={datasetForm.balls_faced} onChange={handleDatasetFormChange} /></label>
                <label>Strike Rate <input type="number" step="0.01" name="strike_rate" value={datasetForm.strike_rate} onChange={handleDatasetFormChange} /></label>
                <label>Average <input type="number" step="0.01" name="average" value={datasetForm.average} onChange={handleDatasetFormChange} /></label>
              </>
            )}
            <label>4s <input type="number" name="fours" value={datasetForm.fours} onChange={handleDatasetFormChange} /></label>
            <label>6s <input type="number" name="sixes" value={datasetForm.sixes} onChange={handleDatasetFormChange} /></label>
            <label>Position <input type="number" name="bat_position" value={datasetForm.bat_position} onChange={handleDatasetFormChange} /></label>
            <label>Dismissal <input type="text" name="dismissal" value={datasetForm.dismissal} onChange={handleDatasetFormChange} /></label>
          </div>

          {/* --- SECTION 4: BOWLING STATS --- */}
          <h4 style={{color: '#28a745'}}>Bowling Stats ({matchType})</h4>
          <div className="form-row-group">
            <label>Overs <input type="number" step="0.1" name="overs" value={datasetForm.overs} onChange={handleDatasetFormChange} /></label>
            {matchType === 'ODI' ? (
              <>
                <label>Maidens <input type="number" name="mdns" value={datasetForm.mdns} onChange={handleDatasetFormChange} /></label>
                <label>Wickets <input type="number" name="wicket_taken" value={datasetForm.wicket_taken} onChange={handleDatasetFormChange} /></label>
                <label>Economy <input type="number" step="0.01" name="econ" value={datasetForm.econ} onChange={handleDatasetFormChange} /></label>
              </>
            ) : (
              <>
                <label>Maidens <input type="number" name="maidens" value={datasetForm.maidens} onChange={handleDatasetFormChange} /></label>
                <label>Wickets <input type="number" name="wickets" value={datasetForm.wickets} onChange={handleDatasetFormChange} /></label>
                <label>Economy <input type="number" step="0.01" name="economy" value={datasetForm.economy} onChange={handleDatasetFormChange} /></label>
              </>
            )}
            <label>Runs Conc. <input type="number" name="runs_conceded" value={datasetForm.runs_conceded} onChange={handleDatasetFormChange} /></label>
            <label>Bowling Pos <input type="number" name="bowling_pos" value={datasetForm.bowling_pos} onChange={handleDatasetFormChange} /></label>
          </div>

          {(matchType === 'T20' || matchType === 'TEST') && (
            <div className="form-row-group" style={{marginTop: '10px'}}>
              <label style={{width: '100%'}}>Notes <textarea name="notes" value={datasetForm.notes} onChange={handleDatasetFormChange} placeholder={`${matchType} match notes...`}></textarea></label>
            </div>
          )}

          <div className="form-actions">
            <button type="button" className="ghost-btn" onClick={checkCondition} disabled={checkingCondition}>
              {checkingCondition ? 'Checking...' : 'Check Existence'}
            </button>
            <button type="submit" className="primary-btn">
              {conditionExists ? `Update ${matchType} Record` : `Save New ${matchType} Record`}
            </button>
          </div>

          {datasetFeedback.message && (
            <p className={`pool-feedback ${datasetFeedback.type}`}>{datasetFeedback.message}</p>
          )}
        </form>
      </section>
    </div>
  );
}

export default ManageDatasetPage;