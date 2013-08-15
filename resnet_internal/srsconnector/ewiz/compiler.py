from django.db.utils import DatabaseError, IntegrityError
from django.db.models.sql.constants import SINGLE, MULTI
from django.db.models.sql import aggregates as sqlaggregates
from django.utils.datastructures import SortedDict
from djangotoolbox.basecompiler import (NonrelQuery,
                                        NonrelCompiler,
                                        NonrelInsertCompiler,
                                        NonrelUpdateCompiler,
                                        NonrelDeleteCompiler)
from url_builders import Select, Update, Insert
from decompiler import EwizDecompiler
from functools import wraps
import sys, urllib2, re

#
# The EnterpriseWizard database backend compilers
#
# Author: Alex Kavanaugh
# Email: kavanaugh.development@outlook.com
#


#
# Function wrapper for debugging - taken from Django-Nonrel/djangotoolbox
#
def safe_call(func):
    @wraps(func)
    def _func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            raise DatabaseError, DatabaseError(*tuple(e)), sys.exc_info()[2]
    return _func

#
# The Ewiz class layer for nonrel queries.
#
# This class provides the framework for a query to the Ewiz REST interface.
#
class EwizQuery(NonrelQuery):
    # A dictionary of operators and their REST representations.
    operators = {
        'exact': lambda lookupType, value: (u"= BINARY", u"'" + unicode(str(value)) + u"'"),
        'iexact': lambda lookupType, value: (u"=", u"'" + unicode(str(value)) + u"'"),
        'contains': lambda lookupType, value: (u"LIKE BINARY", u"'%" + unicode(str(value)) + u"%'"),
        'icontains': lambda lookupType, value: (u"LIKE", u"'%" + unicode(str(value)) + u"%'"),
        'gt': lambda lookupType, value: (u">", u"'" + unicode(str(value)) + u"'"),
        'gte': lambda lookupType, value: (u">=", u"'" + unicode(str(value)) + u"'"),
        'lt': lambda lookupType, value: (u"<", u"'" + unicode(str(value)) + u"'"),
        'lte': lambda lookupType, value: (u"<=", u"'" + unicode(str(value)) + u"'"),
        'in': lambda lookupType, value: (u"IN", value),
        'startswith': lambda lookupType, value: (u"LIKE BINARY", u"'" + unicode(str(value)) + u"%'"),
        'istartswith': lambda lookupType, value: (u"LIKE", u"'" + unicode(str(value)) + u"%'"),
        'endswith': lambda lookupType, value: (u"LIKE BINARY", u"'%" + unicode(str(value)) + u"'"),
        'iendswith': lambda lookupType, value: (u"LIKE", u"'%" + unicode(str(value)) + u"'"),
        'range': lambda lookupType, value: (u"BETWEEN", unicode(str(value))),
        'isnull': lambda lookupType, value: (u"IS NULL", None),
        'regex': lambda lookupType, value: (u"REGEXP BINARY", u"'" + unicode(str(value)) + u"'"),
        'iregex': lambda lookupType, value: (u"REGEXP", u"'" + unicode(str(value)) + u"'"),
    }

    # A dictionary of operators and their negated REST representations.
    negatedOperators = {
        'exact': lambda lookupType, value: (u"!= BINARY", u"'" + unicode(str(value)) + u"'"),
        'iexact': lambda lookupType, value: (u"!=", u"'" + unicode(str(value)) + u"'"),
        'contains': lambda lookupType, value: (u"NOT LIKE BINARY", u"'%" + unicode(str(value)) + u"%'"),
        'icontains': lambda lookupType, value: (u"NOT LIKE", u"'%" + unicode(str(value)) + u"%'"),
        'gt': lambda lookupType, value: (u"<", u"'" + unicode(str(value)) + u"'"),
        'gte': lambda lookupType, value: (u"<=", u"'" + unicode(str(value)) + u"'"),
        'lt': lambda lookupType, value: (u">", u"'" + unicode(str(value)) + u"'"),
        'lte': lambda lookupType, value: (u">=", u"'" + unicode(str(value)) + u"'"),
        'in': lambda lookupType, value: (u"NOT IN", value),
        'startswith': lambda lookupType, value: (u"NOT LIKE BINARY", u"'" + unicode(str(value)) + u"%'"),
        'istartswith': lambda lookupType, value: (u"NOT LIKE", u"'" + unicode(str(value)) + u"%'"),
        'endswith': lambda lookupType, value: (u"NOT LIKE BINARY", u"'%" + unicode(str(value)) + u"'"),
        'iendswith': lambda lookupType, value: (u"NOT LIKE", u"'%" + unicode(str(value)) + u"'"),
        'range': lambda lookupType, value: (u"NOT BETWEEN", unicode(str(value))),
        'isnull': lambda lookupType, value: (u"IS NOT NULL", None),
        'regex': lambda lookupType, value: (u"NOT REGEXP BINARY", u"'" + unicode(str(value)) + u"'"),
        'iregex': lambda lookupType, value: (u"NOT REGEXP", u"'" + unicode(str(value)) + u"'"),
    }

    def __init__(self, compiler, fields):
        super(EwizQuery, self).__init__(compiler, fields)
        self.compiledQuery = {
            'table': None,
            'filters': [],
            'ordering': [],
            'limits': {
                'offset': u'0',
                'limit': u'18446744073709551615' # Max limit as proposed by MySQL,
            },
        }

    def __debug(self):
        return (u'DEBUG INFO:' +
            u'\n\nRAW_QUERY: ' + str(self.query) +
            u'\nCOMPILED_QUERY: ' + str(self.compiledQuery) +
            u'\nQUERY_URL: ' + str(Select(self.connection.settings_dict, self.query.model._meta.db_table, self.compiledQuery).build())
        )

    #
    # EwizQueryCompiler
    #
    # Gathers query parameters (filters, ordering, etc.) into a comiledQuery dictionary,
    # builds a URL using those parameters (via URL Builders),
    # and uses the decompiler to pull data using the REST API.
    #
    # This method returns an iterator (using for/yield) over the query results.
    #
    @safe_call
    def fetch(self, low_mark=0, high_mark=None):

        # Handle all records requests
        if not self.compiledQuery["filters"]:
            self.compiledQuery["filters"] = [u"id LIKE '%'"]

        if high_mark is None:
            # Infinite fetching
            self.compiledQuery["limits"]["offset"] = unicode(str(low_mark))
            self.compiledQuery["limits"]["limit"] = u'18446744073709551615' # Max limit as proposed by MySQL
        elif high_mark > low_mark:
            # Range fetching
            self.compiledQuery["limits"]["offset"] = unicode(str(low_mark))
            self.compiledQuery["limits"]["limit"] = unicode(str(high_mark - low_mark))
        else:
            # Invalid range
            self.compiledQuery["limits"]["offset"] = unicode(str(0))
            self.compiledQuery["limits"]["limit"] = unicode(str(0))

        # Build the url
        url = Select(self.connection.settings_dict, self.query.model._meta.db_table, self.compiledQuery).build()

        # Fetch and decompiler the results
        queryResults = EwizDecompiler(self.query.model, self.connection.settings_dict).decompile(url)

        # Yield each result
        for result in queryResults:
            yield result

    #
    # EwizQueryCounter
    #
    # Sends the query to Ewiz via the REST API, but only decompiles and returns the result count.
    #
    # This method returns the number of results a query will yield.
    #
    @safe_call
    def count(self, limit=None):

        # Pass given limit to the compiledQuery
        if limit:
            self.compiledQuery["limits"]["limit"] = str(unicode(limit))

        # Build the url
        url = Select(self.connection.settings_dict, self.query.model._meta.db_table, self.compiledQuery).build()
        # Send the query, but only fetch and decompile the result count
        count = EwizDecompiler(self.query.model, self.connection.settings_dict).count(url)

        return count

    @safe_call
    def delete(self):
        raise DatabaseError(u"EnterpriseWizard administrators forbid the deletion of records.")

    #
    # EwizQueryOrderer
    #
    # Adds the ORDER BY parameter to the compiledQuery. Default: ORDER BY id ASC.
    #
    # NOTE:
    # 1) EnterpriseWizard's REST interface does not correctly represent ORDER BY queries. The Ewiz
    #    backend handles the query fine, but the frontend reorders it by ticketID. Since this causes
    #    limited results to be yielded incorrectly, this feature has been disabled until further notice.
    #
    @safe_call
    def order_by(self, ordering):

        # A True/False ordering designates default ordering.
        if type(ordering) is bool:
            if ordering:
                self.compiledQuery["ordering"].append(u'id ASC')
            else:
                raise DatabaseError(u"The 'ORDER BY' statement is not currently supported by the EnterpriseWizard REST interface.")
                self.compiledQuery["ordering"].append(u'id DESC')
        # A list of ordering tuples designates multiple ordering (non-default)
        else:
            for order in ordering:
                field = order[0]
                if order[1]:
                    direction = u'ASC'
                else:
                    direction = u'DESC'

                self.compiledQuery["ordering"].append(field.name + u' ' + direction)

            raise DatabaseError(u"The 'ORDER BY' statement is not currently supported by the EnterpriseWizard REST interface.")

    #
    # EwizQueryFilterer
    #
    # Adds a single constraint to be used in the WHERE clause of the compiledQuery.
    #
    # This method is called by the add_filters method of NonrelQuery
    #
    @safe_call
    def add_filter(self, field, lookupType, negated, value):

        # Determine operator
        if negated:
            try:
                operator = self.negatedOperators[lookupType]
            except KeyError:
                raise DatabaseError("Lookup type %r can't be negated" % lookupType)
        else:
            try:
                operator = self.operators[lookupType]
            except KeyError:
                raise DatabaseError("Lookup type %r isn't supported" % lookupType)

        # Handle lambda lookup types
        if callable(operator):
            operator, value = operator(lookupType, value)

        self.compiledQuery["filters"].append(field.column + u' ' + operator + u' ' + value)


