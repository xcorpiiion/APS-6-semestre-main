from src.controller import processarImagem
from src.dao import usuarioDao
from src.model import usuario


def loginController(login, senha=None, img=None):
    dao = usuarioDao.UsuarioDAO()

    if senha is not None:
        u = dao.findUserSenha(login, senha)

    if img is not None:
        r, c = processarImagem.processarImagem(img, 'login')
        u = dao.findUserDigital(login, r[0], c[0])

    if u != []:
        return usuario.Usuario(u[0][0], u[0][1], u[0][2], u[0][3], u[0][4],
                               u[0][5])
    else:
        return None
