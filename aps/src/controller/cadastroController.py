from src.controller import processarImagem
from src.model import usuario
from src.dao import usuarioDao


def cadastroController(img, nome, login, senha, nivelAcesso):
    r, c = processarImagem.processarImagem(img, 'cadastro')
    dao = usuarioDao.UsuarioDAO()
    verificarDigital = dao.existDigital(r[0], c[0])
    if verificarDigital == []:
        user = usuario.Usuario(nome, login, senha, nivelAcesso, r[0], c[0])
        user = dao.create(user)
        return True
    else:
        return False
