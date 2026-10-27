import os
import subprocess
import sys
import unittest
from pathlib import Path

from main import Atendimento, classificar_mensagem, gerar_resposta


class ClassificadorTests(unittest.TestCase):
    def verificar_casos(self, casos):
        for mensagem, esperado in casos:
            with self.subTest(mensagem=mensagem):
                self.assertEqual(classificar_mensagem(mensagem), esperado)

    def test_categorias(self):
        self.verificar_casos([
            ("Quero agendar banho e tosa", "Banho e Tosa"),
            ("Preciso de uma tosa e um banho", "Banho e Tosa"),
            ("Qual o valor do banho?", "Banho"),
            ("Gostaria de agendar uma tosa", "Tosa"),
            ("Quero BANHO E TOSA", "Banho e Tosa"),
            ("Qual o horario de funcionamento?", "Atendimento geral"),
            ("", "Atendimento geral"),
            ("   ", "Atendimento geral"),
        ])

    def test_palavras_inteiras(self):
        self.verificar_casos([
            ("A comida estava gostosa", "Atendimento geral"),
            ("Foi um dia de trabalho trabalhoso", "Atendimento geral"),
            ("Quero banho, a comida estava gostosa", "Banho"),
            ("banho/tosa", "Banho e Tosa"),
            ("(BANHO) e [TOSA]", "Banho e Tosa"),
        ])

    def test_negacoes_simples(self):
        self.verificar_casos([
            ("não quero banho, só tosa", "Tosa"),
            ("nao quero banho, so tosa", "Tosa"),
            ("NÃO QUERO BANHO, SÓ TOSA", "Tosa"),
            ("Não quero tosa, só banho", "Banho"),
            ("Quero banho sem tosa", "Banho"),
            ("Quero tosa sem banho", "Tosa"),
            ("Não quero banho e tosa", "Atendimento geral"),
            ("Não quero banho nem tosa", "Atendimento geral"),
            ("Não quero banho, mas quero tosa", "Tosa"),
            ("Não quero banho mas quero tosa", "Tosa"),
            ("Sem banho; quero tosa", "Tosa"),
            ("Não quero banho. Quero tosa", "Tosa"),
            ("Quero banho e não quero tosa", "Banho"),
            ("Quero banho e tosa, mas sem tosa", "Banho"),
            ("Não quero banho, mudei de ideia: quero banho", "Banho"),
        ])

    def test_atendimento_no_terminal(self):
        resultado = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("main.py"))],
            input="nao quero banho, so tosa\nbanho\nsair\ntosa\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            timeout=5,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Categoria: Tosa", resultado.stdout)
        self.assertIn("Categoria: Banho", resultado.stdout)
        self.assertEqual(resultado.stdout.count("Categoria:"), 2)
        self.assertIn("Atendimento encerrado.", resultado.stdout)

    def test_sair_com_espacos_e_maiusculas(self):
        resultado = self.executar_terminal("  SAIR  \n")
        self.assertNotIn("Categoria:", resultado.stdout)
        self.assertEqual(resultado.stdout.count("Atendimento encerrado."), 1)

    def test_mensagem_vazia_permite_continuar(self):
        resultado = self.executar_terminal("   \nbanho\nsair\n")
        self.assertIn("Digite uma mensagem ou 'sair'", resultado.stdout)
        self.assertEqual(resultado.stdout.count("Categoria:"), 1)
        self.assertIn("Categoria: Banho", resultado.stdout)

    def test_fim_da_entrada_encerra_sem_erro(self):
        resultado = self.executar_terminal("banho\n")
        self.assertIn("Categoria: Banho", resultado.stdout)
        self.assertIn("Atendimento encerrado.", resultado.stdout)

    def test_respostas_por_categoria(self):
        casos = [
            ("Banho", "banho", "porte"),
            ("Tosa", "tosa", "porte"),
            ("Banho e Tosa", "banho e tosa", "porte"),
            ("Atendimento geral", "banho e tosa", "procura"),
        ]
        for categoria, servico, pergunta in casos:
            with self.subTest(categoria=categoria):
                resposta = gerar_resposta(categoria)
                self.assertIn(servico, resposta.lower())
                self.assertIn(pergunta, resposta.lower())
                self.assertTrue(resposta.endswith("?"))

    def test_categoria_desconhecida_recebe_orientacao_geral(self):
        self.assertEqual(
            gerar_resposta("desconhecida"), gerar_resposta("Atendimento geral")
        )

    def test_respostas_no_atendimento_continuo(self):
        resultado = self.executar_terminal(
            "banho\ntosa\nbanho e tosa\nola\nsair\n"
        )
        self.assertEqual(resultado.stdout.count("Assistente:"), 4)
        self.assertIn("Certo, banho!", resultado.stdout)
        self.assertIn("Certo, tosa!", resultado.stdout)
        self.assertIn("Certo, banho e tosa!", resultado.stdout)
        self.assertIn("cancelar", resultado.stdout)
        self.assertNotIn("Traceback", resultado.stderr)

    def test_saida_e_entrada_vazia_nao_geram_respostas(self):
        resultado = self.executar_terminal("\nsair\n")
        self.assertNotIn("Assistente:", resultado.stdout)

    def test_conversa_completa_no_terminal(self):
        resultado = self.executar_terminal("banho\npequeno\namanha\nsair\n")
        self.assertIn("Resumo da solicitação: Banho; porte pequeno", resultado.stdout)
        self.assertIn("dia desejado: amanhã", resultado.stdout)
        self.assertIn("Agendamento não confirmado", resultado.stdout)
        self.assertEqual(resultado.stdout.count("Categoria:"), 1)

    def test_mensagem_completa_natural_no_terminal(self):
        resultado = self.executar_terminal("quero banho para um pet grande amanha\nsair\n")
        self.assertIn("Banho; porte grande; dia desejado: amanhã", resultado.stdout)
        self.assertNotIn("Qual é o porte", resultado.stdout)

    def executar_terminal(self, entrada):
        resultado = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("main.py"))],
            input=entrada,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            timeout=5,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stderr, "")
        return resultado


