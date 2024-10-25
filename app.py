#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from dateutil import parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)

moment = Moment(app)

app.config.from_object('config')

db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Shows(db.Model):
  __tablename__ = "Shows"

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
  start_time = db.Column(db.DateTime)

  def to_dict(self):
    return {
      'id': self.id,
      'venue_id': self.venue_id,
      'artist_id': self.artist_id,
      'start_time': self.start_time
    }
  
  def __repr__(self):
    return f'<Shows {self.id}, {self.artist_id}, {self.venue_id}, {self.start_time}>'

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    #areas_id = db.Column(db.Integer, db.ForeignKey('Areas.id'), nullable = False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, unique=False, default=True)
    seeking_description = db.Column(db.String(1500))
    website = db.Column(db.String(120))
    children = db.relationship('Shows', backref='show', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # Method to serialize the object to a dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent':self.seeking_talent
        }


    # not sure if this is required
    def __repr__(self):
          return f'<Venue {self.id}, {self.name}, {self.phone}, {self.image_link}, {self.facebook_link}, {self.seeking_talent}, {self.seeking_description}, {self.website}>'

class Artist(db.Model): 
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, unique=False, default=True)
    seeking_description = db.Column(db.String(1500))
    children = db.relationship('Shows', backref='venue', lazy=True)

    def to_dict(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'generes': self.genres,
        'facebook_link': self.facebook_link,
        'website': self.website,
        'seeking_venue':self.seeking_venue,
        'seeking_description':self.seeking_description
    }
    def __repr__(self):
      return f'<Venue {self.id}, {self.name}, {self.city}, {self.state}, {self.phone}, {self.genres},  {self.facebook_link}, {self.website}, {self.seeking_venue}, {self.seeking_description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
