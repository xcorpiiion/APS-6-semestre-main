from src.corn import connectionFactory as connectionFac


class UsuarioDAO():

    def __init__(self):
        self.conexao = connectionFac.ConnectionFactory().getConnection()
        self.connection = self.conexao.cursor()

    def create(self, usuario):
        self.connection.execute("""
        INSERT INTO Usuario (nome, login, senha, nivelAcesso, radial, circular) VALUES (?,?,?,?,?,?)
        """, (usuario.nome, usuario.login, usuario.senha,
              usuario.nivelAcesso, usuario.radial, usuario.circular))
        self.conexao.commit()

    def read(self):
        self.connection.execute('SELECT * FROM Usuario')
        return self.connection.fetchall()

    def update(self, login, senha):
        self.connection.execute("""
        UPDATE Usuario SET login = ?, senha = ?
        """, login, senha)
        self.conexao.commit()

    def delete(self, login, senha):
        self.connection.execute('DELETE FROM Usuario WHERE login = ? anda senha = ?', login, senha)

    def findUserDigital(self, login, radial, circular):
        self.connection.execute("""
        SELECT * FROM Usuario WHERE login = ? AND radial = ? AND circular = ?
        """, (login, radial, circular))
        return self.connection.fetchall()

    def findUserSenha(self, login, senha):
        self.connection.execute("""
        SELECT * FROM Usuario WHERE login = ? AND senha = ?
        """, (login, senha))
        return self.connection.fetchall()

    def existDigital(self, radial, circular):
        self.connection.execute("""
        SELECT * FROM Usuario WHERE radial = ? AND circular = ?
        """, (radial, circular))
        return self.connection.fetchall()
