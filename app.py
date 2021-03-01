#### Initial Setup
# Import Dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

# Save References
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

#########################################

#### Flask Routes

# Welcome Page
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Welcome to the Climate App API for Honolulu, Hawaii!<br/>"
        f"<br/>"
        f"The following are the available routes for this API:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


# Precipitation Page
## Bring in the corresponding query from climate.ipynb
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    # Query for last year derived from climate.ipynb
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()

    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    all_prcp = []
    for date, prcp in last_year_data:
        if prcp != None:
            prcp_dict = {}
            prcp_dict[date] = prcp
            all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

# Stations page
## Bring in the corresponding query form climate.ipynb
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    #Query for station information derived from climate.ipynb
    stations = session.query(Station.station, Station.name, Station.latitude, 
    Station.longitude, Station.elevation).all()

    session.close()

    all_stations =[]
    for station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)
    
    return jsonify(all_stations)



# TOBS page
## Bring in the corresponding query form climate.ipynb
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    #Query for TOBS information derived from climate.ipynb

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()


    (most_active_station_id, ) = most_active_station
    most_active_station_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), 
                                            func.avg(Measurement.tobs)).filter(Measurement.station == most_active_station_id).all()


    station_last_year_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last_year).filter(Measurement.station == most_active_station_id)

    session.close()

    all_tobs=[]
    for date, temp in station_last_year_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["temp"] = temp
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

# Start and Start/End pages
## Bring in the corresponding query form climate.ipynb

@app.route('/api/v1.0/<start>', defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def temps_start_end(start, end):
    session = Session(engine)

    # If we have both a start date and an end date.
    if end != None:
        tobs_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(
            Measurement.date <= end).all()
    # If we only have a start date.
    else:
        tobs_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    session.close()

    # Convert the query results to a list.
    tobs_list = []
    no_tobs = False
    for min_temp, avg_temp, max_temp in temperature_data:
        if min_temp == None or avg_temp == None or max_temp == None:
            no_tobs = True
        tobs_list.append(min_temp)
        tobs_list.append(avg_temp)
        tobs_list.append(max_temp)
    # Return the JSON representation of dictionary.
    if no_tobs == True:
        return f"No temperature data found for the given date range. Try another date range."
    else:
        return jsonify(tobs_list)


if __name__ == '__main__':
    app.run(debug=True)
