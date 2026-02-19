import React from 'react';
import '../styles/Footer.css';

function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-content">
        <div className="footer-section about">
          <h3>SL Cricket Stats</h3>
          <p>
            The ultimate platform for analyzing Sri Lanka's national player statistics.
            Empowering fans and analysts with data-driven insights.
          </p>
        </div>
        <div className="footer-section links">
          <h3>Quick Links</h3>
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/batting-performance">Batting Stats</a></li>
            <li><a href="/bowling-performance">Bowling Stats</a></li>
            <li><a href="/best-11-suggestion">Best XI Tool</a></li>
          </ul>
        </div>
        <div className="footer-section contact">
            <h3>Contact Us</h3>
            <p>Email: info@slcricketstats.lk</p>
            <p>Phone: +94 11 234 5678</p>
        </div>
      </div>
      <div className="footer-bottom">
        <p>&copy; 2025 SL Cricket Stats. A Final Year Project. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;