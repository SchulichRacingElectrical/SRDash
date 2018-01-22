import pymysql as sql


class Database:
    unix_socket = '/Applications/MAMP/tmp/mysql/mysql.sock'
    user = 'root'
    password = '123'
    db = 'logs'

    def __init__(self):
        self.connection = sql.connect(unix_socket="/Applications/MAMP/tmp/mysql/mysql.sock", port=3306, user='root', passwd='root', db='logs')

    def insert(self, measurement_date, x, y):

        with self.connection.cursor() as cursor:
            # Create a new record
            #TODO: Change table and column names to match proper dataset that we receive from DAQ
            sql = "INSERT INTO logging VALUES ('%s', '%d', '%d')" % \
                  (measurement_date, x, y)
            cursor.execute(sql)
        self.connection.commit()
        cursor.close()

    def close(self):
        self.connection.close()

    def get_top(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT * " \
                    "FROM `logging`" \
                    "ORDER BY measurement_date DESC LIMIT 1 "
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result


    def view(self):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `logging`"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)

    def update(self, data):
        # print(':')
        #print('Data: ', data)
        self.insert(data[0], data[7], data[3])



