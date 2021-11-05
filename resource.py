""" dealing with getting what CKAN resource this grader should go through

1. API (&& valid URL) -- if invalid URL, update to "F" grade
2. Other formats (e.g. zip, csv, text, xlsx, ...)

"""
from db import Database


def get_valid_api_resources():
    """Get CKAN valid resources easy way. no verification required.
    * Resource with API as type
    * URL with http as prefix

    return db.fetchall()
    """
    db = Database()
    query = """SELECT id, package_id, grade, name, format, url
    FROM resource
    WHERE format = 'API' AND url LIKE 'http%'
    ORDER BY last_modified;
    """
    return db.fetchall_by_query(query)


def get_invalid_api_resources():
    """Get CKAN invalid resources easy way. no verification required.
    * Resource with API as type
    * URL doesn't start with 'http'

    return db.fetchall()
    """
    db = Database()
    query = """SELECT id, package_id, grade, format, url
    FROM resource
    WHERE format = 'API' AND url NOT LIKE 'http%'
    ORDER BY last_modified;
    """
    return db.fetchall_by_query(query)


def get_other_resources(format=None):
    """GET CKAN resource which is not API

    return db.fetchall()
    """
    db = Database()
    where_args = ""
    if format is not None:
        where_args = f" AND format = {format}"
    query = f"""SELECT id, package_id, grade, name, format, mimetype
    FROM resource
    WHERE format != 'API' {where_args}
    ORDER BY last_modified;
    """
    return db.fetchall_by_query(query)
