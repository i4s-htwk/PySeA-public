import unittest
import os
import zipfile
from difflib import unified_diff
import shutil
import xml.etree.ElementTree as ET

from backend.stores import TestStore


def format_xml(filename):
    from xml.dom import minidom
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.strip()
    dom = minidom.parseString(content)
    return dom.toprettyxml(indent="  ")

class TestConfig:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Falls diese Datei in PySeA/tests/integration/ liegt:
    TEST_DIR = os.path.dirname(BASE_DIR)

    PROJECT_DIR = os.path.dirname(TEST_DIR)

    INPUT_DIR = os.path.join(TEST_DIR, "integration_test_data", "input_dir")
    REFERENCE_DIR = os.path.join(TEST_DIR, "integration_test_data", "reference")

    OUTPUT_DIR = os.path.join(TEST_DIR, "integration_test_data", "output_dir")
    TEMP_DIR = os.path.join(TEST_DIR, "integration_test_data", "tmp_dir")

    @classmethod
    def get_test_configs(cls):
        """
        Erstellt die Test-Konfigurationen automatisch.

        Erwartung:
        - In INPUT_DIR liegen JSON-Dateien.
        - In REFERENCE_DIR liegen ZIP-Dateien.
        - Zu jeder JSON-Datei muss eine passende ZIP-Datei existieren.

        Die Zuordnung erfolgt aktuell über die Reihenfolge der sortierten Dateien.
        """
        if not os.path.exists(cls.INPUT_DIR):
            raise FileNotFoundError(f"Input-Ordner nicht gefunden: {cls.INPUT_DIR}")

        if not os.path.exists(cls.REFERENCE_DIR):
            raise FileNotFoundError(f"Reference-Ordner nicht gefunden: {cls.REFERENCE_DIR}")

        json_files = sorted(
            file for file in os.listdir(cls.INPUT_DIR)
            if file.endswith(".json")
        )

        reference_zips = sorted(
            file for file in os.listdir(cls.REFERENCE_DIR)
            if file.endswith(".zip")
        )

        if len(json_files) != len(reference_zips):
            raise AssertionError(
                "Anzahl der JSON-Dateien und Referenz-ZIP-Dateien stimmt nicht überein.\n"
                f"JSON-Dateien: {len(json_files)}\n"
                f"Referenz-ZIPs: {len(reference_zips)}\n\n"
                f"JSON-Dateien:\n{json_files}\n\n"
                f"Referenz-ZIPs:\n{reference_zips}"
            )

        configs = []

        for json_file, reference_zip in zip(json_files, reference_zips):
            configs.append(
                {
                    "name": os.path.splitext(json_file)[0],
                    "json_file": os.path.join(cls.INPUT_DIR, json_file),
                    "reference_zip": os.path.join(cls.REFERENCE_DIR, reference_zip),
                    "output_name": reference_zip
                }
            )

        return configs


