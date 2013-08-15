from resnet_internal.rmsConnector.utils import get_address
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import json

#
# Parses database info into a JSON string.
#
class parse_records():
    request = None                  # The request data
    querySet = None                 # The query set
    columnMap = None                # A dictionary map of each columns name and index
    searchableColumns = None        # A list of searchable columns in the column map

    totalRecords = None             # Total number of records before filtering
    totalDisplayRecords = None      # Total number of records after filtering

    startRecord = None              # Starting record of the display slice
    endRecord = None                # Ending record of the display slice


    def __init__(self, request, querySet, columnMap, searchableColumns):
        self.request = request
        self.querySet = querySet
        self.columnMap = columnMap
        self.searchableColumns = searchableColumns

    def get_json(self):
        # Count the number of total records
        self.totalRecords = self.querySet.count()

        # Paginate data
        self.__paginate()

        # Sort columns, if sorting is requested
        if 'iSortCol_0' in self.request.GET or self.request.GET['iSortCol_0']:
            self.__order()

        # Filter data
        self.__filter()

        # Count the number of records after all criteria are met
        self.totalDisplayRecords = self.querySet.count()

        # Set the final data slice
        self.querySet = self.querySet[self.startRecord:self.endRecord]

        # Prepare the JSON with the response
        if not 'sEcho' in self.request.GET or not self.request.GET['sEcho']:
            sEcho = 0 # default value
        else:
            sEcho = int(self.request.GET['sEcho'])

        data = dict()
        data["sEcho"] = sEcho
        data["iTotalRecords"] = self.totalRecords
        data["iTotalDisplayRecords"] = self.totalDisplayRecords

        # Generate a list of rows which contain a list of index-ordered columns
        rows = []
        for row in self.querySet:
            columns = []
            for columnIndex in range(len(self.columnMap)):
                column = getattr(row, self.columnMap[columnIndex])
                columns.append(column)
            rows.append(columns)

        data['aaData'] = rows

        return json.dumps(data)

    #
    # Pagination
    #
    # Determine the number of records to be displayed per page. Default: 50
    #
    def __paginate(self):
        # Set display length of data slice
        # If an iDisplayLength of -1 is passed in, show all records.
        if not 'iDisplayLength' in self.request.GET or not self.request.GET['iDisplayLength']:
            displayLength = 50 # default value
        else:
            if self.request.GET['iDisplayLength'] != "-1":
                displayLength = min(int(self.request.GET['iDisplayLength']), self.totalRecords)
            else:
                displayLength = self.totalRecords

        # Set starting record and calculate ending record in data slice
        if not 'iDisplayStart' in self.request.GET or not self.request.GET['iDisplayStart']:
            startRecord = 0 # default value
        else:
            startRecord = int(self.request.GET['iDisplayStart'])

        self.endRecord = startRecord + displayLength
        self.startRecord = startRecord

    #
    # Ordering
    #
    # Order each requested column.
    #
    def __order(self):
        if not 'iSortingCols' in self.request.GET or not self.request.GET['iSortingCols']:
            iSortingCols = 0 # default value
        else:
            iSortingCols = int(self.request.GET['iSortingCols'])

        # A list of column ordering flags (ascending, descending, sort order)
        # See QuerySet.order_by in the django docs for more info      
        orderBy = []

        if iSortingCols > 0:
            # Iterate through the columns to sort
            for sortedColIndex in range(0, iSortingCols):
                sortedColName = self.columnMap[int(self.request.GET['iSortCol_' + str(sortedColIndex)])]

                # Check for a sorting direction
                if not 'sSortDir_' + str(sortedColIndex) in self.request.GET or not self.request.GET['sSortDir_' + str(sortedColIndex)]:
                    sortingDirection = ''
                else:
                    sortingDirection = self.request.GET['sSortDir_' + str(sortedColIndex)]

                # Append a minus sign to denote ascending order
                if sortingDirection == 'desc':
                    sortedColName = '-' + sortedColName

                orderBy.append(sortedColName)

            self.querySet = self.querySet.order_by(*orderBy)

    #
    # Filtering
    #
    # Apply filtering by value sent by user
    # Made to work with multiple word search queries and an optional lookup flag.
    # Alex Kavanaugh - kavanaugh.development@outlook.com
    #
    # PHP source: http://datatables.net/forums/discussion/3343/server-side-processing-and-regex-search-filter/p1
    # Credit for finding the add AND method: http://bradmontgomery.blogspot.com/2009/06/adding-q-objects-in-django.html
    #
    def __filter(self):
        if not 'sSearch' in self.request.GET or not self.request.GET['sSearch']:
            customSearch = '' # default value
        else:
            customSearch = str(self.request.GET['sSearch'])

        if customSearch != '':
            words = customSearch.split(" ")
            columnQ = None
            wordQ = None
            firstCol = True
            firstWord = True

            for word in words:
                if word != "":
                    for searchableColumn in self.searchableColumns:
                        kwargz = {searchableColumn + "__icontains": word}
                        q = Q(**kwargz)
                        if (firstCol):
                            firstCol = False
                            columnQ = q
                        else:
                            columnQ |= q
                    if (firstWord):
                        firstWord = False
                        wordQ = columnQ
                    else:
                        wordQ.add(columnQ, Q.AND)
                    columnQ = None
                    firstCol = True
            self.querySet = self.querySet.filter(wordQ)
