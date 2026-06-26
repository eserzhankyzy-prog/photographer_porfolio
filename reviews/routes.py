from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import Review, db, log_action

reviews_bp = Blueprint(
    'reviews',
    __name__
)

@reviews_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_review():

    if request.method == 'POST':

        review = Review(
            author=request.form['author'],
            text=request.form['text'],
            rating=request.form['rating'],
            user_id=current_user.id,
            approved=False
        )

        db.session.add(review)
        log_action(f"Review created by {current_user.email}")
        db.session.commit()

        flash("review_created", "success")
        return redirect(url_for('auth.profile'))

    return render_template(
        'create_review.html'
    )
