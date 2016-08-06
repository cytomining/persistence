"""

"""

import logging
import perturbation.base
import perturbation.models
import perturbation.seed_images
import perturbation.seed_objects
import perturbation.UUID
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import sqlalchemy.types

logger = logging.getLogger(__name__)


def setup(connection):
    """

    :param connection:

    :return:

    """

    Session = sqlalchemy.orm.sessionmaker()

    scoped_session = sqlalchemy.orm.scoped_session(Session)

    engine = sqlalchemy.create_engine(connection)

    scoped_session.remove()

    scoped_session.configure(autoflush=False, bind=engine, expire_on_commit=False)

    return scoped_session, engine


def seed(config, input, output=None, session=None, stage="images", sqlfile=None):
    """Call functions to create backend

    :param config:
    :param input: if stage is `images`, then top-level directory containing sub-directories, each of which have an
    image.csv and object.csv; if stage is "objects", then a subdirectory contain a pair of image.csv and object.csv
    :param output: name of SQLlite/PostGreSQL database
    :param session:
    :param stage: `images` or `objects`
    :param sqlfile: SQL file to be executed on the backend database after it is created

    :return:

    """
    assert (session is not None) != (output is not None)

    if session is None:
        scoped_session, engine = setup(output)
    else:
        scoped_session = session

        engine = scoped_session.connection().engine

    if stage == "images":

        Base = perturbation.base.Base

        Base.metadata.drop_all(engine)

        Base.metadata.create_all(engine)

        logger.debug("Parsing SQL file")

        if sqlfile:
            create_views(sqlfile, engine)

    logger.debug("Parsing csvs")

    if stage == "images":
        perturbation.seed_images.seed(config, input, scoped_session)
    elif stage == "objects":
        perturbation.seed_objects.seed(config, input, scoped_session)
    else:
        raise ValueError("Unknown stage {}".format(stage))


def create_views(sqlfile, engine):
    """

    :param sqlfile:
    :param engine:

    :return:

    """
    with open(sqlfile) as f:
        import sqlparse

        for s in sqlparse.split(f.read()):
            engine.execute(s)






