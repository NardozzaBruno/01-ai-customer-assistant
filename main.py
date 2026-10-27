import re
import unicodedata


SERVICOS = {"banho", "tosa"}
NEGACOES = {"nao", "sem", "nem"}
REINICIOS = {"mas", "porem", "so", "somente", "apenas"}


def classificar_mensagem(mensagem: str) -> str:
    """Classifica palavras inteiras e negacoes simples em mensagens em portugues."""
    normalizada = "".join(
        letra
        for letra in unicodedata.normalize("NFD", mensagem.lower())
        if unicodedata.category(letra) != "Mn"
    )
    palavras = re.findall(r"\w+|[^\w\s]", normalizada)
    solicitados: set[str] = set()
    negado = False

    for palavra in palavras:
        if palavra in REINICIOS or re.fullmatch(r"[^\w\s]", palavra):
            negado = False
        elif palavra in NEGACOES:
            negado = True
        elif palavra in SERVICOS:
            # A ultima mencao de cada servico permite corrigir um pedido anterior.
            if negado:
                solicitados.discard(palavra)
            else:
                solicitados.add(palavra)

    if solicitados == SERVICOS:
        return "Banho e Tosa"
    if "banho" in solicitados:
        return "Banho"
    if "tosa" in solicitados:
        return "Tosa"
    return "Atendimento geral"


def main() -> None:
    print("Assistente de atendimento. Digite 'sair' para encerrar.")
    while True:
        try:
            mensagem = input("Digite a mensagem do cliente: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAtendimento encerrado.")
            break

        if mensagem.casefold() == "sair":
            print("Atendimento encerrado.")
            break
        if not mensagem:
            print("Digite uma mensagem ou 'sair' para encerrar.")
            continue

        print(f"Categoria: {classificar_mensagem(mensagem)}")


if __name__ == "__main__":
    main()
