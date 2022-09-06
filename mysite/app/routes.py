import os
from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import RegisterCompanyForm, RegisterEmployeeForm, LoginForm, AddCompanySeatForm, DeleteCompanySeatForm, AddSeatBookingForm, AddCompanyUpdateForm, ResetPasswordRequestForm, ResetPasswordForm, FilterSeatDepartmentForm
from app.models import User, Role, Company, UserDetails, CompanySeats, SeatBookings
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
from app.email import send_password_reset_email, booking_confirmation_email, booking_cancellation_email, seat_removal_email, seat_booking_removal_email

app.config['UPLOAD_PATH'] = 'uploaded_files'

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/companysignup', methods=['GET', 'POST'])
def company_signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterCompanyForm()
    if form.validate_on_submit():
        comp = Company(company_name=form.company_name.data, company_updates="")
        db.session.add(comp)
        db.session.commit()
        roles = Role.query.filter_by(name="company_admin").first()
        user = User(company_username=form.company_username.data, email=form.email.data, department=form.department.data, company=comp)
        user.set_password(form.password.data)
        user.roles = [roles]
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered company!')
        return redirect(url_for('login'))
    return render_template('companysignup.html', form = form)

@app.route('/employeeregistration', methods=['GET', 'POST'])
def employee_registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterEmployeeForm()
    if form.validate_on_submit():
        company_check = User.query.filter_by(company_username=form.company_username.data).first()
        if company_check is None:
            flash('That company is not registered')
        else:
            roles = Role.query.filter_by(name="employee").first()
            comp = Company.query.filter_by(id=company_check.company_id).first()
            user = User(company_username=form.company_username.data, email=form.email.data, department=form.department.data, company=comp)
            user.set_password(form.password.data)
            user.roles = [roles]
            db.session.add(user)
            db.session.commit()
            user_details = UserDetails(first_name=form.first_name.data, last_name=form.last_name.data, user_id=user.id)
            db.session.add(user_details)
            db.session.commit()
            flash('Congratulations, you are now a registered employee!')
            return redirect(url_for('login'))
    return render_template('employeeregistration.html', form = form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    company_admin = Role.query.filter_by(name='company_admin').first()
    employee = Role.query.filter_by(name='employee').first()
    if current_user.is_authenticated:
        if current_user.roles[0] is company_admin:
            return redirect(url_for('company_admin_home'))
        elif current_user.roles[0] is employee:
            return redirect(url_for('employee_home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        if user.roles[0] is company_admin:
            return redirect(url_for('company_admin_home'))
        elif user.roles[0] is employee:
            return redirect(url_for('employee_home'))
    return render_template('login.html', form = form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    company_admin = Role.query.filter_by(name='company_admin').first()
    employee = Role.query.filter_by(name='employee').first()
    if current_user.is_authenticated:
        if current_user.roles[0] is company_admin:
            return redirect(url_for('company_admin_home'))
        elif current_user.roles[0] is employee:
            return redirect(url_for('employee_home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('request_password_reset.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        company_admin = Role.query.filter_by(name='company_admin').first()
        employee = Role.query.filter_by(name='employee').first()
        if current_user.is_authenticated:
            if current_user.roles[0] is company_admin:
                return redirect(url_for('company_admin_home'))
            elif current_user.roles[0] is employee:
                return redirect(url_for('employee_home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/company_admin_home', methods=['GET', 'POST'])
@login_required
def company_admin_home():
    company_admin = Role.query.filter_by(name='company_admin').first()
    if current_user.roles[0] is company_admin:
        form = AddCompanyUpdateForm()
        companyInfo = Company.query.filter_by(id=current_user.company.id).first()
        if form.validate_on_submit():
            company = Company.query.filter_by(id=current_user.company.id).first()
            company.company_updates = form.company_updates.data
            db.session.commit()
            flash('Company Update has been added!')
            return redirect(url_for('company_admin_home'))
        return render_template('company_admin_home.html', role=company_admin.name, form=form, companyName=companyInfo.company_name)
    return redirect(url_for('employee_home'))

@app.route('/company_admin_add_seat', methods=['GET', 'POST'])
@login_required
def company_admin_add_seat():
    company_admin = Role.query.filter_by(name='company_admin').first()
    if current_user.roles[0] is company_admin:
        form = AddCompanySeatForm()
        if form.validate_on_submit():
            comp_id = current_user.company_id
            seat = CompanySeats(seat_id_name=form.seat_id_name.data, seat_description=form.seat_description.data, comp_id=comp_id)
            db.session.add(seat)
            db.session.commit()
            flash('Your seat has been added')
            return redirect(url_for('company_admin_add_seat'))
        return render_template('company_admin_add_seat.html', role=company_admin.name, form=form)
    return redirect(url_for('employee_home'))

@app.route('/company_admin_delete_seat', methods=['GET', 'POST'])
@login_required
def company_admin_delete_seat():
    company_admin = Role.query.filter_by(name='company_admin').first()
    if current_user.roles[0] is company_admin:
        form = DeleteCompanySeatForm()
        if form.validate_on_submit():
            seat = CompanySeats.query.filter_by(id=form.company_seat_id.data.id).first()
            db.session.delete(seat)
            db.session.commit()
            bookings = SeatBookings.query.filter_by(company_seat_id=form.company_seat_id.data.id).all()
            for booking in bookings:
                db.session.delete(booking)
                db.session.commit()
                user = User.query.filter_by(id=booking.user_id).first()
                seat_removal_email(booking=booking, userEmail=user.email, seatName=seat.seat_id_name)
            flash('Your seat has been removed')
            return redirect(url_for('company_admin_delete_seat'))
        return render_template('company_admin_delete_seat.html', role=company_admin.name, form=form)
    return redirect(url_for('employee_home'))

@app.route('/company_admin_add_seat_booking', methods=['GET', 'POST'])
@login_required
def company_admin_add_seat_booking():
    company_admin = Role.query.filter_by(name='company_admin').first()
    if current_user.roles[0] is company_admin:
        form = AddSeatBookingForm()
        if form.validate_on_submit():
            get_bookings = SeatBookings.query.filter(SeatBookings.company_seat_id==form.company_seat_id.data.id, SeatBookings.date.startswith(form.date.data.strftime('%Y-%m-%d %H:%M:%S'))).all() # check if seat booking exists with that seat on that date
            check_booking_exists = False
            for booking in get_bookings:
                if (form.start_time.data > get_bookings[0].start_time) and (form.start_time.data < get_bookings[0].end_time): # check if start time is in between existing time
                    check_booking_exists=True
                    break
                elif (form.end_time.data > get_bookings[0].start_time) and (form.end_time.data < get_bookings[0].end_time): # check if end time is in between existing time
                    check_booking_exists=True
                    break
                elif (form.start_time.data <= get_bookings[0].start_time) and (form.end_time.data >= get_bookings[0].end_time): # check if start and end time run over existing time or equals existing time
                    check_booking_exists=True
                    break
            if check_booking_exists: # if there is already a seat booking added on that day with overlapping time, then you cannot add it
                flash('Cannot add seat booking - date and time already added to booking page')
                return redirect(url_for('company_admin_add_seat_booking'))

            # Otherwise, you add it
            seatBooking = SeatBookings(company_seat_id=form.company_seat_id.data.id, date=form.date.data, start_time=form.start_time.data, end_time=form.end_time.data, availability=1, user_id=0)
            db.session.add(seatBooking)
            db.session.commit()
            flash('Seat booking has now been added to the booking page')
            return redirect(url_for('company_admin_add_seat_booking'))
        return render_template('company_admin_add_seat_booking.html', role=company_admin.name, form=form)
    return redirect(url_for('employee_home'))

@app.route('/company_admin_bookings')
@login_required
def company_admin_bookings():
    company_admin = Role.query.filter_by(name='company_admin').first()
    if current_user.roles[0] is company_admin:
        seats = CompanySeats.query.filter_by(comp_id=current_user.company_id).all()
        now = datetime.now()
        today = datetime.combine(now, datetime.min.time())
        bookings = []
        for seat in seats:
            seatBookings = SeatBookings.query.filter(SeatBookings.company_seat_id==seat.id, SeatBookings.date>=today).order_by(SeatBookings.date.asc(), SeatBookings.start_time.asc(), SeatBookings.end_time.asc()).all()
            bookings.append([[seat.seat_id_name, seat.seat_description], seatBookings])
        pastBookings = []
        for seat in seats:
            seatBookings = SeatBookings.query.filter(SeatBookings.company_seat_id==seat.id, SeatBookings.date<today).order_by(SeatBookings.date.desc(), SeatBookings.start_time.desc(), SeatBookings.end_time.desc()).all()
            pastBookings.append([seat.seat_id_name, seatBookings])
        return render_template('company_admin_bookings.html', role=company_admin.name, bookings=bookings, pastBookings=pastBookings)
    return redirect(url_for('employee_home'))

@app.route('/company_admin_delete_seat_booking/<seat_id>', methods=['GET', 'POST'])
@login_required
def company_admin_delete_seat_booking(seat_id):
    company_admin = Role.query.filter_by(name='company_admin').first()
    if current_user.roles[0] is company_admin:
        booking = SeatBookings.query.filter_by(id=seat_id).first()
        seatInfo = CompanySeats.query.filter_by(id=booking.company_seat_id).first()
        user = User.query.filter_by(id=booking.user_id).first()
        db.session.delete(booking)
        db.session.commit()
        if user:
            seat_booking_removal_email(booking=booking, userEmail=user.email, seatName=seatInfo.seat_id_name)
        flash('Seat booking has been removed')
        return redirect(url_for('company_admin_bookings'))
    return redirect(url_for('employee_home'))

@app.route('/upload')
@login_required
def upload():
    company_admin = Role.query.filter_by(name='company_admin').first()
    if current_user.roles[0] is company_admin:
        return render_template('upload.html', role=company_admin.name)
    return redirect(url_for('employee_home'))

@app.route('/upload', methods = ['GET', 'POST'])
@login_required
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], str(current_user.company.id)))
    return redirect(url_for('upload'))

'''@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename, as_attachment=True)'''

@app.route('/employee_home')
@login_required
def employee_home():
    employee = Role.query.filter_by(name='employee').first()
    if current_user.roles[0] is employee:
        companyInfo = Company.query.filter_by(id=current_user.company.id).first()
        return render_template('employee_home.html', role=employee.name, companyName=companyInfo.company_name)
    return redirect(url_for('company_admin_home'))

@app.route('/employee_seating_plan')
@login_required
def employee_seating_plan():
    employee = Role.query.filter_by(name='employee').first()
    if current_user.roles[0] is employee:
        return render_template('employee_seating_plan.html', role=employee.name)
    return redirect(url_for('company_admin_home'))

@app.route('/employee_book_seat', methods = ['GET', 'POST'])
@login_required
def employee_book_seat():
    employee = Role.query.filter_by(name='employee').first()
    if current_user.roles[0] is employee:
        form = FilterSeatDepartmentForm()
        now = datetime.now()
        today = datetime.combine(now, datetime.min.time())
        seats = CompanySeats.query.filter_by(comp_id=current_user.company_id).all()
        bookings = []
        bookings2 = []
        filtered = False
        '''checks if the form was submitted'''
        if form.validate_on_submit() and form.department.data != "":
            filtered=True
            for seat in seats:
                seatBookings = SeatBookings.query.filter(SeatBookings.company_seat_id==seat.id, SeatBookings.date>=today).order_by(SeatBookings.date.asc(), SeatBookings.start_time.asc(), SeatBookings.end_time.asc()).all()
                for seatBooking in seatBookings:
                    user = User.query.filter(User.id==seatBooking.user_id, User.department.startswith(form.department.data)).first()
                    if user:
                        bookings2.append([seat.seat_id_name, seatBooking])
        else:
            for seat in seats:
                seatBookings = SeatBookings.query.filter(SeatBookings.company_seat_id==seat.id, SeatBookings.date>=today).order_by(SeatBookings.date.asc(), SeatBookings.start_time.asc(), SeatBookings.end_time.asc()).all()
                bookings.append([[seat.seat_id_name, seat.seat_description], seatBookings])
        return render_template('employee_book_seat.html', role=employee.name, form=form, bookings=bookings, bookings2=bookings2, filtered=filtered)
    return redirect(url_for('company_admin_home'))

@app.route('/book_seat/<seat_id>', methods = ['GET', 'POST'])
@login_required
def book_seat(seat_id):
    employee = Role.query.filter_by(name='employee').first()
    if current_user.roles[0] is employee:
        seatBooking = SeatBookings.query.filter_by(id=seat_id).first()
        seatBooking.user_id = current_user.get_id()
        seatBooking.availability = seatBooking.availability - 1
        db.session.commit()
        seatInfo = CompanySeats.query.filter_by(id=seatBooking.company_seat_id).first()
        userEmail = current_user.email
        booking_confirmation_email(seatBooking, userEmail, seatName=seatInfo.seat_id_name)
        flash('You are now booked in!')
        return redirect(url_for('employee_book_seat'))
    return redirect(url_for('company_admin_home'))

@app.route('/my_bookings')
@login_required
def my_bookings():
    employee = Role.query.filter_by(name='employee').first()
    if current_user.roles[0] is employee:
        # get today's bookings
        today = datetime.now().strftime("%Y-%m-%d 00:00:00")
        todaysBookings = SeatBookings.query.filter(SeatBookings.user_id==current_user.get_id(), SeatBookings.date.startswith(today)).all()
        todaysBookingsList = []
        for todaysBooking in todaysBookings:
            seat_info = CompanySeats.query.filter_by(id=todaysBooking.company_seat_id).first()
            todaysBookingsList.append([seat_info, todaysBooking])

        # get upcoming bookings
        now = datetime.now()
        today = datetime.combine(now, datetime.min.time())
        upcomingBookings = SeatBookings.query.filter(SeatBookings.user_id==current_user.get_id(), SeatBookings.date>today).order_by(SeatBookings.date.asc(), SeatBookings.start_time.asc(), SeatBookings.end_time.asc()).all()
        upcomingBookingsList = []
        for upcomingBooking in upcomingBookings:
            seat_info = CompanySeats.query.filter_by(id=upcomingBooking.company_seat_id).first()
            upcomingBookingsList.append([seat_info, upcomingBooking])

        # get past bookings
        pastBookings = SeatBookings.query.filter(SeatBookings.user_id==current_user.get_id(), SeatBookings.date<today).order_by(SeatBookings.date.desc(), SeatBookings.start_time.desc(), SeatBookings.end_time.desc()).all()
        pastBookingsList = []
        for pastBooking in pastBookings:
            seat_info = CompanySeats.query.filter_by(id=pastBooking.company_seat_id).first()
            pastBookingsList.append([seat_info, pastBooking])
        return render_template('my_bookings.html', role=employee.name, todaysBookingsList=todaysBookingsList, upcomingBookingsList=upcomingBookingsList, pastBookingsList=pastBookingsList)
    return redirect(url_for('company_admin_home'))

@app.route('/cancel_seat/<seat_id>', methods = ['GET', 'POST'])
@login_required
def cancel_seat(seat_id):
    employee = Role.query.filter_by(name='employee').first()
    if current_user.roles[0] is employee:
        seatBooking = SeatBookings.query.filter_by(id=seat_id).first()
        seatBooking.user_id = 0
        seatBooking.availability = seatBooking.availability + 1
        db.session.commit()
        seatInfo = CompanySeats.query.filter_by(id=seatBooking.company_seat_id).first()
        userEmail = current_user.email
        booking_cancellation_email(seatBooking, userEmail, seatName=seatInfo.seat_id_name)
        flash('Your booking is now cancelled!')
        return redirect(url_for('my_bookings'))
    return redirect(url_for('company_admin_home'))