class TestQTIPackage(unittest.TestCase):
    def setUp(self):
        """Testumgebung vorbereiten"""
        self.maxDiff = None

        if os.path.exists(TestConfig.OUTPUT_DIR):
            shutil.rmtree(TestConfig.OUTPUT_DIR)

        if os.path.exists(TestConfig.TEMP_DIR):
            shutil.rmtree(TestConfig.TEMP_DIR)

        os.makedirs(TestConfig.OUTPUT_DIR, exist_ok=True)
        os.makedirs(TestConfig.TEMP_DIR, exist_ok=True)

    def tearDown(self):
        """Testumgebung nach dem Test aufräumen."""
        if os.path.exists(TestConfig.OUTPUT_DIR):
            shutil.rmtree(TestConfig.OUTPUT_DIR)

        if os.path.exists(TestConfig.TEMP_DIR):
            shutil.rmtree(TestConfig.TEMP_DIR)

    def test_multiple_packages(self):
        """Testet mehrere QTI-Pakete"""
        all_errors = []

        test_configs = TestConfig.get_test_configs()

        for config in test_configs:
            try:
                with self.subTest(test_name=config["name"]):
                    if not os.path.exists(config["json_file"]):
                        raise AssertionError(f"JSON-Datei nicht gefunden: {config['json_file']}")

                    if not os.path.exists(config["reference_zip"]):
                        raise AssertionError(f"Referenz-ZIP nicht gefunden: {config['reference_zip']}")

                    test_zip_path = self.create_test_package(
                        config["json_file"],
                        config["output_name"]
                    )

                    if not os.path.exists(test_zip_path):
                        raise AssertionError(f"Generierte ZIP-Datei nicht gefunden: {test_zip_path}")

                    test_extract_dir = os.path.join(TestConfig.TEMP_DIR, config["name"], "test")
                    ref_extract_dir = os.path.join(TestConfig.TEMP_DIR, config["name"], "reference")

                    for dir_path in [test_extract_dir, ref_extract_dir]:
                        if os.path.exists(dir_path):
                            shutil.rmtree(dir_path)
                        os.makedirs(dir_path, exist_ok=True)

                    with zipfile.ZipFile(test_zip_path, 'r') as zip_ref:
                        zip_ref.extractall(test_extract_dir)

                    with zipfile.ZipFile(config["reference_zip"], 'r') as zip_ref:
                        zip_ref.extractall(ref_extract_dir)

                    self.compare_xml_files(test_extract_dir, ref_extract_dir)

            except Exception as e:
                all_errors.append(f"Fehler in {config['name']}: {str(e)}")

        if all_errors:
            self.fail("\n\n".join(all_errors))

    def create_test_package(self, json_file: str, output_name: str) -> str:
        test_data = TestStore.load_test(json_file)
        test_data.store_configurations.path_export = TestConfig.OUTPUT_DIR
        test_data.create_test(TestConfig.OUTPUT_DIR)

        return os.path.join(TestConfig.OUTPUT_DIR, output_name)

    def clean_tag(self, tag):
        """
        Entfernt Namespace aus einem XML-Tag.

        Aus:
          {http://www.imsglobal.org/xsd/imsqti_v2p1}assessmentItem

        wird:
          assessmentItem
        """
        if tag is None:
            return None

        if "}" in tag:
            return tag.split("}", 1)[1]

        return tag

    def normalize_xml_text(self, text):
        """
        Normalisiert XML-Text, damit reine Formatierungsunterschiede
        nicht direkt als Fehler zählen.
        """
        if text is None:
            return ""

        return text.strip()

    def xml_to_string(self, element):
        """
        Wandelt ein XML-Element in einen lesbaren String um.
        """
        if element is None:
            return "  <fehlt>"

        xml_string = ET.tostring(element, encoding="unicode")

        # Kürzen, damit Fehlermeldungen nicht wieder riesig werden
        max_length = 2000

        if len(xml_string) > max_length:
            return xml_string[:max_length] + "\n  ... gekürzt ..."

        return xml_string

    def find_xml_difference(self, ref_elem, test_elem, path):
        """
        Vergleicht zwei XML-Elemente rekursiv und liefert den ersten Unterschied.
        """

        # Tag-Name vergleichen
        if ref_elem.tag != test_elem.tag:
            return {
                "path": path,
                "reason": "Tag-Name unterschiedlich",
                "ref_value": self.clean_tag(ref_elem.tag),
                "test_value": self.clean_tag(test_elem.tag),
                "ref_element": ref_elem,
                "test_element": test_elem,
            }

        # Attribute vergleichen
        if ref_elem.attrib != test_elem.attrib:
            ref_only = {
                key: value
                for key, value in ref_elem.attrib.items()
                if test_elem.attrib.get(key) != value
            }

            test_only = {
                key: value
                for key, value in test_elem.attrib.items()
                if ref_elem.attrib.get(key) != value
            }

            return {
                "path": path,
                "reason": "Attribute unterschiedlich",
                "ref_value": ref_only,
                "test_value": test_only,
                "ref_element": ref_elem,
                "test_element": test_elem,
            }

        # Text vergleichen
        ref_text = self.normalize_xml_text(ref_elem.text)
        test_text = self.normalize_xml_text(test_elem.text)

        if ref_text != test_text:
            return {
                "path": path,
                "reason": "Textinhalt unterschiedlich",
                "ref_value": ref_text,
                "test_value": test_text,
                "ref_element": ref_elem,
                "test_element": test_elem,
            }

        # Anzahl der Kind-Elemente vergleichen
        ref_children = list(ref_elem)
        test_children = list(test_elem)

        if len(ref_children) != len(test_children):
            return {
                "path": path,
                "reason": "Anzahl der Kind-Elemente unterschiedlich",
                "ref_value": len(ref_children),
                "test_value": len(test_children),
                "ref_element": ref_elem,
                "test_element": test_elem,
            }

        # Kinder rekursiv vergleichen
        for index, (ref_child, test_child) in enumerate(zip(ref_children, test_children)):
            child_path = (f"{path}/{self.clean_tag(ref_child.tag)}[{index}]")

            difference = self.find_xml_difference(ref_child, test_child, child_path)

            if difference is not None:
                return difference

        # Tail-Text vergleichen, falls relevant
        ref_tail = self.normalize_xml_text(ref_elem.tail)
        test_tail = self.normalize_xml_text(test_elem.tail)

        if ref_tail != test_tail:
            return {"path": path, "reason": "Tail-Text unterschiedlich", "ref_value": ref_tail, "test_value": test_tail, "ref_element": ref_elem, "test_element": test_elem,}

        return None

    def parse_xml_or_fragment(self, filename):
        """
        Parst eine XML-Datei.

        Falls die Datei mehrere Root-Elemente enthält, wird sie als XML-Fragment
        behandelt und künstlich in ein gemeinsames Root-Element eingepackt.
        """
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read().strip()

        try:
            return ET.fromstring(content)
        except ET.ParseError:
            wrapped_content = f"<PYSEA_FRAGMENT_ROOT>{content}</PYSEA_FRAGMENT_ROOT>"
            return ET.fromstring(wrapped_content)

    def compare_single_xml_file(self, ref_file, test_file, relative_path):
        """
        Vergleicht zwei XML-Dateien strukturell.

        Dateien mit mehreren Root-Elementen werden als XML-Fragmente behandelt.
        """
        try:
            ref_root = self.parse_xml_or_fragment(ref_file)
            test_root = self.parse_xml_or_fragment(test_file)
        except ET.ParseError as e:
            return f"XML konnte nicht geparst werden in {relative_path}\nFehler: {e}"

        difference = self.find_xml_difference(
            ref_root,
            test_root,
            path=self.clean_tag(ref_root.tag)
        )

        if difference is None:
            return None

        message = [
            f"Inhalt unterschiedlich in {relative_path}",
            "",
            "XML-Pfad:",
            f"  {difference['path']}",
            "",
            "Art des Unterschieds:",
            f"  {difference['reason']}",
        ]

        if difference.get("ref_value") is not None or difference.get("test_value") is not None:
            message.extend([
                "",
                "Referenz-Wert:",
                f"  {difference.get('ref_value')}",
                "",
                "Generierter Wert:",
                f"  {difference.get('test_value')}",
            ])

        message.extend([
            "",
            "Referenz-Tag:",
            self.xml_to_string(difference.get("ref_element")),
            "",
            "Generierter Tag:",
            self.xml_to_string(difference.get("test_element")),
        ])

        return "\n".join(message)

    def compare_xml_files(self, test_dir, ref_dir):
        """Vergleicht den Inhalt aller XML-Dateien in beiden Verzeichnissen genauer."""
        errors = []

        for root, _, files in os.walk(test_dir):
            for file in files:
                if not file.endswith('.xml'):
                    continue

                test_file = os.path.join(root, file)
                relative_path = os.path.relpath(test_file, test_dir)
                ref_file = os.path.join(ref_dir, relative_path)

                if not os.path.exists(ref_file):
                    errors.append(f"Referenz-XML fehlt: {relative_path}")
                    continue

                xml_error = self.compare_single_xml_file(ref_file, test_file, relative_path)

                if xml_error:
                    errors.append(xml_error)

        if errors:
            self.fail("\n\n".join(errors))