import React from 'react';
import '../styles/FeaturedPlayers.css';

// ක්‍රීඩකයන්ගේ photos import කරගන්න
import waninduImg from '../assets/images/wanindu.jpg';
import matheeshaImg from '../assets/images/pathum.jpg';
import sadeeraImg from '../assets/images/sadeera.jpg';

function FeaturedPlayers() {
  return (
    <section className="featured-players-section">
      <h2>Featured Players</h2>
      <div className="player-cards-container">
        {/* Player Card 1 */}
        <div className="player-card">
          <img src={waninduImg} alt="Wanindu Hasaranga" className="player-image" />
          <h3>Wanindu Hasaranga</h3>
          <p>All-Rounder</p>
        </div>
        
        {/* Player Card 2 */}
        <div className="player-card">
          <img src={matheeshaImg} alt="Pathum Nissanka" className="player-image" />
          <h3>Pathum Nissanka</h3>
          <p>Batsman</p>
        </div>

        {/* Player Card 3 */}
        <div className="player-card">
          <img src={sadeeraImg} alt="Sadeera Samarawickrama" className="player-image" />
          <h3>Sadeera Samarawickrama</h3>
          <p>Batsman</p>
        </div>
      </div>
    </section>
  );
}

export default FeaturedPlayers;