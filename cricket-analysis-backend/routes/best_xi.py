from flask import Blueprint, jsonify, request
from models import db, BestXIPlayer, GeneratedBestXITeam, ODIPerformance
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
import data_loader
import pandas as pd
import json

best_xi_bp = Blueprint('best_xi', __name__)

# --- Dropdowns ---
@best_xi_bp.route('/api/all-grounds', methods=['GET'])
def get_all_grounds():
    # Use database only
    try:
        grounds = db.session.query(ODIPerformance.ground).distinct().all()
        grounds_list = sorted([g[0] for g in grounds if g[0]])
        return jsonify(grounds_list)
    except Exception as e:
        print(f"Error fetching grounds from database: {e}")
        return jsonify({"error": "Database error occurred"}), 500

@best_xi_bp.route('/api/ml/oppositions', methods=['GET'])
def get_ml_oppositions():
    # Use database only
    try:
        oppositions = db.session.query(ODIPerformance.opposition).distinct().all()
        opp_list = sorted([o[0] for o in oppositions if o[0]])
        return jsonify(opp_list)
    except Exception as e:
        print(f"Error fetching oppositions from database: {e}")
        # Fallback to CSV
        try:
            df = data_loader.df_players_ml
            if not df.empty:
                col_name = next((name for name in ['Opponent_Team', 'opposition'] if name in df.columns), None)
                if col_name:
                    opp_list = sorted([str(o).strip() for o in df[col_name].dropna().unique().tolist() if o])
                    return jsonify(opp_list)
        except:
            pass
        return jsonify([])

@best_xi_bp.route('/api/ml/weather-types', methods=['GET'])
def get_ml_weather_types():
    # Try CSV first (weather not in odi_performance table)
    try:
        df = data_loader.df_players_ml
        if not df.empty:
            col_name = next((name for name in ['Weather', 'weather'] if name in df.columns), None)
            if col_name:
                weather_list = sorted([str(w).strip() for w in df[col_name].dropna().unique().tolist() if w])
                if weather_list:
                    return jsonify(weather_list)
        return jsonify([])
    except Exception as e:
        print(f"Error fetching weather types: {e}")
        return jsonify([])

# --- ODI Performance Routes ---
@best_xi_bp.route('/api/odi-performance', methods=['GET'])
def get_odi_performance():
    """Get ODI performance data from database"""
    player_name = request.args.get('player')
    opposition = request.args.get('opposition')
    ground = request.args.get('ground')
    
    query = ODIPerformance.query
    
    if player_name:
        query = query.filter(ODIPerformance.player_name == player_name)
    if opposition:
        query = query.filter(ODIPerformance.opposition == opposition)
    if ground:
        query = query.filter(ODIPerformance.ground == ground)
    
    try:
        performances = query.all()
        return jsonify([p.to_dict() for p in performances])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@best_xi_bp.route('/api/odi-performance/stats', methods=['GET'])
