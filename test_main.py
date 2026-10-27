import os
import subprocess
import sys
import unittest
from pathlib import Path

from main import classificar_mensagem, gerar_resposta


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
            ("Banho", "banho", "dia"),
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
        self.assertIn("solicitar o banho?", resultado.stdout)
        self.assertIn("pet para a tosa?", resultado.stdout)
        self.assertIn("solicitar banho e tosa?", resultado.stdout)
        self.assertIn("procura?", resultado.stdout)
        self.assertNotIn("Traceback", resultado.stderr)

    def test_saida_e_entrada_vazia_nao_geram_respostas(self):
        resultado = self.executar_terminal("\nsair\n")
        self.assertNotIn("Assistente:", resultado.stdout)

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


if __name__ == "__main__":
    unittest.main()