#class Areas(db.Model):
#  __tablename__ = 'Areas'
#  
#  id = db.Column(db.Integer, primary_key=True)
#  city = db.Column(db.String(120))
#  state = db.Column(db.String(120))
#  children = db.relationship('Venue', backref='Venue', lazy=True)
#
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # not sure if this is required
#  def __repr__(self):
#    return f'<Venue {self.id}, {self.city}, {self.state}>'
    
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
  
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
  areas = []
  venues=db.session.query(Venue).order_by('state', 'city').all()
  for venue in venues:
    area_item = next((area for area in areas if area['city'] == venue.city and area['state'] == venue.state), None)
    # If no such area exists, create a new one
    if not area_item:
        area_item = {
            "city": venue.city,
            "state": venue.state,
            "venues": []
        }
        areas.append(area_item)
    
    # Create the venue dictionary
    v = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": 4  # Replace with a dynamic calculation if needed
    }
    
    # Add this venue to the list of venues for the area
    area_item['venues'].append(v)

  # Render the template and pass the areas data
  return render_template('pages/venues.html', areas=areas)
  
  # TODO: replace with real venues data. DONE!
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  
  #data = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()

  # Main query to get venue details along with the number of upcoming shows
  data = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  '''(
    db.session.query(
        Venue,
        func.count(Shows.id).label('upcoming_shows_count')
    )
    .outerjoin(Shows, (Shows.venue_id == Venue.id) & (Shows.start_time >= func.now()))
    .group_by(Venue.id)
  ).filter(Venue.name.ilike(f'%{search_term}%'))

  items = []
  for row in data:
     aux = {
        'name':row.name,
        "id":row.id,
        'genres':row.genres.split(','),
        'city':row.city,
        'state':row.state,
        'address':row.address,
        'website':row.website,
        'facebook_link':row.facebook_link,
        'seeking_talent':row.seeking_talent,
        'image_link':row.image_link,
        'upcoming_shows_count':row.upcoming_shows_count
     }
     items.append(aux)'''
  items = []
  for venue in data:
      upcoming_shows = []
      past_shows = []
      for show in venue.shows:
          if show.start_time >= datetime.now():
              upcoming_shows.append({
                  'artist_id': show.artist.id,
                  'artist_name': show.artist.name,
                  'artist_image_link': show.artist.image_link,
                  'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
              })
          if show.start_time < datetime.now():
              past_shows.append({
                  'artist_id': show.artist.id,
                  'artist_name': show.artist.name,
                  'artist_image_link': show.artist.image_link,
                  'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
              })
      
      aux = {
          'name': venue.name,
          "id": venue.id,
          'genres': venue.genres.split(','),
          'city': venue.city,
          'state': venue.state,
          'address': venue.address,
          'website': venue.website,
          'facebook_link': venue.facebook_link,
          'seeking_talent': venue.seeking_talent,
          'image_link': venue.image_link,
          'upcoming_shows_count': len(upcoming_shows),
          'upcoming_shows': upcoming_shows,
          'past_shows_count': len(past_shows)
      }
      items.append(aux)
  
  response = {
     "count": len(items),
     "data": items
     }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id - done!
  data = db.session.query(Venue).get(venue_id)
  venue_data = Venue.to_dict(data)
  
  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  error = False
  body = {}
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website = request.form.get('website_link')
    seeking_talent = request.form.get('seeking_talent') == 'y'
    seeking_description = request.form.get('seeking_description')

    new_venue = Venue(
    name = name,
    city = city,
    state = state,
    address = address,
    phone = phone,
    genres = genres,
    facebook_link = facebook_link,
    image_link = image_link,
    website = website,
    seeking_talent = seeking_talent,
    seeking_description = seeking_description
    )
    
    db.session.add(new_venue)
    
    db.session.commit()

    body['venue_name'] = new_venue.name
    flash(f'Venue {new_venue.name} was successfully listed!')  # Success message
    
  except Exception as e:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash(f'An error occurred. Venue {name} could not be listed. Error: {str(e)}')  # Error message for debugging

  finally:
      db.session.close()
  if not error:
     flash(f'Venue {new_venue.name} was successfully listed!')  # Success message
     #return jsonify({
     #   'new_venue':new_venue.name
     #})
  if error:
      #abort(400)
      return jsonify({"error":"Could not create venue"}), 400
  else:
      return render_template('pages/home.html')
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
     venue = Venue.query.get(id)
     Venue.query.filter_by(id = venue).delete()
     db.session.commit()
  except Exception as e:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash(f'An error occurred. Venue {venue} could not be deleted. Error: {str(e)}')  # Error message for debugging
  finally:
      db.session.close()
  if not error:
     flash(f'Venue {venue} was successfully deleted!')  # Success message
     #return jsonify({
     #   'new_venue':new_venue.name
     #})
  if error:
      #abort(400)
      return jsonify({"error":"Could not delete venue"}), 400
  else:
      return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return  render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data =db.session.query(Artist).order_by('state', 'city').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  data = (
    db.session.query(
        Artist.id,
        Artist.name,
        func.coalesce(
            db.session.query(func.count(Shows.id))
            .filter(Shows.artist_id == Artist.id)
            .filter(Shows.start_time >= func.now())
            .correlate(Artist)
            .scalar_subquery(),
            0
        ).label('num_upcoming_shows')
    )
    .filter(Artist.name.ilike(f'%{search_term}%'))
    .all()
    )
  #data = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  items=[]
  for row in data:
     aux = {
        "id":row.id,
        "name":row.name,
        "num_upcoming_shows":4 #len(row.shows)
     }
     items.append(aux)
  response={
    "count": len(items),
    "data": items
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = db.session.query(Artist).get(artist_id)
  venue_data = Artist.to_dict(data)
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = venue_data
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = db.session.query(Artist).filter_by(id = artist_id).first()
  form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  print(artist.name, artist.city)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  # CHE - switch the below data for ARTIST!
  error = False
  body = {}
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website = request.form.get('website_link')
    seeking_venue = request.form.get('seeking_venue') == 'y'
    seeking_description = request.form.get('seeking_description')

    edit_artist = Venue(
    name = name,
    city = city,
    state = state,
    phone = phone,
    genres = genres,
    facebook_link = facebook_link,
    image_link = image_link,
    website = website,
    seeking_venue = seeking_venue,
    seeking_description = seeking_description
    )
    
    db.session.add(edit_artist)

    db.session.commit()

    body['edite_venue'] = edit_artist.name
    flash(f'{edit_artist.name} was successfully edited!')  # Success message
  except Exception as e:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash(f'An error occurred. {name} could not be edited. Error: {str(e)}')  # Error message for debugging
    #db.session.rollback()

  finally:
    db.session.close()
    #return redirect(url_for('index'))
    # # venue record with ID <venue_id> using the new attributes
  
  if not error:
     flash(f'{edit_artist.name} was successfully edited!')  # Success message
     #return jsonify({
     #   'new_venue':new_venue.name
     #})
  
  if error:
      #abort(400)
      return jsonify({"error":"Could not edit Artist"}), 400
  
  else:
      #return render_template('pages/home.html')
      return redirect(url_for('show_artist', venue_id=artist_id))

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = db.session.query(Venue).filter_by(id=venue_id).first()
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  error = False
  body = {}
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website = request.form.get('website_link')
    seeking_talent = request.form.get('seeking_talent') == 'y'
    seeking_description = request.form.get('seeking_description')

    #print('completed', completed)
    edit_venue = Venue(
    name = name,
    city = city,
    state = state,
    address = address,
    phone = phone,
    facebook_link = facebook_link,
    image_link = image_link,
    website = website,
    seeking_talent = seeking_talent,
    seeking_description = seeking_description
    )
    
    db.session.add(edit_venue)

    db.session.commit()

    body['edite_venue'] = edit_venue.name
    flash(f'Venue {edit_venue.name} was successfully edited!')  # Success message
  except Exception as e:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash(f'An error occurred. Venue {name} could not be edited. Error: {str(e)}')  # Error message for debugging
    #db.session.rollback()

  finally:
    db.session.close()
    #return redirect(url_for('index'))
    # # venue record with ID <venue_id> using the new attributes
  
  if not error:
     flash(f'Venue {edit_venue.name} was successfully edited!')  # Success message
     #return jsonify({
     #   'new_venue':new_venue.name
     #})
  
  if error:
      #abort(400)
      return jsonify({"error":"Could not edit venue"}), 400
  
  else:
      #return render_template('pages/home.html')
      return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  body = {}
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website = request.form.get('website_link')
    seeking_venue = request.form.get('seeking_venue') == 'y'
    seeking_description = request.form.get('seeking_description')

    new_artist = Artist(
    name = name,
    city = city,
    state = state,
    genres = genres,
    phone = phone,
    facebook_link = facebook_link,
    image_link = image_link,
    website = website,
    seeking_venue = seeking_venue,
    seeking_description = seeking_description
    )
    
    db.session.add(new_artist)
    
    db.session.commit()

    body['venue_name'] = new_artist.name
    flash(f'Venue {new_artist.name} was successfully listed!')  # Success message
    
  except Exception as e:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash(f'An error occurred. Artist {name} could not be listed. Error: {str(e)}')  # Error message for debugging

  finally:
      db.session.close()
  if not error:
     flash(f'Aartist {new_artist.name} was successfully listed!')  # Success message
     #return jsonify({
     #   'new_venue':new_venue.name
     #})
  if error:
      #abort(400)
      return jsonify({"error":"Could not create venue"}), 400
  else:
      return render_template('pages/home.html')
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = db.session.query(Shows.artist_id, Shows.venue_id
                          , func.to_char(Shows.start_time, 'YYYY-MM-DD HH24:MI:SS').label('start_time')
                          ).all()
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  body = {}
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')
    
    upcoming_shows = Shows(
    artist_id = artist_id,
    venue_id = venue_id,
    start_time = start_time
    )
    
    db.session.add(upcoming_shows)
    
    db.session.commit()

    body['start_time'] = upcoming_shows.start_time
    flash(f'Show {upcoming_shows.start_time} was successfully listed!')  # Success message
    
  except Exception as e:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash(f'An error occurred. Show {start_time} could not be listed. Error: {str(e)}')  # Error message for debugging

  finally:
      db.session.close()
  if not error:
     flash(f'Aartist {upcoming_shows.start_time} was successfully listed!')  # Success message

  if error:
      #abort(400)
      return jsonify({"error":"Could not create venue"}), 400
  else:
      return render_template('pages/home.html')
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''