# PDS-Pipelines
A combination of PDS software for data integrity, universal planetary coordinates, ingestion, services (POW/MAP2), etc.


## Using PDS-Pipelines Locally

PDS-Pipelines is current not available via anaconda or other distribution
platforms. PDS-Pipelines also requires anaconda, and docker. This use case is
largely developer centric and will get technical with the tools used to run
PDS-Pipelines

First cd into the cloned repository, and run:

  conda env create -f environment.yml

This will create a fresh environment called PDS-Pipelines. Then activate said
environment with:

  conda activate PDS-Pipelines

You'll then want to actually install PDS-Pipelines with the following:

  python setup.py develop

Following this run the following to setup the docker containers:

  cd containers
  export /Path/to/the/database docker-compose up

The path you specify should either be an existing folder that a UPC database has
been before or to an empty file for a new database to be written.

From here you can do one of two things, start processing data, or manually create
the databases that UPC, MAP and POW2 depend on. It's recommended that you start
by manually creating the databases as there are a few other idiosyncrasies that
crop up while running locally.

First run the following in a python instance with the above anaconda env
activated:

  from pds_pipelines.models import upc_models, pds_models
  upc_models.create_upc_database()
  pds_models.create_pds_database()

This creates the necessary databases for both the di database and the upc database,
from here things get a little more complicated. Within the PDS-Pipelines repo
there is a file title `PDSinfo.json`. This file maps various missions/instruments
to known archive within the di database. Here is an example record within the json
file:

  "mro_ctx":
  {
    "archiveid": "16",
    "path": "/pds_san/PDS_Archive/Mars_Reconnaissance_Orbiter/CTX/",
    "mission": "CTX",
    "bandbinQuery" : "FilterName",
    "upc_reqs": ["/data/", ".IMG"]
  }

As you can see, you probably don't have the above path on your computer. To gain
access to these files you will need to mirror the PDS_Archive that is maintained
by various entities (such as the USGS). Some images that the PDS_Archive maintains
can be found [here](https://pds-imaging.jpl.nasa.gov/volumes/). From here you will
need to extract files from there respective missions/instruments into the path
defined in the PDSinfo.json. You can do this one of two ways, either mirror the
paths defined in the PDSinfo.json for the mission you are working with, OR you
can update the path in the PDSinfo.json to point to where you have downloaded
files. The latter is much easier but will likely not be able to take advantage
of features supported by the pipelines.

Option 1 Example (Using CTX and the above PDS nodes):

Navigate to the following:

  https://pdsimage2.wr.usgs.gov/archive/mro-m-ctx-2-edr-l0-v1.0/mrox_0602/data/

Pull an image from the archive, lets pick P20_008794_2573_XN_77N268W.IMG. The
first image in the volumn.

Now we make the above file structure:

  mkdir -p /pds_san/PDS_Archive/Mars_Reconnaissance_Orbiter/CTX/

Ideally, working at the root level should only be done on a personal system.

Now we move the file we have pulled to this location:

  mv /Your/Downloads/Folder/P20_008794_2573_XN_77N268W.IMG /pds_san/PDS_Archive/Mars_Reconnaissance_Orbiter/CTX/

  or

  wget -O /pds_san/PDS_Archive/Mars_Reconnaissance_Orbiter/CTX/P20_008794_2573_XN_77N268W.IMG https://pdsimage2.wr.usgs.gov/archive/mro-m-ctx-2-edr-l0-v1.0/mrox_0602/data/P20_008794_2573_XN_77N268W.IMG

Option 2 Example (Using CTX and the above PDS nodes):

  Either download the files to your downloads and move it to a new directory
  or wget it directly to your new directory like:

  wget -O /Path/to/CTX/area/P20_008794_2573_XN_77N268W.IMG https://pdsimage2.wr.usgs.gov/archive/mro-m-ctx-2-edr-l0-v1.0/mrox_0602/data/P20_008794_2573_XN_77N268W.IMG

Then update the PDSinfo.json record to the following:

  "mro_ctx":
  {
    "archiveid": "16",
    "path": "/Path/to/CTX/area/",
    "mission": "CTX",
    "bandbinQuery" : "FilterName",
    "upc_reqs": ["/data/", ".IMG"]
  }

Ideally, if you have done either of the above two options, you will now be able
run both di_queueing.py then di_proces.py in the following manor:
