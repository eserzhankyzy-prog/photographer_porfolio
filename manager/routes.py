import os
from datetime import datetime
from uuid import uuid4

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename

from auth.decorators import role_required, roles_required
from models import Album, Order, Photo, Review, db, log_action


manager_bp = Blueprint('manager', __name__)

ORDER_STATUSES = ('pending', 'confirmed', 'in_progress', 'completed', 'cancelled')
PHOTO_CATEGORIES = ('Wedding', 'Portrait', 'Family', 'Event')
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


@manager_bp.route('/')
@role_required('manager')
def dashboard():
    orders = Order.query.order_by(Order.order_date.desc()).all()
    photos_count = Photo.query.count()
    pending_reviews_count = Review.query.filter_by(approved=False).count()
    return render_template(
        'manager_dashboard.html',
        orders=orders,
        statuses=ORDER_STATUSES,
        photos_count=photos_count,
        pending_reviews_count=pending_reviews_count
    )


@manager_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@role_required('manager')
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status', 'pending')

    if status in ORDER_STATUSES:
        order.status = status
        log_action(f"Manager updated order #{order.id} to {status}")
        db.session.commit()
        flash("order_updated", "success")

    return redirect(url_for('manager.dashboard'))


@manager_bp.route('/photos')
@roles_required('admin', 'manager')
def photos():
    photo_items = Photo.query.order_by(Photo.created_at.desc()).all()
    return render_template('manager/photos.html', photos=photo_items)


@manager_bp.route('/photos/add', methods=['GET', 'POST'])
@roles_required('admin', 'manager')
def add_photo():
    albums = Album.query.order_by(Album.title.asc()).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Wedding')
        description = request.form.get('description', '').strip()
        price_value = request.form.get('price', '').strip()
        shoot_date_value = request.form.get('shoot_date', '').strip()
        album_id_value = request.form.get('album_id', '').strip()
        image = request.files.get('image')

        if category not in PHOTO_CATEGORIES:
            category = 'Wedding'

        if not title or not image or not image.filename:
            flash('photo_required', 'danger')
            return render_template(
                'manager/add_photo.html',
                albums=albums,
                categories=PHOTO_CATEGORIES
            ), 400

        filename = secure_filename(image.filename)
        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            flash('invalid_image_type', 'danger')
            return render_template(
                'manager/add_photo.html',
                albums=albums,
                categories=PHOTO_CATEGORIES
            ), 400

        upload_dir = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_dir, exist_ok=True)

        stored_filename = f"{uuid4().hex}-{filename}"
        absolute_path = os.path.join(upload_dir, stored_filename)
        image.save(absolute_path)

        price = None
        if price_value:
            try:
                price = float(price_value)
            except ValueError:
                price = None

        shoot_date = None
        if shoot_date_value:
            try:
                shoot_date = datetime.strptime(shoot_date_value, '%Y-%m-%d').date()
            except ValueError:
                shoot_date = None

        album_id = int(album_id_value) if album_id_value.isdigit() else None

        photo = Photo(
            title=title,
            category=category,
            description=description,
            image_path=f"uploads/{stored_filename}",
            price=price,
            shoot_date=shoot_date,
            album_id=album_id,
        )
        db.session.add(photo)
        log_action(f"Photo added by {current_user.username}")
        db.session.commit()
        flash('photo_added', 'success')
        return redirect(url_for('manager.photos'))

    return render_template(
        'manager/add_photo.html',
        albums=albums,
        categories=PHOTO_CATEGORIES
    )


@manager_bp.route('/photos/<int:photo_id>/delete', methods=['POST'])
@roles_required('admin', 'manager')
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    image_path = photo.image_path

    if image_path:
        static_root = current_app.static_folder
        absolute_path = os.path.abspath(os.path.join(static_root, image_path))
        upload_root = os.path.abspath(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER']))

        if os.path.commonpath([absolute_path, upload_root]) == upload_root and os.path.exists(absolute_path):
            os.remove(absolute_path)

    log_action(f"Photo deleted by {current_user.username}")
    db.session.delete(photo)
    db.session.commit()
    flash('photo_deleted', 'success')
    return redirect(url_for('manager.photos'))
