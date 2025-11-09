from app import create_app, db
from app.models import Company, User, SeatingType

app = create_app('development')

with app.app_context():
    # Create seating types
    seating_types = [
        {'name': 'Masa - 2 Kiþilik', 'seat_type': 'table', 'capacity': 2, 'color_code': '#3498db'},
        {'name': 'Masa - 4 Kiþilik', 'seat_type': 'table', 'capacity': 4, 'color_code': '#2ecc71'},
        {'name': 'Masa - 5 Kiþilik', 'seat_type': 'table', 'capacity': 5, 'color_code': '#f39c12'},
        {'name': 'Masa - 6 Kiþilik', 'seat_type': 'table', 'capacity': 6, 'color_code': '#e74c3c'},
        {'name': 'Masa - 8 Kiþilik', 'seat_type': 'table', 'capacity': 8, 'color_code': '#9b59b6'},
        {'name': 'Masa - 10 Kiþilik', 'seat_type': 'table', 'capacity': 10, 'color_code': '#1abc9c'},
        {'name': 'Masa - 12 Kiþilik', 'seat_type': 'table', 'capacity': 12, 'color_code': '#34495e'},
        {'name': 'Tekli Koltuk', 'seat_type': 'chair', 'capacity': 1, 'color_code': '#e67e22'},
        {'name': 'Çiftli Koltuk', 'seat_type': 'chair', 'capacity': 2, 'color_code': '#95a5a6'},
        {'name': 'VIP Kutu', 'seat_type': 'vip', 'capacity': 4, 'color_code': '#c0392b'},
    ]
    
    for st in seating_types:
        if not SeatingType.query.filter_by(name=st['name']).first():
            seating_type = SeatingType(**st)
            db.session.add(seating_type)
    
    db.session.commit()
    print("Seating types created successfully!")

if __name__ == '__main__':
    seed_data.py