#
# The Ewiz Query Compiler
#
# This handles SELECT queries and is the base class for INSERT, and UPDATE requests.
#
class EwizCompiler(NonrelCompiler):
    query_class = EwizQuery

    #
    # Handles SQL-like aggregate queries. This method emulates COUNT
    # by using the NonrelQuery.count method.
    #
    def execute_sql(self, result_type=MULTI):

        aggregates = self.query.aggregate_select.values()

        try:
            saveCheck = self.query.extra["a"] == (u'1', [])
        except:
            pass

        # Simulate a count().
        if aggregates:
            assert len(aggregates) == 1
            aggregate = aggregates[0]
            assert isinstance(aggregate, sqlaggregates.Count)
            opts = self.query.get_meta()
            assert aggregate.col == '*' or \
                   aggregate.col == (opts.db_table, opts.pk.column)
            count = self.get_count()
            if result_type is SINGLE:
                return [count]
            elif result_type is MULTI:
                return [[count]]
        #
        # The save() method determines whether to UPDATE or INSERT based on whether or not primary_key query results exist (if a primary_key is not supplied, INSERT is chosen)
        # The following conditional section is a small hack that uses the count() method to count the number of results returned.
        #
        # False is returned if zero results are returned, True otherwise.
        #
        elif saveCheck:
            self.query.extra = SortedDict()
            count = self.get_count()
            if result_type is SINGLE:
                return (count != 0)
            elif result_type is MULTI:
                return (count != 0)

        raise NotImplementedError("The database backend only supports "
                                  "count() queries.")

