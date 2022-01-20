from pds_pipelines.db import db_connect
from pds_pipelines.models.upc_models import Instruments
from pds_pipelines.config import upc_db, summaries_path
import os
import json
import argparse

queries = {
    'volume_summary': """
        SELECT d.instrumentid, d.targetid, t.targetname, t.system, i.instrument, i.mission, i.spacecraft, i.displayname,
        count(d.*) as image_count, min(s.starttime) as start_date, max(s.starttime) as stop_date, max(s.processdate) as publish_date, min(s.solarlongitude) as min_solar_longitude, max(s.solarlongitude) as max_solar_longitude, min(s.meangroundresolution) as min_mean_ground_resolution, max(s.meangroundresolution) as max_mean_ground_resolution, min(s.minimumphase) as min_minimum_phase, max(s.minimumphase) as max_minimum_phase, min(s.maximumphase) as min_maximum_phase, max(s.maximumphase) as max_maximum_phase, min(s.minimumincidence) as min_minimum_incidence, max(s.minimumincidence) as max_minimum_incidence, min(s.maximumincidence) as min_maximum_incidence, max(s.maximumincidence) as max_maximum_incidence, min(s.minimumemission) as min_minimum_emission, max(s.minimumemission) as max_minimum_emission, min(s.maximumemission) as min_maximum_emission, max(s.maximumemission) as max_maximumemission
        FROM datafiles d
        JOIN instruments i on (i.instrumentid=d.instrumentid)
        JOIN targets t on (t.targetid=d.targetid)
        JOIN search_terms s on (d.upcid=s.upcid)
        GROUP by d.instrumentid, i.instrument, i.mission, i.spacecraft, d.targetid, t.targetname, t.system, i.displayname
        """,
   'target_summary': """
       SELECT s2.displayname, s2.system, s1.target_count
       FROM
       (SELECT d.targetid, count(d.*) as target_count from datafiles d
       GROUP BY d.targetid) s1
       JOIN
       (SELECT t.targetid, t.displayname, t.system from targets t) s2
       on s1.targetid = s2.targetid
    """
}

band_summary_query ="""
        SELECT DISTINCT i.instrumentid, i.instrument,
        j.jsonkeywords -> 'caminfo' -> 'isislabel' -> 'isiscube' -> 'bandbin' ->> 'filtername' AS filtername,
        j.jsonkeywords -> 'caminfo' -> 'isislabel' -> 'isiscube' -> 'bandbin' -> 'center' ->> 0 AS center
        FROM datafiles d
        JOIN json_keywords j on (d.upcid = j.upcid)
        JOIN instruments i on (i.instrumentid in (SELECT instrumentid FROM instruments WHERE instruments.mission = '{0}'))
        WHERE  d.instrumentid in (SELECT instrumentid FROM instruments WHERE instruments.mission = '{0}')
        """

def parse_args():
    parser = argparse.ArgumentParser(description='Create view JSONs.')

    parser.add_argument('--path', '-p', dest="path", required=False,
                        help="Enter path - where to write the JSONs.")

    args = parser.parse_args()
    return args


def main(user_args):
    if user_args.path:
        path = user_args.path
    else:
        path = summaries_path

    Session, _ = db_connect(upc_db)
    session = Session()

    missions = [i.mission for i in session.query(Instruments).distinct(Instruments.mission).all()]

    session.close()

    for mission in missions:
        queries['band_summary_{}'.format(mission.lower().replace(" ", "_"))] = band_summary_query.format(mission)

    for key in queries:
        json_query = "with t AS ({}) SELECT json_agg(t) FROM t;".format(queries[key])
        print("Beginning {} Query".format(key))

        session = Session()
        output = session.execute(json_query)
        session.close()

        print("Finished {} Query".format(key))
        json_output = json.dumps([dict(line) for line in output])

        print("Writing Json for {}".format(key))
        with open(os.path.join(path, key + ".json"), "w") as json_file:
            json_file.write(json_output)
        print("Finished view generation for {}".format(key))

if __name__ == "__main__":
    main(parse_args())
