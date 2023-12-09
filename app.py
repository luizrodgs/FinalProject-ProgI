import csv
import hashlib
import random
import secrets
import time

from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

jogos = [
    {"title": "01 - Jogos Matemáticos", "link": "/matematicos/", "descriptions": []},
    {"title": "02 - Cadastro Usuários", "link": "#", "descriptions": []},
    {"title": "03 - Gerador de Senhas", "link": "/gerador/", "descriptions": []},
]


@app.route("/")
def home():
    return render_template(
        "template.html", cards=jogos, titulo="Home", pagina="Qual App deseja usar?"
    )


jogo_matematicos = [
    {"title": "Jogar", "link": "/matematicos/jogar/", "descriptions": []},
    {"title": "Ranking", "link": "/matematicos/ranking/", "descriptions": []},
    {"title": "Sair", "link": "/", "descriptions": []},
]


@app.route("/matematicos/")
def matematicos():
    return render_template(
        "template.html",
        cards=jogo_matematicos,
        titulo="Matematicos",
        pagina="01 - Jogos Matemáticos | O que deseja fazer?",
    )


matematicos_fases = [
    {"title": "Fase 1", "link": "/matematicos/fase1/", "descriptions": []},
    {"title": "Fase 2", "link": "/matematicos/fase2/", "descriptions": []},
    {"title": "Sair", "link": "/", "descriptions": []},
]


@app.route("/matematicos/jogar/", methods=["GET", "POST"])
def jogar():
    if request.method == "POST":
        nickname = request.form["nickname"]
        session["nickname"] = nickname
        return render_template(
            "template.html",
            cards=matematicos_fases,
            titulo="Matemáticos",
            pagina="01 - Jogos Matemáticos | Qual Fase deseja jogar?",
        )
    else:
        return render_template(
            "form.html", titulo="Matematicos", pagina="01 - Jogos Matemáticos | Jogar"
        )


def salvar_recorde(database_fase, nickname, pontuacao):
    jogador_no_ranking = False
    indice_jogador = None
    with open(database_fase, mode="r") as arquivo_csv:
        leitor_csv = csv.reader(arquivo_csv)
        for indice, linha in enumerate(leitor_csv):
            if linha and linha[0] == nickname:
                jogador_no_ranking = True
                indice_jogador = indice
                break
    if jogador_no_ranking and pontuacao > int(linha[1]):
        with open(database_fase, mode="r") as arquivo_csv:
            linhas = list(csv.reader(arquivo_csv))
            linhas[indice_jogador] = [nickname, pontuacao]

        with open(database_fase, mode="w", newline="") as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv)
            escritor_csv.writerows(linhas)

    elif not jogador_no_ranking:
        with open(database_fase, mode="a", newline="") as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv)
            escritor_csv.writerow([nickname, pontuacao])


@app.route("/matematicos/fase1/", methods=["GET", "POST"])
def fase1():
    if request.method == "POST":
        numero_sorteado = session.get("numero_sorteado")
        pontuacao = session.get("pontuacao")
        tentativas = session.get("tentativas")
        chute = request.form["chute"]
        nickname = "@" + session.get("nickname")
        if int(chute) == numero_sorteado:
            salvar_recorde(
                "01-jogosmatematicos/01-ranking-fase1.csv", nickname, pontuacao
            )
            return render_template(
                "sucesso.html",
                cards=matematicos_fases,
                titulo="PARABÉNS!",
                pagina="Você acertou o número secreto",
            )
        else:
            pontuacao -= 3
            tentativas += 1
            session["pontuacao"] = pontuacao
            session["tentativas"] = tentativas
            if int(chute) > numero_sorteado:
                return render_template(
                    "fase1.html",
                    msg="Não foi dessa vez! Tente um número menor!",
                    tentativa=chute,
                    titulo="Fase 1",
                    pagina=tentativas,
                )
            else:
                return render_template(
                    "fase1.html",
                    msg="Não foi dessa vez! Tente um número maior!",
                    tentativa=chute,
                    titulo="Fase 1",
                    pagina=tentativas,
                )
    else:
        nickname = session.get("nickname")
        session["numero_sorteado"] = random.randint(0, 100)
        session["pontuacao"] = 100
        session["tentativas"] = 1
        return render_template(
            "fase1.html",
            nickname=nickname,
            titulo="Fase 1",
            pagina="1",
        )


