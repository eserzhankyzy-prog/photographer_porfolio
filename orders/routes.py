from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import Order, db, log_action

orders_bp = Blueprint(
    'orders',
    __name__
)

@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():

    if request.method == 'POST':

        customer_name = request.form.get('customer_name', current_user.username)
        service_type = request.form['service_type']
        notes = request.form.get('notes', '')

        order = Order(
            customer_name=customer_name,
            customer_email=current_user.email,
            service_type=service_type,
            notes=notes,
            user_id=current_user.id
        )

        db.session.add(order)
        log_action(f"Order created by {current_user.email}: {service_type}")
        db.session.commit()

        flash("order_created", "success")
        return redirect(url_for('auth.profile'))

    return render_template(
        'create_order.html'
    )
