
if __name__ == '__main__':
    from .Helpers import Helpers
    from .DBHelper import DBHelper
    dbh = DBHelper()

    logs,logcolnames = dbh.GET_ALL()
    ##If no log, first generate the logs.
    if len(logs) == 0:
        logs = Helpers.getAllLogsMy(dolower=False,ToText = False)
        dbh.CleanInsertMany(datarows = logs,keys = logcolnames,table = 'LOGS')
        logs,logcolnames = dbh.GET_ALL(table='LOGS')
             
    print ('Count changesets:',len(logs))

    

    ##Read the linked changeset and bugs information. If does not exist, generate it.
    bc,bccolnames = dbh.GET_ALL('BC')

    if len(bc) == 0:
        bc,out = Helpers.GetBC(logs)
        print(out['ccommits'],out['sbugs'],out['len3minCount'])
        print(out['filteredcounts'])
        dbh.CleanInsertMany(datarows = bc,keys = bccolnames,table = 'BC')
     
    if len(bc) == 0:
        bc,bccolnames = dbh.GET_ALL(table='BC')

    print ('BC Count:',len(bc))