def sortear_operacao():
    x = random.randint(0, 100)
    y = random.randint(0, 100)
    operador = random.choice(["+", "-", "*"])
    operacao_sorteada = f"{x} {operador} {y}"
    resultado_operacao_sorteada = eval(operacao_sorteada)
    return operacao_sorteada, resultado_operacao_sorteada


@app.route("/matematicos/fase2/", methods=["GET", "POST"])
def fase2():
    if request.method == "POST":
        nickname = "@" + session.get("nickname")
        resultado_operacao = session.get("resultado_operacao")
        pontuacao = session.get("pontuacao")
        chute = request.form["chute"]
        tempo_passado = time.time() - session.get("tempo")
        tempo_partida = int(max(60 - tempo_passado, 0))

        if tempo_passado >= 60:
            salvar_recorde(
                "01-jogosmatematicos/01-ranking-fase2.csv", nickname, pontuacao
            )
            return render_template(
                "terminou.html",
                cards=matematicos_fases,
                titulo="Escolha",
                pagina="Escolha uma fase?",
            )
        else:
            nova_operacao, novo_resultado_operacao = sortear_operacao()
            session["operacao"] = nova_operacao
            session["resultado_operacao"] = novo_resultado_operacao
            if int(chute) == int(resultado_operacao):
                pontuacao += 1
                session["pontuacao"] = pontuacao
                return render_template(
                    "fase2.html",
                    nickname=nickname,
                    msg=f"Correto! Sua pontuação atual: {pontuacao}",
                    operacao=nova_operacao,
                    titulo="Fase 2",
                    pagina=tempo_partida,
                )
            else:
                return render_template(
                    "fase2.html",
                    msg=f"Errado! Sua pontuação atual: {pontuacao}",
                    operacao=nova_operacao,
                    tentativa=chute,
                    titulo="Fase 2",
                    pagina=tempo_partida,
                )
    else:
        session["pontuacao"] = 0
        session["tempo"] = time.time()
        operacao, resultado_operacao = sortear_operacao()
        session["operacao"] = operacao
        session["resultado_operacao"] = resultado_operacao
        return render_template(
            "fase2.html",
            msg="Qual o resultado da operação abaixo?",
            operacao=operacao,
            titulo="Matemáticos",
            pagina="60",
        )


matematicos_ranking = [
    {"title": "Fase 1", "link": "/matematicos/ranking/fase1/", "descriptions": []},
    {"title": "Fase 2", "link": "/matematicos/ranking/fase2/", "descriptions": []},
    {"title": "Sair", "link": "/", "descriptions": []},
]


@app.route("/matematicos/ranking/")
def ranking():
    return render_template(
        "template.html",
        cards=matematicos_ranking,
        titulo="Cadastro usuários",
        pagina="Escolha qual Ranking",
    )


def exibir_ranking(fase):
    with open(fase, mode="r") as arquivo_csv:
        leitor_csv = csv.reader(arquivo_csv)
        next(leitor_csv, None)
        ranking_list = [linha for linha in leitor_csv if len(linha) >= 2]
        ranking_list = sorted(
            ranking_list, key=lambda linha: int(linha[1]), reverse=True
        )
        return ranking_list


@app.route("/matematicos/ranking/fase1/")
def ranking_fase1():
    ranking_list = exibir_ranking("01-jogosmatematicos/01-ranking-fase1.csv")
    return render_template(
        "table.html",
        th=["Nickname", "Pontuação"],
        linhas=ranking_list,
        titulo="Ranking Fase 1",
        pagina="Ranking Fase 1",
    )


@app.route("/matematicos/ranking/fase2/")
def ranking_fase2():
    ranking_list = exibir_ranking("01-jogosmatematicos/01-ranking-fase2.csv")
    return render_template(
        "table.html",
        th=["Nickname", "Pontuação"],
        linhas=ranking_list,
        titulo="Ranking Fase 2",
        pagina="Ranking Fase 2",
    )


def gerar_senha():
    caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_-+=<>?"
    senha = "".join(secrets.choice(caracteres) for _ in range(12))
    return senha


