from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse




def genCal():
    pass

def genCals():
    pass





#
# Parses database info into a JSON string.
#

def parse_records(request, querySet, columnIndexNameMap, searchableColumns, jsonTemplatePath, *args):
    # count the total number of records before filtering
    iTotalRecords = querySet.count()


    #Safety measure. If someone messes with iDisplayLength manually, we clip it to
    #the number of records. If -1 is passed, show all.
    if not 'iDisplayLength' in request.GET or not request.GET['iDisplayLength']:
        iDisplayLength = 50 # default value
    else:
        if request.GET['iDisplayLength'] != "-1":
            iDisplayLength = min(int(request.GET['iDisplayLength']), iTotalRecords)
        else:
            iDisplayLength = iTotalRecords

    if not 'iDisplayStart' in request.GET or not request.GET['iDisplayStart']:
        startRecord = 0 #default value
    else:
        startRecord = int(request.GET['iDisplayStart'])
    endRecord = startRecord + iDisplayLength

    #apply ordering 
    if 'iSortCol_0' in request.GET or request.GET['iSortCol_0']:
        if not 'iSortingCols' in request.GET or not request.GET['iSortingCols']:
            iSortingCols = 0 #default value
        else:
            iSortingCols = int(request.GET['iSortingCols'])
        asortingCols = []

        if iSortingCols > 0:
            for sortedColIndex in range(0, iSortingCols):
                sortedColName = columnIndexNameMap[int(request.GET['iSortCol_' + str(sortedColIndex)])]
                if not 'sSortDir_' + str(sortedColIndex) in request.GET or not request.GET['sSortDir_' + str(sortedColIndex)]:
                    sortingDirection = ''
                else:
                    sortingDirection = request.GET['sSortDir_' + str(sortedColIndex)]

                if sortingDirection == 'desc':
                    sortedColName = '-' + sortedColName
                asortingCols.append(sortedColName)

            querySet = querySet.order_by(*asortingCols)

    #
    # apply filtering by value sent by user
    # Made to work with multiple word search queries (Alex Kavanaugh - kavanaugh.development@outlook.com)
    # PHP source: http://datatables.net/forums/discussion/3343/server-side-processing-and-regex-search-filter/p1
    # Credit for finding the add AND method: http://bradmontgomery.blogspot.com/2009/06/adding-q-objects-in-django.html
    #
    if not 'sSearch' in request.GET or not request.GET['sSearch']:
        customSearch = '' #default value
    else:
        customSearch = str(request.GET['sSearch'])
    if customSearch != '':
        words = customSearch.split(" ")
        columnQ = None
        wordQ = None
        firstCol = True
        firstWord = True
        for word in words:
            if word != "":
                for searchableColumn in searchableColumns:
                    kwargz = {searchableColumn + "__icontains" : word}
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

        querySet = querySet.filter(wordQ)

    #count how many records match the final criteria
    iTotalDisplayRecords = querySet.count()

    #get the slice
    querySet = querySet[startRecord:endRecord]

    #prepare the JSON with the response
    if not 'sEcho' in request.GET or not request.GET['sEcho']:
        sEcho = '0' #default value
    else:
        sEcho = request.GET['sEcho'] #this is required by datatables 
    jsonString = render_to_string(jsonTemplatePath, locals())

    return HttpResponse(jsonString, mimetype="application/javascript")
