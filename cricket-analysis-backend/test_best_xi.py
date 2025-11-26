#!/usr/bin/env python3
import requests
import time

time.sleep(2)

print("\n" + "=" * 70)
print("TESTING BEST XI GENERATE ENDPOINT")
print("=" * 70)

# Test with Test match type
print("\n1. Testing with Test match type:")
r = requests.get('http://127.0.0.1:5000/api/best-xi/generate', params={
    'opposition': 'Bangladesh',
    'pitch_type': 'Balanced',
    'weather': 'Balanced',
    'match_type': 'Test'
})

print(f"   Status: {r.status_code}")
if r.status_code == 200:
    team = r.json()
    print(f"   Team size: {len(team)}")
    if team:
        print(f"   Sample players:")
        for p in team[:3]:
            print(f"     - {p['player_name']} ({p['role']})")
else:
    print(f"   Error: {r.text}")

# Test with ODI match type
print("\n2. Testing with ODI match type:")
r = requests.get('http://127.0.0.1:5000/api/best-xi/generate', params={
    'opposition': 'India',
    'pitch_type': 'Batting Friendly',
    'weather': 'Sunny',
    'match_type': 'ODI'
})

print(f"   Status: {r.status_code}")
if r.status_code == 200:
    team = r.json()
    print(f"   Team size: {len(team)}")
    if team:
        print(f"   Sample players:")
        for p in team[:3]:
            print(f"     - {p['player_name']} ({p['role']})")
else:
    print(f"   Error: {r.text}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70 + "\n")
