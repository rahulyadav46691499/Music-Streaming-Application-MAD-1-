from flask import Flask,request,render_template,redirect,session
from model import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'


db.init_app(app)
app.app_context().push()

app.secret_key='thisismysecretkey'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login_user',methods=['GET','POST'])
def login_user():
    all_users = User.query.all()
    if request.method=='POST':
        username = request.form.get('username')
        for i in all_users:
            if i.username==username:
                password = request.form.get('password')
                if i.password==password:
                    session['username'] = username
                    session['name'] = i.name
                    session['id'] = i.user_id
                    session['status'] = i.status
                    return redirect('/dashboard')
                else:
                    return redirect('/login_user')
        return redirect('/register')      
    else:
        return render_template('login_user.html')

@app.route('/login_creator',methods=['GET','POST'])
def login_creator():
    all_users = User.query.all()
    if request.method=='POST':
        username = request.form.get('username')
        for i in all_users:
            if i.username==username and i.status=='Creator':
                password = request.form.get('password')
                if i.password==password:
                    session['username'] = username
                    session['name'] = i.name
                    session['id'] = i.user_id
                    session['status'] = i.status
                    return redirect('/creator_dashboard')
                else:
                    return redirect('/login_creator')
        return redirect('/register')      
    else:
        return render_template('login_creator.html')
    
