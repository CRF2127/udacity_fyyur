#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
#import dateutil.parser
#from dateutil import parser
#import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
#from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
#moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    #city = db.Column(db.String(120))
    #state = db.Column(db.String(120))
    areas_id = db.Column(db.Integer, db.ForeignKey('Areas.id'), nullable = False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, unique=False, default=True)
    seeking_description = db.Column(db.String(1500))
    website = db.Column(db.String(120))
    children = db.relationship('Show', backref='show', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # Method to serialize the object to a dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
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
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, unique=False, default=True)
    seeking_description = db.Column(db.String(1500))
    children = db.relationship('Shows', backref='shows', lazy=True)

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
class Areas(db.Model):
  __tablename__ = 'Areas'
  
  id = db.Column(db.Integer, primary_key=True)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  children = db.relationship('Venue', backref='Venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # not sure if this is required
  def __repr__(self):
    return f'<Venue {self.id}, {self.city}, {self.state}>'
    
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Shows(db.Model):
  __tablename__ = "Shows"

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
  show_date = db.Column(db.Date)
  show_time = db.Column(db.Time)

  def to_dict(self):
    return {
      'id': self.id,
      'venue_id': self.venue_id,
      'artist_id': self.artist_id,
      'show_date': self.show_date,
      'show_time': self.show_time
    }
  
  def __repr__(self):
    return f'<Shows {self.id}, {self.show_date}, {self.show_time}>'
  
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

  data=db.session.query(Areas, Venue).join(Venue).order_by('city', 'state', 'name').all()
  for area, venue in data:
    area_item = {}
    pos_area = 0
    if len(areas) == 0:
      pos_area = 0
      area_item = {
        "city": area.city,
        "state": area.state,
        "venues": []
      }
      areas.append(area_item)
    else:
      for i, existing_area in enumerate(areas):
        if existing_area['city'] == area.city and existing_area['state'] == venue.state:
          pos_area = i
          break

      if pos_area < 0:
        area_item = {
          "city": area.city,
          "state": area.state,
          "venues": []
        }
        areas.append(area_item)
        pos_area = len(areas) - 1
      else:
        area_item = areas[pos_area]

    v = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": 4 #calculate this dynamically later
      }
    
    area_item['venues'].append(v)
    areas[pos_area] = area_item

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
  #data = db.session.query(Areas, Venue).join(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  items = []
  for row in data:
     aux = {
        "id":row.id,
        "name":row.name,
        'address':row.address,
        "num_upcoming_shows":4 #len(row.shows)
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
  # TODO: replace with real venue data from the venues table, using venue_id
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
  '''try:
    name = request.get_json()['name']
    grain_name = dim_grain(name=name)
    db.session.add(grain_name)
    db.session.commit()
    return jsonify({
       name:grain_name.name
       })
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      abort(400)
  else:
      return jsonify({
            'name':grain.name
      })'''
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
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
