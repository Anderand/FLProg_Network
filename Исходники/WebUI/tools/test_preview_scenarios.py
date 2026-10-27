from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PreviewScenariosTest(unittest.TestCase):
    def test_scenarios_and_simulator_integration(self):
        subprocess.run(['node',str(ROOT/'tools/test_preview_scenarios.js'),
                        str(ROOT/'editor/public/preview-scenarios.js'),
                        str(ROOT/'editor/public/preview-simulator.js')],check=True)

if __name__=='__main__':unittest.main()