class AtendimentoTests(unittest.TestCase):
    def test_guarda_contexto_e_limpa_apos_resumo(self):
        atendimento = Atendimento()
        atendimento.responder("quero banho")
        self.assertIn("dia", atendimento.responder("pequeno"))
        resumo = atendimento.responder("amanhã")
        self.assertIn("Banho; porte pequeno", resumo)
        self.assertIn("dia desejado: amanhã", resumo)
        self.assertIn("não confirmado", resumo)
        self.assertIsNone(atendimento.servico)
        self.assertIsNone(atendimento.porte)
        self.assertIsNone(atendimento.dia)

    def test_dia_pode_vir_antes_do_porte(self):
        atendimento = Atendimento()
        atendimento.responder("tosa")
        self.assertIn("porte", atendimento.responder("sexta-feira"))
        self.assertIn("Tosa; porte médio; dia desejado: sexta-feira", atendimento.responder("MÉDIO"))

    def test_detalhe_invalido_nao_perde_contexto(self):
        atendimento = Atendimento()
        atendimento.responder("banho e tosa")
        atendimento.responder("grande")
        for entrada in ["", "nao amanha", "qual o preco?", "32/13"]:
            with self.subTest(entrada=entrada):
                atendimento.responder(entrada)
                self.assertEqual(atendimento.servico, "Banho e Tosa")
                self.assertEqual(atendimento.porte, "grande")
                self.assertIsNone(atendimento.dia)
        self.assertIn("Banho e Tosa; porte grande", atendimento.responder("hoje"))

    def test_cancelar_e_reiniciar_descartam_detalhes(self):
        for comando in [" CANCELAR ", "reiniciar"]:
            with self.subTest(comando=comando):
                atendimento = Atendimento()
                atendimento.responder("banho")
                atendimento.responder("pequeno")
                atendimento.responder(comando)
                self.assertIsNone(atendimento.servico)
                self.assertIsNone(atendimento.porte)
                self.assertIsNone(atendimento.dia)
                self.assertIn("procura", atendimento.responder("amanha"))

    def test_troca_de_servico_inicia_outro_pedido(self):
        atendimento = Atendimento()
        atendimento.responder("banho")
        atendimento.responder("pequeno")
        atendimento.responder("nao quero banho, so tosa")
        self.assertEqual(atendimento.servico, "Tosa")
        self.assertIsNone(atendimento.porte)
        self.assertIsNone(atendimento.dia)

    def test_respostas_naturais(self):
        atendimento = Atendimento()
        atendimento.responder("quero banho")
        self.assertIn("dia", atendimento.responder("Meu pet é pequeno."))
        resumo = atendimento.responder("Pode ser amanhã.")
        self.assertIn("Banho; porte pequeno; dia desejado: amanhã", resumo)

    def test_todos_os_dados_na_primeira_mensagem(self):
        atendimento = Atendimento()
        resumo = atendimento.responder("Quero banho para um pet grande amanhã")
        self.assertIn("Banho; porte grande; dia desejado: amanhã", resumo)
        self.assertIsNone(atendimento.servico)

    def test_pergunta_apenas_o_que_falta(self):
        atendimento = Atendimento()
        pergunta = atendimento.responder("Banho e tosa para sexta-feira")
        self.assertIn("porte", pergunta)
        self.assertEqual(atendimento.dia, "sexta-feira")
        resumo = atendimento.responder("Meu pet é de porte médio")
        self.assertIn("Banho e Tosa; porte médio; dia desejado: sexta-feira", resumo)

    def test_detalhes_juntos_em_resposta(self):
        atendimento = Atendimento()
        atendimento.responder("tosa")
        resumo = atendimento.responder("Ele é pequeno e pode ser na terça-feira")
        self.assertIn("Tosa; porte pequeno; dia desejado: terça-feira", resumo)

    def test_repetir_servico_preserva_detalhes(self):
        atendimento = Atendimento()
        atendimento.responder("banho para pet pequeno")
        resumo = atendimento.responder("o banho pode ser amanhã")
        self.assertIn("Banho; porte pequeno; dia desejado: amanhã", resumo)

    def test_detalhes_ambiguos_nao_alteram_pedido(self):
        for entrada in [
            "amanha ou sexta", "pequeno ou grande", "nao amanha",
            "nao e pequeno", "nao amanha, sexta", "sem banho amanha",
        ]:
            with self.subTest(entrada=entrada):
                atendimento = Atendimento(servico="Banho", porte="medio")
                resposta = atendimento.responder(entrada)
                self.assertIn("esclarecer", resposta)
                self.assertEqual(atendimento.servico, "Banho")
                self.assertEqual(atendimento.porte, "medio")
                self.assertIsNone(atendimento.dia)

    def test_nao_extrai_fragmentos_de_palavras(self):
        atendimento = Atendimento(servico="Banho")
        atendimento.responder("a grandeza e a medianoche")
        self.assertIsNone(atendimento.porte)
        self.assertIsNone(atendimento.dia)

    def test_servico_com_negacao_e_detalhes_separados(self):
        atendimento = Atendimento()
        resumo = atendimento.responder("Nao quero banho, so tosa, pet pequeno amanha")
        self.assertIn("Tosa; porte pequeno; dia desejado: amanhã", resumo)

    def test_detalhes_antes_do_servico(self):
        atendimento = Atendimento()
        self.assertIn("procura", atendimento.responder("pet pequeno para amanha"))
        self.assertIn("Banho; porte pequeno; dia desejado: amanhã", atendimento.responder("banho"))

    def test_correcao_de_porte_antes_do_resumo(self):
        atendimento = Atendimento()
        atendimento.responder("banho para pet pequeno")
        atendimento.responder("na verdade ele e grande")
        self.assertEqual(atendimento.porte, "grande")
        self.assertIn("porte grande", atendimento.responder("amanha"))

    def test_sessoes_independentes(self):
        primeiro, segundo = Atendimento(), Atendimento()
        primeiro.responder("banho")
        self.assertIn("procura", segundo.responder("amanha"))
        self.assertIsNone(segundo.servico)


if __name__ == "__main__":
    unittest.main()
