import subprocess
import sys
import unittest
from pathlib import Path

from main import classificar_mensagem


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

    def executar_terminal(self, entrada):
        resultado = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("main.py"))],
            input=entrada,
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stderr, "")
        return resultado


if __name__ == "__main__":
    unittest.main()
