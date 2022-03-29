#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')# load all settings from config
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# TODO: connect to a local postgresql database
db.create_all() 
db.init_app(app)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    genres = db.Column(ARRAY(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())

    def __repr__(self):
       return f'<id: {self.id}, name: {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
                       
    
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())

    def __repr__(self):
        return f'<id: {self.id}, name: {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
                       
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime)
    venue_name = db.relationship('Venue', backref=db.backref('shows'), lazy='dynamic')                   
    artist = db.relationship('Artist', backref=db.backref('shows'), lazy='dynamic')
                       
    def __repr__(self):
        return f'<id: {self.id}>'

db.create_all() 
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
                       
  for city in cities: 
    venues_in_city = db. session.query(Venue.id, Venue.name).filter(Venue.city==city[0]).filter(Venue.state==city[1])
    data.append({
        "city":city[0],
        "state":city[1],
        "venues":venues_in_city
    })

  return render_template('pages/venues.html', areas=data);
                       
# Search venue-----------------------------------------------------------
                       
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []
  for venue in venues: 
      num_upcoming_shows = 0
      shows = db.session.query(Show).filter(show.venue_id == venue.id)
      for show in shows:
          if (show.start_time > datetime.now()):
              num_upcoming_shows += 1; 
      data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows   
      })
  

  response= {
     "count": len(venues),
      "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Show Venue--------------------------------------------------
                       
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  if not venue: 
    return render_template('errors/404.html') 
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all() 
  upcoming_shows=[] 
  
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue.id).filter(Show.start_time<datetime.now()).all() 
  past_shows=[] 

  for show in past_shows_query: 
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%d/%m/%Y')
    })
  for show in upcoming_shows_query: 
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%d/%m/%Y')
    })
                                   
   data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)
                       
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
 
     
  # TODO: on unsuccessful db insert, flash an error instead.
                       
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try: 
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone'] 
    genres =request.form.getlist('genres') 
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website'] 
    seeking_talent = True if 'seeking_talent' in request.form else False 
    seeking_description = request.form['seeking_description'] 
    
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue) 
    db.session.commit() 
  except: 
    error = True
    db.session.rollback() 
    print(sys.exc_info()) 
  finally: 
    db.session.close() 
  if error: 
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  if not error:
    flash('Venue'+request.form['name']+' was successfully listed!')

  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False 
  try:
      db.session.query(Venue).filter(Venue.id==venue_id).delete()
      db.session.commit()
  except:
      error = True
      flash('An error has occurred')
      db.session.rollback()
  finally:
      db.session.close()
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all() 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '') 
  search_result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all() 
  data = [] 
  for result in search_result: 
    data.append({
      "id": result.id, 
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id)).filter(Show.start_time > datetime.now()).all()  
    })
                       
                       
   response=data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_query = db.session.query(Artist).get(artist.id)
  
  if not artist_query:
    return render_template('error/404.html')
                       
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).all()
  past_shows = [] 
                       
  for show in past_shows_query: 
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue,image_link,
      "start_time": show.start_time.strftime('%d/%m/%Y')
    })
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
  upcoming_shows = [] 
  
  for show in upcoming_shows_query:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue,image_link,
      "start_time": show.start_time.strftime('%d/%m/%Y')
    })
                       
  data = {
    "id": artist_query.id,
    "name": artist_query.name,
    "genres": artist_query.genres,
    "city": artist_query.city,
    "state": artist_query.state,
    "phone": artist_query.phone,
    "website": artist_query.website,
    "facebook_link": artist_query.facebook_link,
    "seeking_venue": artist_query.seeking_venue,
    "seeking_description": artist_query.seeking_description,
    "image_link": artist_query.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
    
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  form_artist = db.session.query(Artist).get(artist_id)
  artist={
    "id": form_artist.id,
    "name": form_artist.name,
    "genres": form_artist.genres,
    "city": form_artist.city,
    "state": form_artist.state,
    "phone": form_artist.phone,
    "website": form_artist.website,
    "facebook_link": form_artist.facebook_link,
    "seeking_venue": form_artist.seeking_venue,
    "seeking_description": form_artist.seeking_description,
    "image_link": form_artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  artist = Artist.query.get(artist_id) 
  try:
      artist.name = request.form['name']
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form[phone']
      artist.image_link = request.form['image_link']
      artist.facebook_link = request.form['facebook_link']
      artist.genres = request.form.getlist('genres')
      artist.website_link = request.form['website_link']
      artist.seeking_venue = True if 'seeking_venue' in request.form else False
      artist.seeking_description = request.form['seeking_description']
      db.session.commit()
  except:
      error=True
      flash('An error has occurred')
      db.session.rollback()
  finally:
      db.session.close()
                    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  form_venue = db.session.query(Venue).get(venue_id)
  venue={
    form.name.data = form_venue.name
    form.city.data = form_venue.city
    form.state.data = form_venue.state
    form.phone.data = form_venue.phone
    form.address.data = form_venue.address
    form.genres.data = form_venue.genres
    form.facbook_link.data = form_venue.facebook_link
    form.image_link.data = form_venue.image_link
    form.website.data = form_venue.website
    form.seeking_talent.data = form_venue.seeking_talent
    form.seeking_description.data = form_venue.seeking_description 
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
      venue = db.session.query(Venue).get(venue_id)
      venue.name = request.form.get('name')
      venue.city = request.form.get('city')
      venue.state = request.form.get('state')
      venue.address = request.form.get('address')
      venue.phone = request.form.get('phone')
      venue.image_link = request.form.get('image_link')
      venue.facebook_link = request.form.get('facebook_link')
      venue.genres = request.form.getlist('genres')
      venue.website_link = request.form.get('website_link')
      if request.form.get('seeking_talent'):
          venue.seeking_talent = True
      else:
          venue.seeking_talent = False
      venue.seeking_description = request.form.get('seeking_description')
      db.session.commit()
  except:
      flash('An error has occurred')
      db.session.rollback()
  finally:
      db.session.close()
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website = request.form['website']
    seeking_venue = True if 'seeking_venue' in request.form else False 
    seeking_description = request.form['seeking_description'] 

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website,seeking_venue=seeking_venue)
    # on successful db insert, flash success
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  except:
    flash('An error occurred '+ request.form['name']+ ' Artist could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows_query = db.session.query(Show).join(Artist).join(Venue).all()
  data = [] 
  for show in shows_query:
    data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue_name, 
        "artist_id": show.artist_id,
        "artist_name": show.artist_name,
        "artist_image_link": show.artist.image_link
        "start_time":show.start_time.strftime('%d/%m/%Y')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
      venue_id = request.form['venue_id']
      artist_id = request.form['artist_id']
      start_time = request.form['start_time']
      show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
      # on successful db insert, flash success
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
      flash('An error has occurred. Show could not be listed.')
      db.session.rollback()
  finally:
      db.session.close()
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
