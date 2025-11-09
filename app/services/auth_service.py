from app import db
from app.models import User, Company


class AuthService:
    @staticmethod
    def create_company(data):
        company = Company(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            address=data.get('address'),
            is_setup_complete=True
        )
        db.session.add(company)
        db.session.flush()
        return company

    @staticmethod
    def create_admin_user(company_id, data):
        user = User(
            company_id=company_id,
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            role='admin'
        )
        user.set_password(data['password'])
        db.session.add(user)
        return user

    @staticmethod
    def authenticate_user(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_active:
            return user
        return None
