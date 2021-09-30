import sqlite3
import numpy as np
import io


class ConnectionFactory():

    def getConnection(self):
        def adapt_array(arr):
            out = io.BytesIO()
            np.save(out, arr)
            out.seek(0)
            return sqlite3.Binary(out.read())

        def convert_array(text):
            out = io.BytesIO(text)
            out.seek(0)
            return np.load(out)

        sqlite3.register_adapter(np.ndarray, adapt_array)
        sqlite3.register_converter("array", convert_array)
        try:
            self.conn = sqlite3.connect(
                'aps.db', detect_types=sqlite3.PARSE_DECLTYPES)
            return self.conn
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)

    def closeConnection(self):
        self.conn.close()
