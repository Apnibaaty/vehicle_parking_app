from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..models import ParkingLot, ParkingSpot, Reservation
from ..extensions import db
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))

    lots = ParkingLot.query.all()
    reservation = Reservation.query.filter_by(user_id=current_user.id, leave_time=None).first()
    return render_template('user/dashboard.html', lots=lots, active_reservation=reservation)

@user_bp.route('/book/<int:lot_id>')
@login_required
def book_spot(lot_id):
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))

    # Check if user already has a booking
    existing = Reservation.query.filter_by(user_id=current_user.id, leave_time=None).first()
    if existing:
        flash("You already have an active reservation.", "warning")
        return redirect(url_for('user.user_dashboard'))

    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not spot:
        flash("No available spots in this lot.", "danger")
        return redirect(url_for('user.user_dashboard'))

    spot.status = 'O'
    reservation = Reservation(spot_id=spot.id, user_id=current_user.id, parking_time=datetime.now())
    db.session.add(reservation)
    db.session.commit()

    flash("Spot booked successfully!", "success")
    return redirect(url_for('user.user_dashboard'))

@user_bp.route('/leave')
@login_required
def leave_spot():
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))

    reservation = Reservation.query.filter_by(user_id=current_user.id, leave_time=None).first()
    if reservation:
        reservation.leave_time = datetime.now()
        reservation.spot.status = 'A'

        # Calculate cost
        duration = reservation.leave_time - reservation.parking_time
        hours = duration.total_seconds() / 3600
        rate = reservation.spot.lot.price_per_hour
        reservation.cost = round(hours * rate, 2)

        db.session.commit()
        flash(f"Spot released. Total cost: ₹{reservation.cost}", "info")
    else:
        flash("No active reservation found.", "danger")

    return redirect(url_for('user.user_dashboard'))


@user_bp.route('/history')
@login_required
def history():
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))

    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.parking_time.desc()).all()
    return render_template('user/history.html', reservations=reservations)
