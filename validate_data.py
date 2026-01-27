"""Validation script for anime data"""
import json
import sys

def validate_anime_data(filename='anime_data.json'):
    """Validate anime data structure and count"""
    try:
        # Load and validate the data
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Check minimum count
        if len(data) < 28000:
            print(f"❌ Validation failed: Only {len(data)} anime (need >= 28000)")
            return False
        
        # Check structure of first few items
        required_fields = ['title', 'rating', 'type', 'url', 'genres', 'mal_id']
        for i, anime in enumerate(data[:5]):
            for field in required_fields:
                if field not in anime:
                    print(f"❌ Validation failed: Missing field '{field}' in anime {i}")
                    return False
        
        # Check for valid JSON structure
        if not isinstance(data, list):
            print(f"❌ Validation failed: Data is not a list")
            return False
        
        print(f"✅ Validation passed: {len(data)} anime with correct structure")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Validation failed: Invalid JSON - {e}")
        return False
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    if validate_anime_data():
        sys.exit(0)
    else:
        sys.exit(1)
