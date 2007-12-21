# -*- coding: utf-8 -*-
"""
TracFullBlogPlugin: The code managing the database setup and upgrades.

License: BSD

(c) 2007 ::: www.CodeResort.com - BV Network AS (simon-code@bvnetwork.no)
"""

from trac.core import *
from trac.db.schema import Table, Column, Index
from trac.env import IEnvironmentSetupParticipant

__all__ = ['FullBlogSetup']

# Database version identifier for upgrades.
db_version = 1

# Database schema
schema = [
    # Blog posts
    Table('fullblog_posts', key=('name', 'version'))[
        Column('name'),
        Column('version', type='int'),
        Column('title'),
        Column('body'),
        Column('publish_time', type='int'),
        Column('version_time', type='int'),
        Column('version_comment'),
        Column('version_author'),
        Column('author'),
        Column('categories')],
    # Blog comments
    Table('fullblog_comments', key=('name', 'number'))[
        Column('name'),
        Column('number', type='int'),
        Column('comment'),
        Column('author'),
        Column('time', type='int')],
]

# Create tables

def to_sql(env, table):
    """ Convenience function to get the to_sql for the active connector."""
    from trac.db.api import DatabaseManager
    dm = env.components[DatabaseManager]
    dc = dm._get_connector()[0]
    return dc.to_sql(table)

def create_tables(cursor, env):
    """ Creates the basic tables as defined by schema.
    using the active database connector. """
    for table in schema:
        for stmt in to_sql(env, table):
            cursor.execute(stmt)
    cursor.execute("INSERT into system values ('fullblog_version', '1')")
    cursor.execute("INSERT into system values ('fullblog_infotext', '')")

# Upgrades

pass

# Component that deals with database setup

class FullBlogSetup(Component):
    """Component that deals with database setup and upgrades."""
    
    implements(IEnvironmentSetupParticipant)

    def environment_created(self):
        """Called when a new Trac environment is created."""
        pass

    def environment_needs_upgrade(self, db):
        """Called when Trac checks whether the environment needs to be upgraded.
        Returns `True` if upgrade is needed, `False` otherwise."""
        cursor = db.cursor()
        return self._get_version(cursor) != db_version

    def upgrade_environment(self, db):
        """Actually perform an environment upgrade, but don't commit as
        that is done by the common upgrade procedure when all plugins are done."""
        cursor = db.cursor()
        if self._get_version(cursor) == 0:
            create_tables(cursor, self.env)
        else:
            # do upgrades here when we get to that...
            pass

    def _get_version(self, cursor):
        try:
            sql = "SELECT value FROM system WHERE name='fullblog_version'"
            self.log.debug(sql)
            cursor.execute(sql)
            for row in cursor:
                return int(row[0])
            return 0
        except:
            return 0