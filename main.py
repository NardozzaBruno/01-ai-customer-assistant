def classificar_mensagem(mensagem: str) -> str:
    """Classifica uma mensagem usando palavras-chave de servicos do pet shop."""
    mensagem = mensagem.lower()

    if "banho" in mensagem and "tosa" in mensagem:
        return "Banho e Tosa"
    if "banho" in mensagem:
        return "Banho"
    if "tosa" in mensagem:
        return "Tosa"
    return "Atendimento geral"


def main() -> None:
    mensagem = input("Digite a mensagem do cliente: ")
    print(f"Categoria: {classificar_mensagem(mensagem)}")


if __name__ == "__main__":
    main()
