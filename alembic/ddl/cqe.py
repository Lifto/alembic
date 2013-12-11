from alembic.ddl.impl import DefaultImpl

class CQLEngineImpl(DefaultImpl):
    __dialect__ = 'cqlengine'

    def static_output(self, text):
        self.output_buffer.write(text + "\n\n")

    @property
    def bind(self):
        raise NotImplementedError

    def _exec(self, construct, execution_options=None,
                            multiparams=(),
                            params=None):#util.immutabledict()):
        raise NotImplementedError
        #if isinstance(construct, basestring):
        #    construct = text(construct)
        #if self.as_sql:
        #    if multiparams or params:
        #        # TODO: coverage
        #        raise Exception("Execution arguments not allowed with as_sql")
        #    self.static_output(unicode(
        #            construct.compile(dialect=self.dialect)
        #            ).replace("\t", "    ").strip() + self.command_terminator)
        #else:
        #    conn = self.connection
        #    if execution_options:
        #        conn = conn.execution_options(**execution_options)
        #    conn.execute(construct, *multiparams, **params)

    def execute(self, sql, execution_options=None):
        raise NotImplementedError
        #self._exec(sql, execution_options)

    def alter_column(self, table_name, column_name,
                        nullable=None,
                        server_default=False,
                        name=None,
                        type_=None,
                        schema=None,
                        autoincrement=None,
                        existing_type=None,
                        existing_server_default=None,
                        existing_nullable=None,
                        existing_autoincrement=None
                    ):
        raise NotImplementedError
        if autoincrement is not None or existing_autoincrement is not None:
            util.warn("nautoincrement and existing_autoincrement only make sense for MySQL")
        if nullable is not None:
            self._exec(base.ColumnNullable(table_name, column_name,
                                nullable, schema=schema,
                                existing_type=existing_type,
                                existing_server_default=existing_server_default,
                                existing_nullable=existing_nullable,
                                ))
        if server_default is not False:
            self._exec(base.ColumnDefault(
                                table_name, column_name, server_default,
                                schema=schema,
                                existing_type=existing_type,
                                existing_server_default=existing_server_default,
                                existing_nullable=existing_nullable,
                            ))
        if type_ is not None:
            self._exec(base.ColumnType(
                                table_name, column_name, type_, schema=schema,
                                existing_type=existing_type,
                                existing_server_default=existing_server_default,
                                existing_nullable=existing_nullable,
                            ))
        # do the new name last ;)
        if name is not None:
            self._exec(base.ColumnName(
                                table_name, column_name, name, schema=schema,
                                existing_type=existing_type,
                                existing_server_default=existing_server_default,
                                existing_nullable=existing_nullable,
                            ))

    def add_column(self, table_name, column):
        raise NotImplementedError
        self._exec(base.AddColumn(table_name, column))

    def drop_column(self, table_name, column, **kw):
        raise NotImplementedError
        self._exec(base.DropColumn(table_name, column))

    def add_constraint(self, const):
        raise NotImplementedError
        if const._create_rule is None or \
            const._create_rule(self):
            self._exec(schema.AddConstraint(const))

    def drop_constraint(self, const):
        raise NotImplementedError
        self._exec(schema.DropConstraint(const))

    def rename_table(self, old_table_name, new_table_name, schema=None):
        raise NotImplementedError
        self._exec(base.RenameTable(old_table_name,
                    new_table_name, schema=schema))

    def create_table(self, table):
        if util.sqla_07:
            table.dispatch.before_create(table, self.connection,
                                        checkfirst=False,
                                            _ddl_runner=self)
        self._exec(schema.CreateTable(table))
        if util.sqla_07:
            table.dispatch.after_create(table, self.connection,
                                        checkfirst=False,
                                            _ddl_runner=self)
        for index in table.indexes:
            self._exec(schema.CreateIndex(index))

    def drop_table(self, table):
        self._exec(schema.DropTable(table))

    def create_index(self, index):
        self._exec(schema.CreateIndex(index))

    def drop_index(self, index):
        self._exec(schema.DropIndex(index))

    def bulk_insert(self, table, rows):
        if not isinstance(rows, list):
            raise TypeError("List expected")
        elif rows and not isinstance(rows[0], dict):
            raise TypeError("List of dictionaries expected")
        if self.as_sql:
            for row in rows:
                self._exec(table.insert(inline=True).values(**dict(
                    (k, _literal_bindparam(k, v, type_=table.c[k].type))
                    for k, v in row.items()
                )))
        else:
            # work around http://www.sqlalchemy.org/trac/ticket/2461
            if not hasattr(table, '_autoincrement_column'):
                table._autoincrement_column = None
            self._exec(table.insert(inline=True), multiparams=rows)

    def compare_type(self, inspector_column, metadata_column):

        conn_type = inspector_column['type']
        metadata_type = metadata_column.type

        metadata_impl = metadata_type.dialect_impl(self.dialect)

        # work around SQLAlchemy bug "stale value for type affinity"
        # fixed in 0.7.4
        metadata_impl.__dict__.pop('_type_affinity', None)

        if conn_type._compare_type_affinity(
                            metadata_impl
                        ):
            comparator = _type_comparators.get(conn_type._type_affinity, None)

            return comparator and comparator(metadata_type, conn_type)
        else:
            return True

    def compare_server_default(self, inspector_column,
                            metadata_column,
                            rendered_metadata_default):
        conn_col_default = inspector_column['default']
        return conn_col_default != rendered_metadata_default

    def start_migrations(self):
        """A hook called when :meth:`.EnvironmentContext.run_migrations`
        is called.

        Implementations can set up per-migration-run state here.

        """

    def emit_begin(self):
        """Emit the string ``BEGIN``, or the backend-specific
        equivalent, on the current connection context.

        This is used in offline mode and typically
        via :meth:`.EnvironmentContext.begin_transaction`.

        """
        raise NotImplementedError
        self.static_output("BEGIN" + self.command_terminator)

    def emit_commit(self):
        """Emit the string ``COMMIT``, or the backend-specific
        equivalent, on the current connection context.

        This is used in offline mode and typically
        via :meth:`.EnvironmentContext.begin_transaction`.

        """
        raise NotImplementedError
        self.static_output("COMMIT" + self.command_terminator)



class Dialect(object):
    name = 'cqlengine'


class ConnectionProxy(object):
    dialect = Dialect

    @staticmethod
    def close():
        pass

def add_column_raw(column_family_with_keyspace, column, cassandra_type, keyspace):
    statement = 'ALTER TABLE %s ADD %s %s' % (
        column_family_with_keyspace, column, cassandra_type)#, keyspace)
        # Do we need keyspace?
        #"SELECT columnfamily_name from system.schema_columnfamilies WHERE keyspace_name = :ks_name",
        #{'ks_name': ks_name}
    from cqlengine import connection
    with connection.connection_manager() as con:
        tables = con.execute(statement, {})

def add_column(model, column_name):
    column = model._columns[column_name]
    cf_name = model.column_family_name()
    col_name = column.db_field_name
    cassandra_type = column.db_type
    keyspace = model._get_keyspace()
    add_column_raw(cf_name, col_name, cassandra_type, keyspace)

def drop_column(column):
    raise NotImplementedError('Drop column not supported in Cassandra 1.2')
