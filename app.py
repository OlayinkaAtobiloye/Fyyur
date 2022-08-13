#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import Venue, Artist, Show, db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.

#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
      date = dateutil.parser.parse(value)
  else:
      date = value
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
  recent_artists = Artist.query.order_by(Artist.date_created).limit(10).all()
  recent_venues = Venue.query.order_by(Venue.date_created).limit(10).all()
  return render_template('pages/home.html', recent_artists=recent_artists, recent_venues=recent_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  form = VenueForm()
  data = []
  venues = Venue.query.all()
  locations = set()
  for venue in venues:
      locations.add((venue.city, venue.state))
  for location in locations:
      data.append({
          "city": location[0],
          "state": location[1],
          "venues": []
      })
  for venue in venues:
      for loc in data:
          if loc['city'] == venue.city and loc['state'] == venue.state:
              upcoming_shows = Show.query.join(Venue).filter(Venue.id == venue.id).filter(
                  Show.start_time > datetime.utcnow())
              loc['venues'].append(
                  {'id': venue.id, 'name': venue.name, 'num_upcoming_shows': upcoming_shows.count()})
  return render_template('pages/venues.html', areas=data, form=form)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  form = VenueForm()
  search_keyword = request.form.get('search_term')
  data = (Venue.query.filter((Venue.city.ilike('%' + search_keyword + '%') |
                                      Venue.name.ilike('%' + search_keyword + '%') |
                                      Venue.state.ilike('%' + search_keyword + '%') )))

  return render_template('pages/search_venues.html', form=form, results=data, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  form = VenueForm()
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  upcoming_shows = Show.query.join(Venue).filter(Venue.id == venue_id).filter(Show.show_time > datetime.utcnow())
  past_shows = Show.query.join(Venue).filter(Venue.id == venue_id).filter(Show.show_time <= datetime.utcnow())
  return render_template('pages/show_venue.html', venue=venue, upcoming_shows=upcoming_shows, past_shows=past_shows)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate():
    try:
        venue_name = request.form.get("name")
        venue_city = request.form.get("city")
        venue_state = request.form.get("state")
        venue_address = request.form.get("address")
        venue_image_link = request.form.get("image_link")
        venue_facebook_link = request.form.get("facebook_link")
        venue_seeking_talent = True if request.form.get("seeking_talent") else False
        venue_seeking_description = request.form.get("seeking_description")
        venue = Venue(name=venue_name,
        facebook_link=venue_facebook_link,
            state=venue_state,
            city=venue_city,
            image_link=venue_image_link,
            seeking_talent=venue_seeking_talent, seeking_description=venue_seeking_description)
        db.session.add(venue)
        db.session.commit()
        flash(venue_name + ' was successfully listed!')
        return render_template('pages/home.html')
    except Exception as e:
         db.session.rollback()
         flash('An error occurred. Venue ' + request.form['name'] + f' could not be listed! {e}')
         return redirect(url_for('index'))
  else:
    flash(f'An error occurred, Please check form and try again')
    return redirect(url_for('index'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
     venue = Venue.query.get(venue_id)
     db.session.delete(venue)
  except Exception as e:
     db.session.rollback()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  form = ArtistForm()
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  form = ArtistForm()
  search_keyword = request.form.get('search_term')
  data = (Artist.query.filter((Artist.city.ilike('%' + search_keyword + '%') |
                                        Artist.name.ilike('%' + search_keyword + '%') |
                                        Artist.state.ilike('%' + search_keyword + '%') )))
  return render_template('pages/search_artists.html', form=form, results=data, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  upcoming_shows = Show.query.join(Artist).filter(Artist.id == artist_id).filter(Show.show_time > datetime.utcnow())
  past_shows = Show.query.join(Artist).filter(Artist.id == artist_id).filter(Show.show_time <= datetime.utcnow())
  return render_template('pages/show_artist.html', artist=artist, upcoming_shows=upcoming_shows, past_shows=past_shows)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm()
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.state.data = artist.state
    form.city.data = artist.state
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  if form.validate():
    try:
        artist_name = request.form.get("name")
        artist_city = request.form.get("city")
        artist_state = request.form.get("state")
        artist_address = request.form.get("address")
        artist_image_link = request.form.get("image_link")
        artist_facebook_link = request.form.get("facebook_link")
        artist_seeking_venue = True if request.form.get("seeking_venue") else False
        artist_seeking_description = request.form.get("seeking_description")
        artist.name = artist_name
        artist.image_link = artist_image_link
        artist.facebook_link = artist_facebook_link
        artist.seeking_venue = artist_seeking_venue
        artist.genres = request.form.getlist("genres")
        artist.seeking_description = artist_seeking_description
        artist.city = artist_city
        artist.state = artist_state
        artist.address = artist_address
        db.session.commit()
        flash(artist_name + ' was successfully updated!')
        return redirect(url_for('show_artist', artist_id=artist_id), form=form)
    except Exception as e:
         db.session.rollback()
         flash('Artist ' + request.form['name'] + f' could not be listed!')
         return redirect(url_for('show_artist', artist_id=artist_id), form=form)
  else:
    flash(f'An error occurred, Please check form and try again {artist}')
    return redirect(url_for('show_artist', artist_id=artist_id), form=form)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Artist.query.get(venue_id)
  form = VenueForm()
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.state.data = venue.state
  form.city.data = venue.state
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.seeking_venue.data = venue.seeking_venue
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
 form = VenueForm(request.form)
 venue = Venue.query.get(venue_id)
 if form.validate():
    try:
        venue.name = request.form.get("name")
        venue.image_link = request.form.get("image_link")
        venue.facebook_link = request.form.get("facebook_link")
        venue.seeking_venue = True if request.form.get("seeking_venue") else False
        venue.genres = request.form.getlist("genres")
        venue.seeking_description = request.form.get("seeking_description")
        venue.city = request.form.get("city")
        venue.state = request.form.get("state")
        venue.address = request.form.get("address")
        db.session.commit()
        flash(artist_name + ' was successfully updated!')
        return redirect(url_for('show_venue', venue_id=venue_id))
    except Exception as e:
         db.session.rollback()
         flash('Artist ' + request.form['name'] + f' could not be listed!')
         return redirect(url_for('show_venue', venue_id=venue_id), form=form)
 else:
    flash(f'An error occurred, Please check form and try again')
    return redirect(url_for('show_venue', venue_id=venue_id), form=form)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form)
  if form.validate():
      try:
          artist_id = request.form.get("id")
          artist_name = request.form.get("name")
          artist_city = request.form.get("city")
          artist_state = request.form.get("state")
          artist_address = request.form.get("address")
          artist_image_link = request.form.get("image_link")
          artist_facebook_link = request.form.get("facebook_link")
          artist_looking_for_venues = True if request.form.get("seeking_venue") else False
          artist_seeking_description = request.form.get("seeking_description")
          artist = Artist(id=artist_id, name=artist_name,
          facebook_link=artist_facebook_link,
          state=artist_state,
          city=artist_city,
          image_link=artist_image_link,
          seeking_venue=artist_looking_for_venues, seeking_description=artist_seeking_description)
          db.session.add(artist)
          db.session.commit()
          flash(artist_name + ' was successfully listed!')
          return render_template('pages/home.html')
      except Exception as e:
           db.session.rollback()
           flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed!')
           return redirect(url_for('index'))
  else:
       flash(f'An error occurred, Please check form and try again')
       return redirect(url_for('index'))



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm(request.form)
  if form.validate():
      try:
          artist_id = request.form.get("artist_id")
          venue_id = request.form.get("venue_id")
          start_time = request.form.get("start_time")
          show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
          db.session.add(show)
          db.session.commit()
          flash('Show was successfully listed!')
          return render_template('pages/home.html')
      except Exception as e:
          db.session.rollback()
          flash(f'An error occurred. Show could not be listed!{e}')
          return redirect(url_for('index'))
  else:
      flash(f'An error occurred, Please check form and try again')
      return redirect(url_for('index'))




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
