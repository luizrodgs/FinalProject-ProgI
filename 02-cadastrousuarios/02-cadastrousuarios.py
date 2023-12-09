# # Objetivo: Trata-se de um sistema de cadastro de usuário.
# # 1. Na tela de cadastro o usuário deve informar os seguintes dados: Nome, Telefone, CPF, RG,
# # Endereço, Nascimento, E-mail, upload de Foto.
# # 2. Você deve validar todos os campos e informar para o usuário caso algum dado informado seja
# # inválido. Seja criativo!
# # 3. Todos os campos são obrigatórios.
# # 4. O cadastro só pode ser realizado quando todos os dados forem válidos.
# # 5. Na tela de pesquisa os dados dos usuários devem ser exibidos em uma tabela e deve ser
# # permitido o filtro por qualquer dado cadastrado.
# # 6. Na tabela de pesquisa devem constar os botões para editar e remover cadastros.
# # 7. Na tela de atualização as mesmas regras de validação do cadastro devem ser aplicadas.
# # 8. Os dados dos usuários devem ser armazenados em um arquivo csv.
# # 9. No arquivo csv, a coluna foto deve armazenar o path de onde a foto está armazenada.

import csv
import re

from tabulate import tabulate

database = "02-cadastrousuarios/02-usuarios.csv"


def salvar_usuario_no_csv(usuario):
    with open(database, mode="a", newline="") as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv, delimiter=",")
        escritor_csv.writerow(usuario)


def validar_telefone(telefone):
    padrao_telefone = re.compile(r"^(\d{2}\s)?9\d{4}-\d{4}$")
    return bool(padrao_telefone.match(telefone))


def validar_cpf(cpf):
    padrao_cpf = re.compile(r"^\d{11}$")
    return bool(padrao_cpf.match(cpf))


def validar_rg(rg):
    padrao_rg = re.compile(r"\d+")
    return bool(padrao_rg.match(rg))


def validar_nascimento(nascimento):
    if int(nascimento) <= 2023:
        return True
    else:
        return False


def validar_email(email):
    padrao_email = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return bool(padrao_email.match(email))


def cadastrar():
    nome = input("Nome: ")
    telefone = input("Telefone (Ex: 91 98877-6655): ")

    while not validar_telefone(telefone):
        print("Telefone inválido. Por favor, digite novamente.")
        telefone = input("Telefone: ")

    cpf = input("CPF: ")
    while not validar_cpf(cpf):
        print("CPF inválido. Por favor, digite novamente.")
        cpf = input("CPF: ")

    rg = input("RG: ")
    while not validar_rg(rg):
        print("RG inválido. Por favor, digite novamente.")
        rg = input("RG: ")

    endereco = input("Endereco: ")
    nascimento = input("Ano de nascimento: ")
    while not validar_nascimento(nascimento):
        print("Ano de nascimento inválido. Por favor, digite novamente.")
        nascimento = input("Ano de nascimento: ")

    email = input("Email: ")
    while not validar_email(email):
        print("Email inválido. Por favor, digite novamente.")
        email = input("Email: ")

    foto = input("Path para foto: ")

    usuario = [
        nome,
        telefone,
        cpf,
        rg,
        endereco,
        nascimento,
        email,
        foto,
    ]

    salvar_usuario_no_csv(usuario)
    print("Usuário cadastrado com sucesso.")


def buscar_por_campo(indice_campo, valor):
    resultados = []

    with open(database, mode="r") as arquivo_csv:
        leitor_csv = csv.reader(arquivo_csv, delimiter=",")
        for linha in leitor_csv:
            if (
                linha
                and 0 <= indice_campo < len(linha)
                and linha[indice_campo] == valor
            ):
                resultados.append(linha)

    return resultados


def exibir_resultados(resultados):
    if resultados:
        headers = [
            "Nome",
            "Telefone",
            "CPF",
            "RG",
            "Endereco",
            "Nascimento",
            "Email",
            "Foto",
        ]
        print(tabulate(resultados, headers=headers, tablefmt="grid"))
    else:
        print("Nenhum resultado encontrado.")


def main():
    executando_programa = True
    while executando_programa == True:
        escolha = int(
            input("O que deseja fazer? 1 - Cadastrar | 2 - Buscar | 3 - Sair ")
        )
        match escolha:
            case 1:
                cadastrar()
            case 2:
                print("A - Nome")
                print("B - Telefone")
                print("C - CPF")
                print("D - RG")
                print("E - Endereco")
                print("F - Nascimento")
                print("G - Email")
                print("H - Path foto")
                indice_campo = input("Qual campo de deseja buscar? ")
                valor_busca = input(
                    f"Informe o valor para buscar no campo {indice_campo}: "
                )

                mapeamento_indices = {
                    "A": 0,
                    "B": 1,
                    "C": 2,
                    "D": 3,
                    "E": 4,
                    "F": 5,
                    "G": 6,
                    "H": 7,
                }

                resultados = buscar_por_campo(
                    mapeamento_indices.get(indice_campo.upper()), valor_busca
                )
                exibir_resultados(resultados)
            case _:
                print("Encerrando...")
                executando_programa = False


if __name__ == "__main__":
    main()
