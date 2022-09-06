from flask_mail import Message
from app import mail, app
from flask import render_template

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[SimpleSeating] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', token=token),
               html_body=render_template('email/reset_password.html', token=token))

def booking_confirmation_email(seatBooking, userEmail, seatName):
    send_email('[SimpleSeating] Seat Booking Confirmation',
               sender=app.config['ADMINS'][0],
               recipients=[userEmail],
               text_body=render_template('email/booking_confirmation.txt', seatBooking=seatBooking, seatName=seatName),
               html_body=render_template('email/booking_confirmation.html', seatBooking=seatBooking, seatName=seatName))

def booking_cancellation_email(seatBooking, userEmail, seatName):
    send_email('[SimpleSeating] Seat Booking Cancellation',
               sender=app.config['ADMINS'][0],
               recipients=[userEmail],
               text_body=render_template('email/booking_cancellation.txt', seatBooking=seatBooking, seatName=seatName),
               html_body=render_template('email/booking_cancellation.html', seatBooking=seatBooking, seatName=seatName))

def seat_removal_email(booking, userEmail, seatName):
    send_email('[SimpleSeating] Seat Removal',
               sender=app.config['ADMINS'][0],
               recipients=[userEmail],
               text_body=render_template('email/seat_removal.txt', booking=booking, seatName=seatName),
               html_body=render_template('email/seat_removal.html', booking=booking, seatName=seatName))

def seat_booking_removal_email(booking, userEmail, seatName):
    send_email('[SimpleSeating] Seat Booking Removal',
               sender=app.config['ADMINS'][0],
               recipients=[userEmail],
               text_body=render_template('email/seat_booking_removal.txt', booking=booking, seatName=seatName),
               html_body=render_template('email/seat_booking_removal.html', booking=booking, seatName=seatName))