def gerar_hash(senha, algoritmo="sha256"):
    hash_obj = hashlib.new(algoritmo)
    hash_obj.update(senha.encode("utf-8"))
    return hash_obj.hexdigest()


def salvar_login_no_csv(login, database):
    with open(database, mode="a", newline="") as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv, delimiter=",")
        escritor_csv.writerow(login)


def exibir_senhas(database):
    with open(database, mode="r") as arquivo_csv:
        leitor_csv = csv.reader(arquivo_csv)
        next(leitor_csv, None)
        leitor_csv = [linha for linha in leitor_csv]
    return leitor_csv


menu_gerador = [
    {"title": "Cadastrar", "link": "/gerador/senha/", "descriptions": []},
    {"title": "Listar", "link": "/gerador/lista/", "descriptions": []},
    {"title": "Sair", "link": "/", "descriptions": []},
]


@app.route("/gerador/")
def gerador():
    return render_template(
        "template.html",
        cards=menu_gerador,
        titulo="Gerador de senhas",
        pagina="03 - Gerador de Senhas | O que deseja fazer?",
    )


@app.route("/gerador/senha/", methods=["GET", "POST"])
def gerador_senha():
    if request.method == "POST":
        sistema = request.form["sistema"]
        senha = gerar_senha()
        pass_hash = gerar_hash(senha)
        login = [sistema, senha, pass_hash]
        salvar_login_no_csv(login, "03-geradorsenhas/03-senhas.csv")
        return render_template(
            "sucesso.html",
            titulo="Gerador de Senha",
            pagina="03 - Gerador de Senha | Criado com sucesso",
        )
    else:
        return render_template(
            "cadastrar.html",
            titulo="Gerador de Senha",
            pagina="03 - Gerador de Senha | Cadastrar",
        )


@app.route("/gerador/lista/")
def listar_senhas():
    lista = exibir_senhas("03-geradorsenhas/03-senhas.csv")
    return render_template(
        "table.html",
        th=["Sistema", "Senha", "Hash", "Regerar", "Excluir"],
        linhas=lista,
        titulo="Gerador de Senha",
        pagina="03 - Gerador de Senha | Listar",
    )


def salvar_login_no_csv(login, database):
    with open(database, mode="a", newline="") as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv, delimiter=",")
        escritor_csv.writerow(login)


def atualizar_senha(login, database):
    indice_jogador = None
    with open(database, mode="r") as arquivo_csv:
        leitor_csv = csv.reader(arquivo_csv)
        for indice, linha in enumerate(leitor_csv):
            if linha and linha[0] == login[0]:
                jogador_no_ranking = True
                indice_jogador = indice
                break
    if jogador_no_ranking:
        with open(database, mode="r") as arquivo_csv:
            linhas = list(csv.reader(arquivo_csv))
            linhas[indice_jogador] = login

        with open(database, mode="w", newline="") as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv)
            escritor_csv.writerows(linhas)


@app.route("/gerador/editar/<string:nome_sistema>/")
def editar(nome_sistema):
    senha = gerar_senha()
    pass_hash = gerar_hash(senha)
    login = [nome_sistema, senha, pass_hash]
    atualizar_senha(login, "03-geradorsenhas/03-senhas.csv")
    return render_template(
        "sucesso.html",
        titulo="Gerador de Senha",
        pagina="03 - Gerador de Senha | Criado com sucesso",
    )


def deletar_senha(database, nome_sistema):
    linhas = []
    with open(database, mode="r", newline="") as arquivo_csv:
        leitor_csv = csv.reader(arquivo_csv, delimiter=",")
        for linha in leitor_csv:
            if linha[0] != nome_sistema:
                linhas.append(linha)

    with open(database, mode="w", newline="") as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv, delimiter=",")
        for linha in linhas:
            escritor_csv.writerow(linha)


@app.route("/gerador/deletar/<string:nome_sistema>/")
def deletar(nome_sistema):
    deletar_senha("03-geradorsenhas/03-senhas.csv", nome_sistema)
    lista = exibir_senhas("03-geradorsenhas/03-senhas.csv")
    return render_template(
        "table.html",
        th=["Sistema", "Senha", "Hash", "Regerar", "Excluir"],
        linhas=lista,
        titulo="Gerador de Senha",
        pagina="03 - Gerador de Senha | Listar",
    )


if __name__ == "__main__":
    app.run()
