from Database import Database

while True:
    db = Database()

    row_list = []

    #row_list.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%m"))
    #row_list.append(1000)
    #row_list.append(500)
    #row_list.append(6000)
    #print(row_list)
    #db.update(row_list)
    print(db.get_top()[0][0])

