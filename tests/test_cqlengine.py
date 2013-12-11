from __future__ import with_statement
from tests import op_fixture, db_for_dialect, eq_, staging_env, \
            clear_staging_env, _cqlengine_testing_config,\
            capture_context_buffer, requires_07, write_script
from unittest import TestCase
from cqlengine import DateTime, Column, Text, Integer
#from sqlalchemy import DateTime, MetaData, Table, Column, text, Integer, String
#from sqlalchemy.engine.reflection import Inspector
from alembic import command, util
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory

class CQLEngineBasicTest(TestCase):

    def setUp(self):
        env = staging_env(template='cqlengine')
        self.cfg = cfg = _cqlengine_testing_config()

        #self.rid = rid = util.rev_id()

        #self.script = script = ScriptDirectory.from_config(cfg)
        #script.generate_revision(rid, None, refresh=True)
        #script.generate_revision(None, None, refresh=True)
        self.write_scripts()

    def tearDown(self):
        clear_staging_env()


#    def _first_script(self):
#        write_script(self.script, self.rid, """
#revision = '%s'
#down_revision = None
#
#import uuid
#from cqlengine import columns, management, models
#
#class TestTable(models.Model):
#    __table_name__ = 'test_table'
#    partition = columns.Text(primary_key=True)
#    uuid = columns.UUID(primary_key=True, default=uuid.uuid4)
#    title = columns.Text()
#
#def upgrade():
#    management.create_table(TestTable)
#
#def downgrade():
#    management.drop_table(TestTable)
#
#""" % self.rid)
#
#    def _second_script(self):
#        write_script(self.script, self.rid, """
#revision = '%s'
#down_revision = None
#
#import uuid
#from alembic.ddl.cqe import add_column
#from cqlengine import columns, management, models
#
#class TestTable(models.Model):
#    __table_name__ = 'test_table'
#    partition = columns.Text(primary_key=True)
#    uuid = columns.UUID(primary_key=True, default=uuid.uuid4)
#    title = columns.Text()
#    new_col = columns.Float()
#
#def upgrade():
#    add_column(TestTable, 'new_col')
#
#def downgrade():
#    pass
#
#""" % self.rid)
    def write_scripts(self):
        self.a = util.rev_id()
        self.b = util.rev_id()
        self.c = util.rev_id()

        script = ScriptDirectory.from_config(self.cfg)
        script.generate_revision(self.a, None, refresh=True)
        write_script(script, self.a, """
    revision = '%s'
    down_revision = None

    from alembic import op

    def upgrade():
        pass
        #op.execute("CREATE TABLE foo(id integer)")

    def downgrade():
        pass
        #op.execute("DROP TABLE foo")

    """ % self.a)

        script.generate_revision(self.b, None, refresh=True)
        write_script(script, self.b, """
    revision = '%s'
    down_revision = '%s'

    from alembic import op

    def upgrade():
        pass
        #op.execute("CREATE TABLE bar(id integer)")

    def downgrade():
        pass
        #op.execute("DROP TABLE bar")

    """ % (self.b, self.a))

        script.generate_revision(self.c, None, refresh=True)
        write_script(script, self.c, """
    revision = '%s'
    down_revision = '%s'

    from alembic import op

    def upgrade():
        pass
        #op.execute("CREATE TABLE bat(id integer)")

    def downgrade():
        pass
        #op.execute("DROP TABLE bat")

    """ % (self.c, self.b))


    def test_upgrade(self):
        print '--call upgrade-1-'
        command.upgrade(self.cfg, self.a)
        print 'ooo{}ooo'.format(self.a)
        print 'ooo{}ooo'.format(self.b)
        print '--call upgrade-2-'
        command.upgrade(self.cfg, self.b)
        #command.upgrade(self.cfg, self.c)
        #assert "CREATE TYPE pgenum AS ENUM ('one','two','three')" in buf.getvalue()
        #assert "CREATE TABLE sometable (\n    data pgenum\n)" in buf.getvalue()
    #
    #def test_002_upgrade(self):
    #    command.upgrade(self.cfg, c)
    #    db = sqlite_db()
    #    assert db.dialect.has_table(db.connect(), 'foo')
    #    assert db.dialect.has_table(db.connect(), 'bar')
    #    assert db.dialect.has_table(db.connect(), 'bat')
    #
    #def test_003_downgrade(self):
    #    command.downgrade(self.cfg, a)
    #    db = sqlite_db()
    #    assert db.dialect.has_table(db.connect(), 'foo')
    #    assert not db.dialect.has_table(db.connect(), 'bar')
    #    assert not db.dialect.has_table(db.connect(), 'bat')
    #
    #def test_004_downgrade(self):
    #    command.downgrade(self.cfg, 'base')
    #    db = sqlite_db()
    #    assert not db.dialect.has_table(db.connect(), 'foo')
    #    assert not db.dialect.has_table(db.connect(), 'bar')
    #    assert not db.dialect.has_table(db.connect(), 'bat')
    #
    #def test_005_upgrade(self):
    #    command.upgrade(self.cfg, b)
    #    db = sqlite_db()
    #    assert db.dialect.has_table(db.connect(), 'foo')
    #    assert db.dialect.has_table(db.connect(), 'bar')
    #    assert not db.dialect.has_table(db.connect(), 'bat')
    #
    #def test_006_upgrade_again(self):
    #    command.upgrade(self.cfg, b)
    #
    #
    ## TODO: test some invalid movements
    #
    #@classmethod
    #def setup_class(cls):
    #    cls.env = staging_env()
    #    cls.cfg = _sqlite_testing_config()
    #
    #@classmethod
    #def teardown_class(cls):
    #    clear_staging_env()