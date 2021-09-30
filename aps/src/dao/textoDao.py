from src.corn import connectionFactory as connectionFac


class TextoDAO():

    def __init__(self):
        self.conexao = connectionFac.ConnectionFactory().getConnection()
        self.connection = self.conexao.cursor()

    def findText(self, nivel):
        self.connection.execute("""
        SELECT Texto FROM Textos WHERE NivelAcesso = ?
        """, (nivel))
        return self.connection.fetchall()
