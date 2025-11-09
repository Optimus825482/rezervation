"""
Script to generate QR codes for existing reservations
"""
from app import create_app, db
from app.models.reservation import Reservation

def generate_all_qr_codes():
    """Generate QR codes for all active reservations"""
    app = create_app()
    
    with app.app_context():
        # Get all active reservations without QR codes
        reservations = Reservation.query.filter(
            Reservation.qr_code_path.is_(None),
            Reservation.status == 'active'
        ).all()
        
        print(f"Found {len(reservations)} reservations without QR codes")
        
        generated = 0
        for reservation in reservations:
            try:
                filepath = reservation.generate_qr_code()
                db.session.commit()
                print(f"✅ Generated QR code for {reservation.reservation_code}: {filepath}")
                generated += 1
            except Exception as e:
                print(f"❌ Error generating QR for {reservation.reservation_code}: {e}")
                db.session.rollback()
        
        print(f"\n🎉 Successfully generated {generated}/{len(reservations)} QR codes")

if __name__ == '__main__':
    generate_all_qr_codes()
