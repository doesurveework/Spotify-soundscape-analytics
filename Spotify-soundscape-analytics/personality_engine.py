def calculate_metrics(tracks_data, features_data):
    if not tracks_data or not features_data:
        return {
            "obscurityScore": 0,
            "personalityType": "The Silent Listener",
            "averages": {"energy": 0, "danceability": 0, "valence": 0}
        }

    total_popularity = sum([track['popularity'] for track in tracks_data])
    avg_popularity = total_popularity / len(tracks_data)
    obscurity_score = 100 - avg_popularity 
    
    valid_features = [f for f in features_data if f is not None]
    if not valid_features:
        return {
            "obscurityScore": round(obscurity_score, 1),
            "personalityType": "The Enigmatic Curator",
            "averages": {"energy": 0, "danceability": 0, "valence": 0}
        }

    avg_energy = sum([f['energy'] for f in valid_features]) / len(valid_features)
    avg_dance = sum([f['danceability'] for f in valid_features]) / len(valid_features)
    avg_valence = sum([f['valence'] for f in valid_features]) / len(valid_features)
    
    if avg_energy > 0.7 and avg_dance > 0.7:
        personality = "The Kinetic Hedonist (High-energy, rhythm-driven)"
    elif avg_valence < 0.4 and avg_energy < 0.5:
        personality = "The Melancholic Introspector (Deep, atmospheric soundscapes)"
    elif avg_dance > 0.6 and avg_valence > 0.6:
        personality = "The Solar Optimist (Vibrant, uplifting anthems)"
    else:
        personality = "The Sonic Eclectic (Highly balanced, diverse selection)"
        
    return {
        "obscurityScore": round(obscurity_score, 1),
        "personalityType": personality,
        "averages": {
            "energy": round(avg_energy, 2),
            "danceability": round(avg_dance, 2),
            "valence": round(avg_valence, 2)
        }
    }