# 
# Ewiz Insert Compiler
#
# Creates new tickets in the Ewiz database via the REST API.
#
class EwizInsertCompiler(NonrelInsertCompiler, EwizCompiler):

    #
    # Prepares field, value tuples for the compiler to use and,
    # if requested, returns the primary key of the new ticket.
    #
    @safe_call
    def execute_sql(self, return_id=False):
        docs = []
        pk = self.query.get_meta().pk
        for obj in self.query.objs:
            doc = []
            for field in self.query.fields:
                value = field.get_db_prep_save(
                    getattr(obj, field.attname) if self.query.raw else field.pre_save(obj, obj._state.adding),
                    connection=self.connection
                )
                if not field.null and value is None and not field.primary_key:
                    raise IntegrityError("You can't set %s (a non-nullable "
                                         "field) to None!" % field.name)

                # Prepare value for database, note that query.values have
                # already passed through get_db_prep_save.
                value = self.ops.value_for_db(value, field)
                doc.append((field, value))

            docs.append(doc)

        if len(docs) > 1:
            raise DatabaseError(u'INSERT COMPILER: Docs length assumption was wrong. Contact Alex Kavanaugh with details./n/tDocs Length: ' + unicode(str(len(docs))))

        key = self.insert(docs[0], return_id=return_id)
        # Pass the key value through normal database deconversion.
        return self.ops.convert_values(self.ops.value_from_db(key, pk), pk)


    #
    # Builds and sends a query to create a new ticket in the Ewiz database.
    #
    @safe_call
    def insert(self, values, return_id):

        # Build the url
        url = Insert(self.connection.settings_dict, self.query.model._meta.db_table, values).build()

        # Attempt the Insert
        request = urllib2.Request(url)

        try:
            response = urllib2.urlopen(request)

            # Return the new ID
            if return_id:
                pattern = re.compile(r"^EWREST_id='(?P<value>.*)';$", re.DOTALL)

                idList = []
                for line in iter(lambda: unicode(response.readline().decode('string-escape').strip(), 'ISO-8859-1'), ""):
                    idList.append(pattern.match(line).group('value'))
                return int(idList[0])

        except urllib2.HTTPError, message:
            raise DatabaseError(self.query.model._meta.object_name + u' - An INSERT error has occurred. Please contact the development team with the following details:\n\t' + unicode(str(message)))

# 
# Ewiz Insert Compiler
#
# Creates new tickets in the Ewiz database via the REST API.
#
class EwizUpdateCompiler(NonrelUpdateCompiler):

    #
    # Builds and sends a query to update/change information in a ticket that currently exists in the Ewiz database.
    #
    @safe_call
    def update(self, values):

        # Build the url
        try:
            ticketID = self.query.where.children[0].children[0][-1]
        except:
            raise DatabaseError(u'UPDATE COMPILER: UPDATE ticketID assumptions were wrong. Contact Alex Kavanaugh with details.')
        url = Update(self.connection.settings_dict, self.query.model._meta.db_table, ticketID, values).build()

        # Attempt the Update
        request = urllib2.Request(url)

        try:
            urllib2.urlopen(request)
        except urllib2.HTTPError, message:
            raise DatabaseError(self.query.model._meta.object_name + u' - An UPDATE error has occurred. Please contact the development team with the following details:\n\t' + unicode(str(message)))

class EwizDeleteCompiler(NonrelDeleteCompiler):

    @safe_call
    def execute_sql(self, result_type=None):
        raise DatabaseError(u"EnterpriseWizard administrators forbid the deletion of records.")

# Assign new compiler classes as default compilers
SQLCompiler = EwizCompiler
SQLInsertCompiler = EwizInsertCompiler
SQLUpdateCompiler = EwizUpdateCompiler
SQLDeleteCompiler = EwizDeleteCompiler
