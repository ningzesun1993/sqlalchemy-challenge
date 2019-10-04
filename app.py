from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from datetime import datetime

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
def calc_temps(start_date, end_date = '2017-08-23'):
    """TMIN, TAVG, and TMAX for a list of dates.

    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d

    Returns:
        TMIN, TAVE, and TMAX
    """
    print("start_date = ", start_date)
    try:
        session = Session(engine)
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)). \
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        session.close()
        return results
    except Exception as e:
        print("{}: {}".format(type(e), str(e)))
        return ['it is not a valid date formate, it should be YYYY-MM-DD']


@app.route("/")
def welcome():
    return (
        f"Welcome to SQLAlchemy Homework!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/start-day<br/>'
        f'/api/v1.0/start-day/end-day'

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prec = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    result = {}
    for i in prec:
        result[i[0]] = i[1]
    return jsonify(result), 404

@app.route("/api/v1.0/tobs")
def temp():
    select = [Measurement.date, Measurement.tobs]
    # Calculate the date 1 year ago from the last data point in the database
    session = Session(engine)
    target_date = session.query(select[0]).order_by((func.strftime("%Y-%m-%d", Measurement.date).desc())).first()
    target_date_new = target_date[0]
    target_date = target_date_new[:3] + str(eval(target_date_new[3]) - 1) + target_date_new[4:]
    # Perform a query to retrieve the data and precipitation scores
    # Sort the dataframe by date
    date_prec = session.query(select[1]).filter(func.strftime("%Y-%m-%d", Measurement.date) > target_date) \
        .order_by(func.strftime("%Y-%m-%d", Measurement.date)).all()
    session.close()
    result = []
    for i in date_prec:
        result.append(i[0])
    return jsonify(result), 404

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    stat = session.query(Station.station).all()
    session.close()
    result = []
    for i in stat:
        result.append(i[0])
    return jsonify(result), 404

@app.route("/api/v1.0/<start>")
def start_day(start):
    start = str(start)
    return jsonify(calc_temps(start)), 200

@app.route("/api/v1.0/<start>/<end>")
def start_end_day(start, end):
    return jsonify(calc_temps(start_date = start, end_date = end)), 404

if __name__ == "__main__":
    app.run(debug=True)
