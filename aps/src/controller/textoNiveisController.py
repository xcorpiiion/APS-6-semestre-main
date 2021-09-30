from src.dao import textoDao


def textoNivelAcessoController(nivel):
    dao = textoDao.TextoDAO()
    texto = dao.findText(nivel)
    return texto[0][0]