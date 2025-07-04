from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import ParkingLot, ParkingSpot
from ..extensions import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))
    
    lots = ParkingLot.query.all()
    return render_template('admin/dashboard.html', lots=lots)

@admin_bp.route('/create_lot', methods=['GET', 'POST'])
@login_required
def create_lot():
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    if request.method == 'POST':
        location = request.form['location']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price = float(request.form['price'])
        total_spots = int(request.form['total_spots'])

        new_lot = ParkingLot(location=location, address=address,
                             pin_code=pin_code, price_per_hour=price,
                             total_spots=total_spots)
        db.session.add(new_lot)
        db.session.commit()

        # Automatically create parking spots
        for _ in range(total_spots):
            spot = ParkingSpot(lot_id=new_lot.id, status='A')
            db.session.add(spot)
        db.session.commit()

        flash('Parking Lot created successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/create_lot.html')

@admin_bp.route('/delete_lot/<int:lot_id>')
@login_required
def delete_lot(lot_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    lot = ParkingLot.query.get_or_404(lot_id)
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()

    if occupied_spots > 0:
        flash('Cannot delete a lot with occupied spots.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    # Delete spots first
    ParkingSpot.query.filter_by(lot_id=lot.id).delete()
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted successfully.', 'info')
    return redirect(url_for('admin.admin_dashboard'))
