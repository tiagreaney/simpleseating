from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt
from app import app

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    company_username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    roles = db.relationship('Role', secondary='user_roles')
    department = db.Column(db.String(128))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    def __repr__(self):
        return '<User {}>'.format(self.company_username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer(), primary_key=True)
    company_name = db.Column(db.String(64))
    company_updates = db.Column(db.String(300))
    user = db.relationship('User', backref='company', lazy='dynamic')

class UserDetails(db.Model):
    __tablename__ = "user_details"
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    user_id = db.Column(db.Integer())

class CompanySeats(db.Model):
    __tablename__ = "company_seats"
    id = db.Column(db.Integer(), primary_key=True)
    seat_id_name = db.Column(db.String(64))
    seat_description = db.Column(db.String(300))
    comp_id = db.Column(db.Integer())

    def __repr__(self):
        return '{}'.format(self.seat_id_name)

class SeatBookings(db.Model):
    __tablename__ = "seat_bookings"
    id = db.Column(db.Integer(), primary_key=True)
    company_seat_id = db.Column(db.Integer())
    date = db.Column(db.DateTime)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    availability = db.Column(db.Integer())
    user_id = db.Column(db.Integer())