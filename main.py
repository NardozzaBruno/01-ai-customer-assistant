from dataclasses import dataclass
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


def normalizar(texto: str) -> str:
    return "".join(
        letra for letra in unicodedata.normalize("NFD", texto.casefold())
        if unicodedata.category(letra) != "Mn"
    ).strip().rstrip(".!?").strip()


def gerar_resposta(categoria: str) -> str:
    """Retorna a pergunta inicial para um servico ou a orientacao geral."""
    if categoria in {"Banho", "Tosa", "Banho e Tosa"}:
        return (
            f"Certo, {categoria.lower()}! Qual é o porte do seu pet "
            "(pequeno, médio ou grande)?"
        )
    return "Olá! Posso ajudar com banho e tosa. Qual serviço você procura?"


def extrair_detalhes(mensagem: str) -> tuple[str | None, str | None, bool]:
    """Extrai detalhes por palavras inteiras; pede esclarecimento se houver duvida."""
    entrada = normalizar(mensagem)
    portes = {"pequeno": "pequeno", "medio": "médio", "grande": "grande"}
    dias = {
        "hoje": "hoje", "amanha": "amanhã",
        "segunda": "segunda-feira", "terca": "terça-feira",
        "quarta": "quarta-feira", "quinta": "quinta-feira",
        "sexta": "sexta-feira", "sabado": "sábado", "domingo": "domingo",
    }
    encontrados_porte: set[str] = set()
    encontrados_dia: set[str] = set()
    ambiguo = False
    # Uma negacao no mesmo trecho de um detalhe exige uma resposta mais clara.
    for trecho in re.split(r"[,;.!?]|\b(?:mas|porem)\b", entrada):
        palavras = set(re.findall(r"\b\w+\b", trecho))
        p = palavras & portes.keys()
        d = palavras & dias.keys()
        if (p or d) and palavras & NEGACOES:
            ambiguo = True
        encontrados_porte.update(portes[item] for item in p)
        encontrados_dia.update(dias[item] for item in d)
    ambiguo = ambiguo or len(encontrados_porte) > 1 or len(encontrados_dia) > 1
    porte = next(iter(encontrados_porte)) if len(encontrados_porte) == 1 else None
    dia = next(iter(encontrados_dia)) if len(encontrados_dia) == 1 else None
    return porte, dia, ambiguo


@dataclass
class Atendimento:
    """Mantem apenas os dados da solicitacao atual, em memoria."""

    servico: str | None = None
    porte: str | None = None
    dia: str | None = None

    def reiniciar(self) -> None:
        self.servico = self.porte = self.dia = None

    def responder(self, mensagem: str) -> str:
        entrada = normalizar(mensagem)
        if entrada in {"cancelar", "reiniciar"}:
            self.reiniciar()
            return "Solicitação descartada. Qual serviço você procura?"
        if not entrada:
            return "Digite uma mensagem para continuar ou 'cancelar' para recomeçar."

        categoria = classificar_mensagem(mensagem)
        porte, dia, ambiguo = extrair_detalhes(mensagem)
        if ambiguo:
            return (
                "Preciso esclarecer os detalhes. Informe um único porte "
                "(pequeno, médio ou grande) e um único dia desejado, "
                "sem alternativas ou negações. O pedido anterior foi mantido."
            )

        novo_servico = categoria != "Atendimento geral"
        if novo_servico:
            if self.servico is not None and self.servico != categoria:
                self.reiniciar()
            self.servico = categoria
        if porte is not None:
            self.porte = porte
        if dia is not None:
            self.dia = dia

        if self.servico is None:
            return gerar_resposta("Atendimento geral")
        if self.porte is None:
            return gerar_resposta(self.servico)
        if self.dia is None:
            return "Para qual dia? Responda hoje, amanhã ou um dia da semana."

        resumo = (
            f"Resumo da solicitação: {self.servico}; porte {self.porte}; "
            f"dia desejado: {self.dia}. "
            "Agendamento não confirmado: depende da disponibilidade do pet shop. "
            "Para iniciar outra solicitação, informe o serviço."
        )
        self.reiniciar()
        return resumo


def main() -> None:
    print("Assistente de atendimento. Digite 'sair' para encerrar.")
    print("Demonstração: não confirma agendamentos. Digite 'cancelar' para recomeçar.")
    atendimento = Atendimento()
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

        categoria = classificar_mensagem(mensagem)
        if categoria != "Atendimento geral":
            print(f"Categoria: {categoria}")
        print(f"Assistente: {atendimento.responder(mensagem)}")


if __name__ == "__main__":
    main()