def get_odi_performance_stats():
    """Get aggregated ODI performance stats by player"""
    player_name = request.args.get('player')
    opposition = request.args.get('opposition')
    
    if not player_name:
        return jsonify({"error": "player parameter required"}), 400
    
    query = ODIPerformance.query.filter(ODIPerformance.player_name == player_name)
    
    if opposition:
        query = query.filter(ODIPerformance.opposition == opposition)
    
    try:
        performances = query.all()
        
        if not performances:
            return jsonify({"message": "No performance data found"})
        
        # Aggregate stats
        total_matches = sum(p.matches for p in performances)
        total_runs = sum(p.runs for p in performances)
        total_wickets = sum(p.wickets for p in performances)
        avg_strike_rate = sum(p.strike_rate for p in performances) / len(performances) if performances else 0
        avg_batting_avg = sum(p.average for p in performances) / len(performances) if performances else 0
        avg_economy = sum(p.economy for p in performances) / len(performances) if performances else 0
        
        grounds_played = [p.ground for p in performances]
        oppositions_played = [p.opposition for p in performances]
        
        stats = {
            "player_name": player_name,
            "total_matches": total_matches,
            "total_runs": total_runs,
            "total_wickets": total_wickets,
            "average_strike_rate": round(avg_strike_rate, 2),
            "average_batting_avg": round(avg_batting_avg, 2),
            "average_economy": round(avg_economy, 2),
            "grounds_played": sorted(list(set(grounds_played))),
            "oppositions_played": sorted(list(set(oppositions_played))),
            "performance_records": len(performances)
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- CRUD for Best XI ---
@best_xi_bp.route('/api/best-xi/players', methods=['GET'])
def list_best_xi_players():
    players = BestXIPlayer.query.order_by(BestXIPlayer.player_name).all()
    return jsonify([player.to_dict() for player in players])

@best_xi_bp.route('/api/best-xi/players', methods=['POST'])
def create_best_xi_player():
    data = request.get_json() or {}
    if not all(k in data for k in ['player_name', 'player_type', 'role']):
        return jsonify({"error": "Missing fields"}), 400

    try:
        player = BestXIPlayer(
            player_name=data['player_name'],
            player_type=data['player_type'],
            role=data['role']
        )
        db.session.add(player)
        db.session.commit()
        return jsonify(player.to_dict()), 201
    except SQLAlchemyError as err:
        db.session.rollback()
        return jsonify({"error": str(err)}), 500

@best_xi_bp.route('/api/best-xi/players/<int:player_id>', methods=['PUT'])
def update_best_xi_player(player_id):
    data = request.get_json() or {}
    player = BestXIPlayer.query.get_or_404(player_id)
    for field in ['player_name', 'player_type', 'role']:
        if field in data: setattr(player, field, data[field])
    try:
        db.session.commit()
        return jsonify(player.to_dict())
    except SQLAlchemyError as err:
        db.session.rollback()
        return jsonify({"error": str(err)}), 500

@best_xi_bp.route('/api/best-xi/players/<int:player_id>', methods=['DELETE'])
def delete_best_xi_player(player_id):
    player = BestXIPlayer.query.get_or_404(player_id)
    try:
        db.session.delete(player)
        db.session.commit()
        return jsonify({"message": "Player removed"})
    except SQLAlchemyError as err:
        db.session.rollback()
        return jsonify({"error": str(err)}), 500

# --- Generated Teams Management ---
@best_xi_bp.route('/api/best-xi/generated-teams', methods=['GET'])
def list_generated_teams():
    """Get all generated teams, ordered by most recent first"""
    try:
        teams = GeneratedBestXITeam.query.order_by(GeneratedBestXITeam.created_at.desc()).limit(10).all()
        return jsonify([team.to_dict() for team in teams]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@best_xi_bp.route('/api/best-xi/generated-teams/<int:team_id>', methods=['GET'])
def get_generated_team(team_id):
    """Get a specific generated team"""
    try:
        team = GeneratedBestXITeam.query.get_or_404(team_id)
        return jsonify(team.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@best_xi_bp.route('/api/best-xi/generated-teams/<int:team_id>', methods=['DELETE'])
def delete_generated_team(team_id):
    """Delete a generated team"""
    try:
        team = GeneratedBestXITeam.query.get_or_404(team_id)
        db.session.delete(team)
        db.session.commit()
        return jsonify({"message": "Team deleted successfully"}), 200
    except SQLAlchemyError as err:
        db.session.rollback()
        return jsonify({"error": str(err)}), 500

# --- Prediction Logic ---
@best_xi_bp.route('/api/best-xi/generate', methods=['GET'])
def generate_best_xi():
    """Generate Best XI based on match conditions - works with ODI, T20, Test"""
    opposition = request.args.get('opposition')
    pitch_type = request.args.get('pitch_type')
    weather = request.args.get('weather')
    match_type = request.args.get('match_type', 'ODI').upper()
    
    if not all([opposition, pitch_type, weather]):
        return jsonify({"error": "Missing parameters: opposition, pitch_type, weather"}), 400
    
    # Map match type to database model
    from models import ODIPerformance, T20Performance, TestPerformance
    match_models = {
        'ODI': ODIPerformance,
        'TEST': TestPerformance,
        'T20': T20Performance
    }
    
    if match_type not in match_models:
        return jsonify({"error": f"Invalid match type. Use ODI, TEST, or T20"}), 400
    
    try:
        model_class = match_models[match_type]
        
        # Get all unique players with their roles from the selected match type
        players_query = db.session.query(
            model_class.player_name, 
            model_class.main_role,
            model_class.runs,
            model_class.wickets
        ).distinct(model_class.player_name).all()
        
        if not players_query:
            return jsonify({"error": f"No players found for {match_type} matches"}), 404
        
        # Classify players by role
        keepers = []
        batsmen = []
        all_rounders = []
        bowlers = []
        processed_players = set()  # Track which players we've already classified
        
        # Known player role mappings
        KNOWN_KEEPERS = {
            'Kusal Mendis', 'Sadeera Samarawickrama', 'Kusal Janith Perera',
            'kusal_mendis', 'sadeera_samarawickrama', 'kusal_janith_perera'
        }
        
        KNOWN_ALL_ROUNDERS = {
            'Wanindu Hasaranga', 'Dhananjaya de Silva', 'Dasun Shanaka',
            'Dunith Wellalage', 'Chamika Karunaratne', 'Charith Asalanka', 
            'Janith Liyanage', 'Angelo Mathews', 'Anjelo Mathews',
            'wanindu_hasaranga', 'dhananjaya_de_silva', 'dasun_shanaka',
            'dunith_wellalage', 'chamika_karunaratne', 'charith_asalanka',
            'janith_liyanage', 'angelo_mathews', 'anjelo_mathews'
        }
        
        # Process each player
        for player_name, main_role, runs, wickets in players_query:
            # Skip if we've already processed this player
            if player_name in processed_players:
                continue
            processed_players.add(player_name)
            
            player_info = {
                'player_name': player_name,
                'player_type': 'Batsman',
                'role': 'Batsman'
            }
            
            # Determine role based on main_role field, known mappings, and performance
            if player_name in KNOWN_KEEPERS:
                player_info['role'] = 'Wicket Keeper'
                player_info['player_type'] = 'Wicket Keeper'
                keepers.append(player_info)
            elif player_name in KNOWN_ALL_ROUNDERS:
                player_info['role'] = 'All-Rounder'
                player_info['player_type'] = 'All-Rounder'
                all_rounders.append(player_info)
            elif main_role:
                # Try to parse main_role
                role_lower = str(main_role).lower()
                if 'keeper' in role_lower or 'wicket' in role_lower:
                    player_info['role'] = 'Wicket Keeper'
                    player_info['player_type'] = 'Wicket Keeper'
                    keepers.append(player_info)
                elif 'allrounder' in role_lower or 'all-rounder' in role_lower or 'all_rounder' in role_lower:
                    player_info['role'] = 'All-Rounder'
                    player_info['player_type'] = 'All-Rounder'
                    all_rounders.append(player_info)
                elif 'bowler' in role_lower or 'bowling' in role_lower:
                    player_info['role'] = 'Bowler'
                    player_info['player_type'] = 'Bowler'
                    bowlers.append(player_info)
                else:
                    player_info['role'] = 'Batsman'
                    player_info['player_type'] = 'Batsman'
                    batsmen.append(player_info)
            else:
                # If no main_role, infer from performance stats
                if wickets and int(wickets) > 0 and runs and int(runs) > 0:
                    # Both batting and bowling stats = all-rounder
                    player_info['role'] = 'All-Rounder'
                    player_info['player_type'] = 'All-Rounder'
                    all_rounders.append(player_info)
                elif wickets and int(wickets) > 0:
                    # Mostly bowling stats = bowler
                    player_info['role'] = 'Bowler'
                    player_info['player_type'] = 'Bowler'
                    bowlers.append(player_info)
                else:
                    # Default = batsman
                    player_info['role'] = 'Batsman'
                    player_info['player_type'] = 'Batsman'
                    batsmen.append(player_info)
        
        # Build team with proper composition: 1 WK, 5 Batsmen, 3 All-rounders, 3 Bowlers
        all_players_by_role = {
            'Wicket Keeper': keepers,
            'Batsman': batsmen,
            'All-Rounder': all_rounders,
            'Bowler': bowlers
        }
        
        team = []
        added_names = set()
        
        # Add players in order of role priority
        role_order = ['Wicket Keeper', 'Batsman', 'All-Rounder', 'Bowler']
        role_needed = {
            'Wicket Keeper': 1,
            'Batsman': 4,
            'All-Rounder': 3,
            'Bowler': 3
        }
        
        # Collect exactly the required number from each role
        for role in role_order:
            players_for_role = all_players_by_role[role]
            needed = role_needed[role]
            count = 0
            
            for player in players_for_role:
                if count >= needed:
                    break
                player_name = player['player_name']
                if player_name not in added_names:
                    team.append(player)
                    added_names.add(player_name)
                    count += 1
        
        if not team:
            return jsonify({"error": f"Could not generate team for {match_type}"}), 400
        
        # Save to database
        try:
            team_name = f"{opposition} vs {match_type} - {pitch_type} Pitch ({weather})"
            generated_team = GeneratedBestXITeam(
                team_name=team_name,
                opposition=opposition,
                pitch_type=pitch_type,
                weather=weather,
                match_type=match_type,
                players_json=json.dumps(team)
            )
            db.session.add(generated_team)
            db.session.commit()
        except Exception as e:
            print(f"Error saving team: {e}")
            db.session.rollback()
        
        return jsonify(team), 200
    
    except Exception as e:
        print(f"Error generating Best XI: {e}")
        return jsonify({"error": f"Error generating team: {str(e)}"}), 500

@best_xi_bp.route('/api/suggest-best-xi', methods=['GET'])
def suggest_best_xi():
    opposition = request.args.get('opposition')
    pitch = request.args.get('pitch')
    weather = request.args.get('weather') or data_loader.default_weather
    match_type = request.args.get('match_type', 'ODI')  # Default to ODI if not provided

    if not all([opposition, pitch, weather, data_loader.model]):
        return jsonify({"error": "Missing parameters or model not loaded"}), 400

    if data_loader.df_players_ml.empty:
        return jsonify({"error": "CSV dataset not loaded"}), 400

    unique_players = data_loader.df_players_ml[['Player_Name', 'Player_Type', 'Role']].drop_duplicates(subset=['Player_Name'])
    
    predictions = []
    for _, row in unique_players.iterrows():
        player_name = row['Player_Name']
        player_type = row['Player_Type'] if pd.notna(row['Player_Type']) else 'Batsman'
        
        input_data = pd.DataFrame({
            'Opponent_Team': [opposition], 'Pitch_Type': [pitch],
            'Weather': [weather], 'Player_Name': [player_name],
            'Player_Type': [player_type]
        })
        
        try:
            predicted_score = data_loader.model.predict(input_data)[0]
            role = row['Role'] if pd.notna(row['Role']) else player_type
            
            if player_name in data_loader.WICKET_KEEPER_NAMES: role = 'Wicket Keeper'
            elif player_name in data_loader.ALL_ROUNDER_NAMES: role = 'All-Rounder'
            
            predictions.append({
                'name': player_name, 'type': player_type,
                'role': role, 'score': float(predicted_score)
            })
        except: continue

    if not predictions: return jsonify({"error": "No predictions generated"}), 400

    predictions.sort(key=lambda x: x['score'], reverse=True)
    
    final_team = []
    team_names = set()
    
    # Select Keeper
    keepers = [p for p in predictions if 'keeper' in str(p['role']).lower()]
    if keepers:
        best_keeper = max(keepers, key=lambda x: x['score'])
        best_keeper['role'] = 'Wicket Keeper'
        final_team.append(best_keeper)
        team_names.add(best_keeper['name'])

    # Fill remaining spots
    for p in predictions:
        if len(final_team) >= 11: break
        if p['name'] not in team_names:
            final_team.append(p)
            team_names.add(p['name'])

    # Ensure we return exactly 11 players (or as many as available)
    if len(final_team) < 11:
        print(f"Warning: Only {len(final_team)} players selected. Need 11.")
        # Try to add more from remaining predictions
        remaining = [p for p in predictions if p['name'] not in team_names]
        for p in remaining:
            if len(final_team) >= 11: break
            final_team.append(p)
            team_names.add(p['name'])

    # Format response - only include name and role
    formatted_team = [{'name': p['name'], 'role': p['role']} for p in final_team]
    
    # Save generated team to database
    try:
        team_name = f"{opposition} vs {match_type} - {pitch} Pitch ({weather})"
        generated_team = GeneratedBestXITeam(
            team_name=team_name,
            opposition=opposition,
            pitch_type=pitch,
            weather=weather,
            match_type=match_type,
            players_json=json.dumps(formatted_team)
        )
        db.session.add(generated_team)
        db.session.commit()
        print(f"Saved generated team to database: {team_name}")
    except Exception as e:
        print(f"Error saving team to database: {e}")
        db.session.rollback()
    
    print(f"Generated Best XI: {len(formatted_team)} players for {opposition} on {pitch} pitch ({weather} weather, {match_type} match)")
    
    return jsonify(formatted_team)