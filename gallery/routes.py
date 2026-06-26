from flask import Blueprint, render_template, request
from models import Album, Photo

gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route('/')
def gallery():

    albums = Album.query.all()
    photos = Photo.query.order_by(Photo.created_at.desc()).all()

    return render_template(
        'gallery.html',
        albums=albums,
        photos=photos
    )
@gallery_bp.route('/album/<int:id>')
def album_detail(id):

    album = Album.query.get_or_404(id)

    photos = Photo.query.filter_by(
        album_id=id
    ).all()

    return render_template(
        'album_detail.html',
        album=album,
        photos=photos
    )
@gallery_bp.route('/search')
def search():

    query = request.args.get('q', '')

    albums = Album.query.filter(
        Album.title.contains(query)
    ).all()

    return render_template(
        'search.html',
        albums=albums,
        query=query
    )
