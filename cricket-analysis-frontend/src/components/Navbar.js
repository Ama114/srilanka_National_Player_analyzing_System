import React from 'react';
// import nav lonk
import { NavLink } from 'react-router-dom'; 
import '../styles/Navbar.css';
import { ReactComponent as CricketBallIcon } from '../assets/cricket-ball.svg';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <CricketBallIcon className="logo-icon" />
    
        <NavLink to="/">Criclyzing</NavLink>
      </div>
      <ul className="navbar-links">

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