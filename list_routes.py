from app import create_app

app = create_app('development')

print("\n📋 Tüm Flask Route'ları:\n")
print(f"{'Endpoint':<40} {'Methods':<20} {'Rule'}")
print("=" * 100)

for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f"{rule.endpoint:<40} {methods:<20} {rule.rule}")
