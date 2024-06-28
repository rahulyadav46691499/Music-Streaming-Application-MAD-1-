from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    user_id = db.Column(db.Integer(),primary_key = True)
    name = db.Column(db.String(),nullable = False)
    username = db.Column(db.String(),unique = True, nullable = False)
    password  = db.Column(db.String(),unique = True, nullable = False)
    status = db.Column(db.String(),nullable=False)
    user_playlist = db.relationship('Playlist',backref='your_name')

class Singer(db.Model):
    singer_id = db.Column(db.Integer(),primary_key = True)
    name = db.Column(db.String(),nullable = False,unique = True)
    singer_song = db.relationship('Song',backref = 'creator')

class Song(db.Model):
    song_id = db.Column(db.Integer(),primary_key = True)
    title = db.Column(db.String())
    lyrics = db.Column(db.String())
    likes = db.Column(db.Integer(),default=0)
    composer = db.Column(db.Integer(),db.ForeignKey('singer.singer_id'))
    song_playlist = db.relationship('Playlist',backref='ganna')

class Playlist(db.Model):
    playlist_id = db.Column(db.Integer(),primary_key=True)
    name = db.Column(db.String(),nullable = False)
    person_id = db.Column(db.Integer(),db.ForeignKey('user.user_id'))
    music_id = db.Column(db.Integer(),db.ForeignKey('song.song_id'))
    

