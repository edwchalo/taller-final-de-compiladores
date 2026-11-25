import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))

from compiler import compile_code, PHASE_ORDER


def later_phases_after(failed_key):
    index = PHASE_ORDER.index(failed_key)
    return PHASE_ORDER[index + 1 :]


class CasosDeDemostracionTest(unittest.TestCase):
    def test_1_compilacion_exitosa(self):
        result = compile_code("a = 10\nb = 5\nresultado = (a + b) * 2")
        self.assertTrue(result["success"])
        self.assertIsNone(result["error"])
        for name in PHASE_ORDER:
            self.assertEqual(result["phases"][name]["status"], "ok")
        self.assertIn("t1 = a + b", result["phases"]["intermediate"]["code"])
        self.assertIn("resultado = 30", result["phases"]["optimization"]["after"])

    def test_2_error_lexico(self):
        result = compile_code("a = 10 @ 5")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["type"], "ERROR LÉXICO")
        self.assertIn("@", result["error"]["description"])
        self.assertEqual(result["phases"]["lexical"]["status"], "error")
        for name in later_phases_after("lexical"):
            self.assertEqual(result["phases"][name]["status"], "skipped")

    def test_3_error_sintactico(self):
        result = compile_code("x = 10 +")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["type"], "ERROR SINTÁCTICO")
        self.assertEqual(result["phases"]["lexical"]["status"], "ok")
        self.assertEqual(result["phases"]["syntax"]["status"], "error")
        for name in later_phases_after("syntax"):
            self.assertEqual(result["phases"][name]["status"], "skipped")

    def test_4_error_semantico(self):
        result = compile_code("resultado = a + 5")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["type"], "ERROR SEMÁNTICO")
        self.assertIn('variable "a" no declarada', result["error"]["description"])
        self.assertEqual(result["phases"]["semantic"]["status"], "error")
        for name in later_phases_after("semantic"):
            self.assertEqual(result["phases"][name]["status"], "skipped")

    def test_5_plegado_de_constantes(self):
        result = compile_code("x = 2 + 3")
        self.assertTrue(result["success"])
        techniques = [
            item["technique"] for item in result["phases"]["optimization"]["applied"]
        ]
        self.assertIn("Plegado de constantes", techniques)
        self.assertEqual(result["phases"]["optimization"]["after"], ["x = 5"])

    def test_6_simplificacion_algebraica(self):
        result = compile_code("a = 10\nresultado = a * 1")
        self.assertTrue(result["success"])
        techniques = [
            item["technique"] for item in result["phases"]["optimization"]["applied"]
        ]
        self.assertIn("Simplificación algebraica", techniques)
        self.assertIn("t1 = a * 1", result["phases"]["optimization"]["before"])

    def test_7_generacion_de_ensamblador(self):
        result = compile_code("a = 10\nb = 5\nresultado = (a + b) * 2")
        self.assertTrue(result["success"])
        assembly = result["phases"]["assembly"]
        code_text = "\n".join(assembly["code"])
        self.assertIn("R0", assembly["architecture"])
        self.assertIn("x86", assembly["architecture"].lower())
        self.assertIn("MOV R0", code_text)
        self.assertIn("MOV resultado, R0", code_text)


if __name__ == "__main__":
    unittest.main()
