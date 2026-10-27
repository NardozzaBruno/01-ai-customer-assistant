import subprocess
import sys
import unittest
from pathlib import Path

from main import classificar_mensagem


class ClassificadorTests(unittest.TestCase):
    def test_categorias(self):
        casos = [
            ("Quero agendar banho e tosa", "Banho e Tosa"),
            ("Preciso de uma tosa e um banho", "Banho e Tosa"),
            ("Qual o valor do banho?", "Banho"),
            ("Gostaria de agendar uma tosa", "Tosa"),
            ("Quero BANHO E TOSA", "Banho e Tosa"),
            ("Qual o horario de funcionamento?", "Atendimento geral"),
            ("", "Atendimento geral"),
            ("   ", "Atendimento geral"),
        ]
        for mensagem, esperado in casos:
            with self.subTest(mensagem=mensagem):
                self.assertEqual(classificar_mensagem(mensagem), esperado)

    def test_atendimento_no_terminal(self):
        resultado = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("main.py"))],
            input="Quero banho e tosa\n",
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Categoria: Banho e Tosa", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
