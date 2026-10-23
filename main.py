
mensagem = input("Digite a mensagem do cliente: ").lower()

if "banho" in mensagem and "tosa" in mensagem:
    print("Categoria: Banho e Tosa")

elif "banho" in mensagem:
    print("Categoria: Banho")

elif "tosa" in mensagem:
    print("Categoria: Tosa")

else:
    print("Categoria: Atendimento geral")