@app.route('/login_admin',methods=['GET','POST'])
def login_admin():
    all_users = User.query.all()
    if request.method=='POST':
        username = request.form.get('username')
        for i in all_users:
            if i.username==username and i.status=='Admin':
                password = request.form.get('password')
                if i.password==password:
                    session['username'] = username
                    return redirect('/admin_dashboard')
                else:
                    return redirect('/login_admin')
        return redirect('/register')      
    else:
        return render_template('login_admin.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        status = request.form.get('status')
        
        new_user = User(name=name, username=username, password=password, status=status)
        db.session.add(new_user)
        db.session.commit()
        
        if status=='User':
            return redirect('/login_user')
        else:
            return redirect('/login_creator')
    return render_template('registration.html')
    
@app.route('/admin_dashboard')
def admin_dashboard():
    total = len(User.query.filter_by(status='User').all())
    total_creators = len(Singer.query.all())
    total_songs = len(Song.query.all())
    songs = Song.query.all()
    total_albums = len(Singer.query.all())
    max_like = 0
    min_like = 1000000
    print(songs)
    for i in songs:
        if i.likes>max_like:
            max_like = i.likes
            hit_song = i.title
        if i.likes<min_like:
            min_like = i.likes
            floop_song = i.title
    
    return render_template('admin_dashboard.html',name=session['username'],total=total,total_songs=total_songs,hit_song=hit_song,total_creators=total_creators,total_albums=total_albums,floop_song=floop_song)
    
    
@app.route('/songs_and_albums')
def songs_and_albums():
    all_songs = Song.query.all()
    return render_template('songs_and_albums.html',name=session['username'],all_songs=all_songs)

@app.route('/creator_dashboard')
def creator_dashboard():
    count = 0
    obj = Singer.query.filter_by(name=session['name']).first() # object with singer details
    session['id'] = obj.singer_id # fetching singers id
    all_songs = Song.query.filter_by(composer = session['id']).all()
    for i in all_songs:
        count = count+i.likes
    print(all_songs)
        
    total_songs = len(all_songs)
    if total_songs==0:
        average_rating=0
    else:
        average_rating = count//total_songs
    
    return render_template('creator_dashboard.html',name = session['username'],total=total_songs,average_rating=average_rating,songs=all_songs)
    
@app.route('/delete/<int:id>')
def delete(id):
    x = Song.query.filter_by(song_id=id).first()
    db.session.delete(x)
    db.session.commit()
    return redirect('/creator_dashboard')

@app.route('/admin_delete/<int:id>')
def admin_delete(id):
    x = Song.query.filter_by(song_id=id).first()
    db.session.delete(x)
    db.session.commit()
    return redirect('/songs_and_albums')

@app.route('/dashboard')
def dashboard():
    all_songs = Song.query.all()
    user_playlist = []
    pl = Playlist.query.all()
    for i in pl:
        if i.person_id==session['id'] and i.name not in user_playlist:
            user_playlist.append(i.name)
    all_singers = Singer.query.all()
    print(all_singers)
    
    return render_template('dashboard.html',username=session['username'],id = session['id'],status = session['status'], allsongs=all_songs,user_playlist = user_playlist, all_singers=all_singers)

@app.route('/process_like/<int:song_id>', methods=['POST'])
def process_like(song_id):
    # Find the song by song_id
    song = Song.query.get(song_id)

    # Increment likes for the song if it exists
    if song:
        song.likes += 1
        db.session.commit()

    # Redirect back to the main page after incrementing likes
    return redirect('/dashboard')

@app.route('/create_new_playlist',methods=['GET','POST'])
def create_new_playlist():
    if request.method=='POST':
        name = request.form.get('name')
        songs_id = request.form.getlist('song_ids[]')
        print(songs_id)
        for i in songs_id:
            x = Playlist(name=name,person_id=session['id'],music_id=i)
            db.session.add(x)
            db.session.commit()
        return redirect('/dashboard')
    all_songs = Song.query.all()
    return render_template('create_new_playlist.html',username=session['username'],all_songs=all_songs)

@app.route('/delete_playlist/<name>')
def delete_playlist(name):
    all_playlist = Playlist.query.all()
    for i in all_playlist:
        if i.name==name:
            db.session.delete(i)
            db.session.commit()
    return redirect('/dashboard')

@app.route('/playlist/<name>',methods=['GET','POST'])
def playlist(name):
    if request.method=='POST':
        songs_id = request.form.getlist('song_ids[]')
        print(songs_id)
        for i in songs_id:
            x = Playlist(name=name,person_id=session['id'],music_id=i)
            db.session.add(x)
            db.session.commit()
        return redirect('/dashboard')
    
    s1 = Playlist.query.filter_by(name=name).all() 
    playlist_songs = []
    for i in s1:
        playlist_songs.append(i.ganna)
    s2 = Playlist.query.filter(Playlist.name!=name).all()
    not_playlist_songs = []
    all_songs = Song.query.all()
    for i in all_songs:
        flag = False
        for j in s1:
            if i.song_id==j.music_id:
                flag=True
                break
        if flag==False:
            not_playlist_songs.append(i)
            
    print(not_playlist_songs)
    
    return render_template('playlist.html',username = session['username'],playlist_songs = playlist_songs,not_playlist_songs=not_playlist_songs,name=name)

@app.route('/delete_playlist_song/<int:id>')
def delete_playlist_song(id):
    x = Playlist.query.filter_by(music_id=id,person_id = session['id']).first()
    db.session.delete(x)
    db.session.commit()
    return redirect('/dashboard')


@app.route('/uploadsong',methods=['GET','POST'])
def uploadsong():
    if request.method=='POST':
        title = request.form.get('title')
        lyrics = request.form.get('lyrics')
        
        new_song = Song(title = title,lyrics=lyrics,likes=0,composer = session['id'])
        db.session.add(new_song)
        db.session.commit()
        
        count = 0
        all_songs = Song.query.filter_by(composer=session['id']).all()
        for i in all_songs:
            count = count+i.likes
        
        total_songs = len(all_songs)
        if total_songs==0:
            average_rating=0
        else:
            average_rating = count//total_songs
        
        return redirect('/creator_dashboard')
        # return render_template('creator_dashboard.html',name=session['username'],average_rating=average_rating,total=total_songs)
    
    return render_template('upload_song.html',name=session['username'])

@app.route('/creator_view_lyrics/<int:id>')
def creator_view_lyrics(id):
    all_songs = Song.query.filter_by(song_id=id).first()
    return render_template('creator_view_lyrics.html',title=all_songs.title,lyrics=all_songs.lyrics,username=session['username'])

@app.route('/Allbum/<int:id>')
def Allbum(id):
    all_songs = Song.query.filter(Song.composer==id).all()
    
    return render_template('Allbum.html',username=session['username'],all_songs=all_songs)

@app.route('/edit/<int:id>',methods=['GET','POST'])
def edit(id):
    if request.method=='POST':
        title = request.form.get('title')
        lyrics = request.form.get('lyrics')
        all_songs = Song.query.filter_by(song_id=id).first()
        all_songs.title = title
        all_songs.lyrics = lyrics
        db.session.commit()
        return redirect('/creator_dashboard')
    return render_template('edit.html',name=session['username'],id=id)

@app.route('/user_view_lyrics/<int:id>')
def user_view_lyrics(id):
    all_songs = Song.query.filter_by(song_id=id).first()
    return render_template('creator_view_lyrics.html',title=all_songs.title,lyrics=all_songs.lyrics,username=session['username'])

@app.route('/search_songs')
def search_songs():
    query = request.args.get('query')  # Retrieve the search query from the URL parameter
    # Assuming you have a model named Song and want to filter songs by their title
    filtered_songs = Song.query.filter(Song.title.ilike(f"%{query}%")).all()
    filtered_singers = Singer.query.filter(Singer.name.ilike(f"%{query}%")).all()
    return render_template('user_search.html',username=session['username'],id = session['id'],status = session['status'], filtered_songs=filtered_songs, filtered_singers=filtered_singers)

@app.route('/admin_search_songs')
def admin_search_songs():
    query = request.args.get('query')  # Retrieve the search query from the URL parameter
    # Assuming you have a model named Song and want to filter songs by their title
    filtered_songs = Song.query.filter(Song.title.ilike(f"%{query}%")).all()
    return render_template('admin_search.html',name=session['username'],filtered_songs=filtered_songs)



if __name__=='__main__':
    app.run(debug=True)