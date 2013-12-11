from __future__ import with_statement
from alembic import context
from alembic.ddl.cqe import ConnectionProxy
from cqlengine.connection import setup
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# note: cqlengine does not support autogenerate at this time
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    settings = config.get_section(config.config_ini_section)
    hosts = settings['cqlengine.hosts']
    keyspace = settings['cqlengine.keyspace']

    # cqlengine uses a global setup that is shared by any usage of the module.
    setup(hosts, default_keyspace=keyspace)
    # ConnectionProxy talks to the global cqlengine connection.
    context.configure(
                connection=ConnectionProxy,
                target_metadata=target_metadata
                )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        ConnectionProxy.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

