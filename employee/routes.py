from flask import Blueprint, flash, redirect, render_template, url_for

from auth.decorators import role_required
from models import Order, db, log_action


employee_bp = Blueprint('employee', __name__)


@employee_bp.route('/')
@role_required('employee')
def dashboard():
    orders = Order.query.filter(
        Order.status.in_(('confirmed', 'in_progress'))
    ).order_by(Order.order_date.desc()).all()
    return render_template('employee_dashboard.html', orders=orders)


@employee_bp.route('/orders/<int:order_id>/complete', methods=['POST'])
@role_required('employee')
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'completed'
    log_action(f"Employee completed order #{order.id}")
    db.session.commit()
    flash("order_updated", "success")
    return redirect(url_for('employee.dashboard'))
