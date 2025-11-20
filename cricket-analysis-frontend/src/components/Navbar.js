import React from 'react';
// 'Link' වෙනුවට 'NavLink' import කරගන්නවා
import { NavLink } from 'react-router-dom'; 
import '../styles/Navbar.css';
import { ReactComponent as CricketBallIcon } from '../assets/cricket-ball.svg';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <CricketBallIcon className="logo-icon" />
        {/* Logo එකටත් NavLink එකක් දාන එක හොඳයි */}
        <NavLink to="/">SL Cricket Stats</NavLink>
      </div>
      <ul className="navbar-links">
        {/* හැම 'Link' එකක්ම 'NavLink' බවට පත්කරලා, activeClassName එක දානවා */}
        <li><NavLink to="/" activeClassName="active" exact>Home</NavLink></li>
        <li><NavLink to="/bowling-performance" activeClassName="active">Bowling Stats</NavLink></li>
        <li><NavLink to="/batting-performance" activeClassName="active">Batting Stats</NavLink></li>
        <li><NavLink to="/best-11-suggestion" activeClassName="active">Best XI</NavLink></li>
        <li><NavLink to="/manage-dataset" activeClassName="active">Manage Dataset</NavLink></li>

        <li><NavLink to="/about" activeClassName="active">About</NavLink></li>
      </ul>
    </nav>
  );
}

export default Navbar;