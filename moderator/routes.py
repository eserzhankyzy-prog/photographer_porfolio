from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user

from auth.decorators import role_required, roles_required
from models import Review, db, log_action


moderator_bp = Blueprint('moderator', __name__)


@moderator_bp.route('/')
@role_required('moderator')
def dashboard():
    pending_count = Review.query.filter_by(approved=False).count()
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(5).all()
    return render_template(
        'moderator_dashboard.html',
        pending_count=pending_count,
        reviews=recent_reviews
    )


@moderator_bp.route('/reviews')
@roles_required('admin', 'manager', 'moderator')
def review_moderation():
    pending_reviews = Review.query.filter_by(approved=False).order_by(
        Review.created_at.desc()
    ).all()
    return render_template('moderator/reviews.html', reviews=pending_reviews)


@moderator_bp.route('/reviews/<int:review_id>/approve', methods=['POST'])
@roles_required('admin', 'manager', 'moderator')
def approve_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.approved = True
    log_action(f"Review approved by {current_user.username}")
    db.session.commit()
    flash("review_approved", "success")
    return redirect(url_for('moderator.review_moderation'))


@moderator_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@roles_required('admin', 'manager', 'moderator')
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    log_action(f"Review deleted by {current_user.username}")
    db.session.delete(review)
    db.session.commit()
    flash("review_deleted", "success")
    return redirect(url_for('moderator.review_moderation'))
