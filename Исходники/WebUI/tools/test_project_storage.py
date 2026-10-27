import tempfile, unittest
from pathlib import Path
from project_storage import project_locations

class ProjectStorageTest(unittest.TestCase):
    def test_external_project_contains_document_and_libraries(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'User projects'/'a123'
            doc,libs=project_locations({'project':{'id':'a123'},'projectFolder':str(root)},'/unused','/unused')
            self.assertEqual(doc,root/'a123.flpui')
            self.assertEqual(libs,root/'libraries')
            self.assertFalse(root.exists())
    def test_legacy_paths_preserved(self):
        doc,libs=project_locations({'project':{'id':'a123'}},Path.cwd()/'projects',Path.cwd()/'packages')
        self.assertEqual(doc,Path.cwd()/'projects/a123.flpui')
        self.assertEqual(libs,Path.cwd()/'packages')
    def test_relative_project_folder_rejected(self):
        with self.assertRaises(ValueError):
            project_locations({'project':{'id':'a123'},'projectFolder':'relative/a123'},'.','.')
