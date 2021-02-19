import os
from unittest import TestCase

from queridodiario_toolbox import Gazette, Page
from queridodiario_toolbox.etl.file_transform import *
from queridodiario_toolbox.process import *


class TextExtractionTests(TestCase):
    def setUp(self):
        ROOT = "tests/bin"
        self.TIKA_PATH = ROOT + "/tika-app-1.24.1.jar"
        self.TABULA_PATH = ROOT + "/tabula-1.0.4-jar-with-dependencies.jar"

    def tearDown(self):
        self.clean_txt_file_generated_during_tests()

    # definition of helper functions
    def clean_txt_file_generated_during_tests(self):
        for root, dirs, files in os.walk("tests/data/"):
            for generated_file in self.get_files_generated_during_tests(
                root, files
            ):
                os.remove(generated_file)

    def get_files_generated_during_tests(self, root, files):
        for f in files:
            if f in [
                "fake_gazette.txt",
                "fake_cpf_cnpj.txt",
                "multiple_columns.txt",
                "multiple_columns.json",
            ]:
                yield f"{root}{f}"

    def process_gazette_text(self, filepath):
        gazette = Gazette(filepath=filepath, apache_tika_jar=self.TIKA_PATH)
        gazette.extract_content()
        gazette.load_content()
        text = gazette.process_text()
        return text

    def validate_basic_extract_content(self, gazette, metadata=False):
        if metadata:
            target = "tests/data/fake_gazette.json"
        else:
            target = "tests/data/fake_gazette.txt"

        gazette.extract_content(metadata=metadata)
        self.assertEqual(gazette.filepath, target)

        gazette.load_content()
        self.assertNotEqual(0, len(gazette.content))

        if metadata:
            self.assertIsInstance(gazette.content, dict)
            self.assertNotEqual(gazette.content.items(), None)
        else:
            self.assertIn("Querido", gazette.content, "Extraction Failed")

    # filetype tests
    def test_extract_text_from_invalid_file(self):
        with self.assertRaisesRegex(Exception, "No such file"):
            gazette = Gazette("file/does/not/exist", self.TIKA_PATH)
            gazette.extract_content()

    def test_extract_metadata_from_invalid_file(self):
        with self.assertRaisesRegex(Exception, "No such file"):
            gazette = Gazette("file/does/not/exist", self.TIKA_PATH)
            gazette.extract_content(metadata=True)

    def test_extract_text_using_invalid_apache_tika_jar_path(self):
        with self.assertRaisesRegex(Exception, "File does not exist"):
            gazette = Gazette("tests/data/fake_gazette.pdf", "/tika/path")
            gazette.extract_content()

    def test_extract_metadata_using_invalid_apache_tika_jar_path(self):
        with self.assertRaisesRegex(Exception, "File does not exist"):
            gazette = Gazette("tests/data/fake_gazette.pdf", "/tika/path")
            gazette.extract_content(metadata=True)

    def test_extract_text_using_invalid_file_type_apache_tika(self):
        with self.assertRaisesRegex(Exception, "Expected Apache Tika jar"):
            gazette = Gazette(
                "tests/data/fake_gazette.pdf", "tests/data/fake_gazette.pdf"
            )
            gazette.extract_content(metadata=True)

    def test_extract_metadata_using_invalid_file_type_apache_tika(self):
        with self.assertRaisesRegex(Exception, "Expected Apache Tika jar"):
            gazette = Gazette(
                "tests/data/fake_gazette.pdf", "tests/data/fake_gazette.pdf",
            )
            gazette.extract_content(metadata=True)

    def test_extract_text_from_invalid_file_type_should_fail(self):
        with self.assertRaisesRegex(Exception, "Unsupported file type"):
            gazette = Gazette("tests/data/fake_gazette.m4a", self.TIKA_PATH)
            gazette.extract_content()

    def test_extract_metadata_from_invalid_file_type_should_fail(self):
        with self.assertRaisesRegex(Exception, "Unsupported file type"):
            gazette = Gazette("tests/data/fake_gazette.m4a", self.TIKA_PATH)
            gazette.extract_content(metadata=True)

    # class instantiation tests
    def test_empty_class_instantiation_should_fail(self):
        with self.assertRaises(Exception):
            Gazette()

    def test_class_instantiation_with_tika_path_but_no_filepath(self):
        with self.assertRaises(Exception):
            gazette = Gazette(apache_tika_jar=self.TIKA_PATH)

    def test_class_instantiation_with_content(self):
        gazette = Gazette(content="tests/data/fake_content.txt")
        self.assertNotEqual(gazette.content, None)

    def test_class_instantiation_with_no_content(self):
        gazette = Gazette(
            filepath="tests/data/fake_gazette.pdf",
            apache_tika_jar=self.TIKA_PATH,
        )
        self.assertNotEqual(gazette.filepath, None)
        self.assertNotEqual(gazette.tika_jar, None)
        self.assertEqual(gazette.content, None)

    def test_class_instantiation_with_no_filepath(self):
        gazette = Gazette(
            apache_tika_jar=self.TIKA_PATH,
            content="tests/data/fake_content.txt",
        )
        self.assertEqual(gazette.filepath, None)
        self.assertNotEqual(gazette.tika_jar, None)
        self.assertNotEqual(gazette.content, None)

    def test_class_instantiation_with_all_arguments(self):
        gazette = Gazette(
            filepath="tests/data/fake_gazette.pdf",
            apache_tika_jar=self.TIKA_PATH,
            content="tests/data/fake_content.txt",
        )
        self.assertNotEqual(gazette.filepath, None)
        self.assertNotEqual(gazette.tika_jar, None)
        self.assertNotEqual(gazette.content, None)

    # content extraction tests
    def test_extract_text_from_doc_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.doc", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette)

    def test_extract_text_from_docx_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.docx", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette)

    def test_extract_text_from_odt_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.odt", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette)

    def test_extract_text_from_html_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.html", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette)

    def test_extract_text_from_pdf_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.pdf", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette)

    def test_extract_text_from_jpeg_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.jpeg", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette)

    def test_extract_text_from_png_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.png", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette)

    def test_extract_text_from_tiff_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.tiff", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette)

    # metadata extraction tests
    def test_extract_metadata_from_doc_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.doc", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette, metadata=True)

    def test_extract_metadata_from_docx_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.docx", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette, metadata=True)

    def test_extract_metadata_from_odt_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.odt", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette, metadata=True)

    def test_extract_metadata_from_html_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.html", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette, metadata=True)

    def test_extract_metadata_from_pdf_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.pdf", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette, metadata=True)

    def test_extract_metadata_from_jpeg_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.jpeg", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette, metadata=True)

    def test_extract_metadata_from_png_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.png", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette, metadata=True)

    def test_extract_metadata_from_tiff_should_return_content(self):
        gazette = Gazette("tests/data/fake_gazette.tiff", self.TIKA_PATH)
        self.validate_basic_extract_content(gazette, metadata=True)

    # text linearization tests
    def test_gazette_text_is_linearized(self):
        gazette = Gazette("tests/data/multiple_columns.pdf", self.TIKA_PATH)
        gazette.extract_content()
        gazette.load_content()
        text = gazette.process_text()
        self.assertNotIn("-\n", text, "Text Processing Failed")

    def test_page_table_has_been_extracted(self):
        page = Page(
            filepath="tests/data/fake_table.pdf",
            apache_tika_jar=self.TIKA_PATH,
            tabula_jar=self.TABULA_PATH,
        )
        content = page.extract_table()

        table = content.split("\r\n")
        table = filter(None, table)
        matrix = [row.split(",") for row in table]

        matrix_size = [len(element) for element in matrix]
        self.assertEqual(matrix_size, [2, 2])

    # cpf and cnpj extraction tests
    def test_cpf_has_been_extracted(self):
        text = self.process_gazette_text("tests/data/fake_cpf_cnpj.pdf")
        cpfs = Gazette.scan_cpf(text)
        self.assertEqual(len(cpfs), 6)

    def test_cnpj_has_been_extracted(self):
        text = self.process_gazette_text("tests/data/fake_cpf_cnpj.pdf")
        cnpj = Gazette.scan_cnpj(text)
        self.assertIsNotNone(len(cnpj), 4)

    def test_cpf_has_been_validated(self):
        text = self.process_gazette_text("tests/data/fake_cpf_cnpj.pdf")
        cpfs = Gazette.scan_cpf(text, validate=True)
        self.assertEqual(len(cpfs), 4)

    def test_cnpj_has_been_validated(self):
        text = self.process_gazette_text("tests/data/fake_cpf_cnpj.pdf")
        cnpj = Gazette.scan_cnpj(text, validate=True)
        self.assertEqual(len(cnpj), 3)
