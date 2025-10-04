import mysql.connector, time

class ReplicaManager:
    def __init__(self, host_primary='localhost', host_secondary='127.0.0.1',
                 user='root', password='', database='biblioteca'):
        self.host_primary = host_primary
        self.host_secondary = host_secondary
        self.user = user
        self.password = password
        self.database = database
        self.active_host = host_primary

    def check_connection(self, host):
        try:
            cnx = mysql.connector.connect(
                host=host, user=self.user, password=self.password, database=self.database
            )
            cnx.close()
            return True
        except:
            return False

    def monitor(self, interval=5):
        while True:
            ok = self.check_connection(self.host_primary)
            if not ok:
                print("⚠️ Falla detectada en BD primaria. Cambiando a réplica...")
                self.active_host = self.host_secondary
            else:
                self.active_host = self.host_primary
            time.sleep(interval)