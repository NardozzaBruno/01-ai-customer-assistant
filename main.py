from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from collections.abc import Callable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
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


def hoje_sao_paulo() -> date:
    try:
        fuso = ZoneInfo("America/Sao_Paulo")
    except ZoneInfoNotFoundError:
        # Windows pode nao ter a base IANA; Sao Paulo usa UTC-3 atualmente.
        fuso = timezone(timedelta(hours=-3))
    return datetime.now(fuso).date()


def resolver_data(dia: str, hoje: date) -> date:
    """Resolve uma preferencia ou levanta ValueError com orientacao ao cliente."""
    relativos = {"hoje": 0, "amanhã": 1, "depois de amanhã": 2}
    semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
              "sexta-feira", "sábado", "domingo"]
    if dia in relativos:
        return hoje + timedelta(days=relativos[dia])
    if dia in semana:
        return hoje + timedelta(days=(semana.index(dia) - hoje.weekday()) % 7)
    if dia in {"ontem", "anteontem"}:
        raise ValueError("Essa data já passou. Informe hoje ou uma data futura.")
    if not re.fullmatch(r"\d{1,2}/\d{1,2}(?:/\d{4})?", dia):
        raise ValueError("Data inválida. Use dia/mês ou dia/mês/ano com quatro dígitos.")
    partes = [int(item) for item in dia.split("/")]
    try:
        data = date(partes[2] if len(partes) == 3 else hoje.year, partes[1], partes[0])
    except ValueError:
        raise ValueError("Data inválida no calendário. Confira o dia, o mês e o ano.") from None
    if data < hoje:
        raise ValueError(
            "Essa data já passou. Sem ano, considero o ano atual. "
            "Informe uma data futura com o ano, por exemplo dia/mês/ano."
        )
    return data


def extrair_detalhes(mensagem: str) -> tuple[str | None, str | None, bool]:
    """Extrai detalhes por palavras inteiras; pede esclarecimento se houver duvida."""
    entrada = normalizar(mensagem).replace("depois de amanha", "depois_de_amanha")
    portes = {"pequeno": "pequeno", "medio": "médio", "grande": "grande"}
    dias = {
        "hoje": "hoje", "amanha": "amanhã",
        "depois_de_amanha": "depois de amanhã", "ontem": "ontem", "anteontem": "anteontem",
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
        numericas = set(re.findall(r"(?<![\w/])\d{1,4}/\d{1,4}(?:/\d{1,4})?(?![\w/])", trecho))
        if (p or d or numericas) and palavras & NEGACOES:
            ambiguo = True
        encontrados_porte.update(portes[item] for item in p)
        encontrados_dia.update(dias[item] for item in d)
        encontrados_dia.update(numericas)
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
    data_desejada: date | None = None
    em_revisao: bool = False
    relogio: Callable[[], date] = field(default=hoje_sao_paulo, repr=False)

    def reiniciar(self) -> None:
        self.servico = self.porte = self.dia = None
        self.data_desejada = None
        self.em_revisao = False

    def resumo(self) -> str:
        return (
            f"Resumo da solicitação: {self.servico}; porte {self.porte}; "
            f"dia desejado: {self.dia} ({self.data_desejada:%d/%m/%Y}). "
            "Agendamento não confirmado: depende da disponibilidade do pet shop. "
        )

    def responder(self, mensagem: str) -> str:
        entrada = normalizar(mensagem)
        if entrada in {"cancelar", "reiniciar"}:
            self.reiniciar()
            return "Solicitação descartada. Qual serviço você procura?"
        if not entrada:
            return "Digite uma mensagem para continuar ou 'cancelar' para recomeçar."

        hoje = self.relogio()
        if entrada == "confirmar":
            if not self.em_revisao:
                return "Ainda faltam dados para revisar a solicitação. Informe serviço, porte e dia."
            if self.data_desejada is None or self.data_desejada < hoje:
                self.dia = None
                self.data_desejada = None
                self.em_revisao = False
                return "O dia informado anteriormente já passou. Para qual nova data deseja solicitar?"
            resposta = (
                self.resumo()
                + "Solicitação revisada e concluída nesta demonstração. "
                "Nada foi enviado ao pet shop. Para iniciar outra, informe o serviço."
            )
            self.reiniciar()
            return resposta

        categoria = classificar_mensagem(mensagem)
        porte, dia, ambiguo = extrair_detalhes(mensagem)
        if ambiguo:
            return (
                "Preciso esclarecer os detalhes. Informe um único porte "
                "(pequeno, médio ou grande) e um único dia desejado, "
                "sem alternativas ou negações. O pedido anterior foi mantido."
            )

        data = None
        if dia is not None:
            try:
                data = resolver_data(dia, hoje)
            except ValueError as erro:
                return f"{erro} O pedido anterior foi mantido."

        novo_servico = categoria != "Atendimento geral"
        if novo_servico:
            if self.servico is not None and self.servico != categoria and not self.em_revisao:
                self.reiniciar()
            self.servico = categoria
        if porte is not None:
            self.porte = porte
        if dia is not None:
            self.dia = dia
            self.data_desejada = data

        if self.data_desejada is not None and self.data_desejada < hoje:
            self.dia = None
            self.data_desejada = None
            self.em_revisao = False
            return "O dia informado anteriormente já passou. Para qual nova data deseja solicitar?"

        if self.servico is None:
            return gerar_resposta("Atendimento geral")
        if self.porte is None:
            return gerar_resposta(self.servico)
        if self.dia is None:
            return "Para qual dia? Responda hoje, amanhã, um dia da semana ou uma data (dia/mês/ano)."

        self.em_revisao = True
        return (
            self.resumo()
            + "Confira os dados. Digite 'confirmar' para concluir a solicitação, "
            "informe outro serviço, porte ou dia para corrigir, "
            "ou digite 'cancelar' para descartar."
        )


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
