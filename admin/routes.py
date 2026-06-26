from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from auth.decorators import role_required
from models import Log, ROLES, User, db, log_action


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@role_required('admin')
def dashboard():
    users = User.query.order_by(User.id.desc()).all()
    logs = Log.query.order_by(Log.created_at.desc()).limit(20).all()
    return render_template('admin_dashboard.html', users=users, roles=ROLES, logs=logs)


@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@role_required('admin')
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    role = request.form.get('role', 'client')

    if role in ROLES:
        user.role = role
        log_action(f"Admin updated {user.email} role to {role}")
        db.session.commit()
        flash("role_updated", "success")

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("cannot_delete_self", "danger")
        return redirect(url_for('admin.dashboard'))

    log_action(f"Admin deleted user {user.email}")
    db.session.delete(user)
    db.session.commit()
    flash("user_deleted", "success")

    return redirect(url_for('admin.dashboard'))
