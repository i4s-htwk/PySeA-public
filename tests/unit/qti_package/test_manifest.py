import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace

from backend.QTI_Paket.Manifest import Manifest


def image(image_id, href):
    return SimpleNamespace(
        id=image_id,
        href=href
    )

def variant_dependent_image(image_id):
    return SimpleNamespace(
        id=image_id
    )

def task(
    task_id,
    images_used=None,
    variant_dependent_images=None
):
    return SimpleNamespace(
        id=task_id,
        images_used=images_used or [],
        variant_dependent_images=variant_dependent_images or []
    )

def section(
    section_id,
    images_used=None,
    list_tasks=None
):
    return SimpleNamespace(
        id=section_id,
        images_used=images_used or [],
        list_tasks=list_tasks or []
    )

class TestManifest(unittest.TestCase):

    def test_manifest_creates_imsmanifest_file(self):
        test_structure = SimpleNamespace(
            list=[
                section(
                    section_id="section1",
                    list_tasks=[
                        task("task11")
                    ]
                )
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Manifest(test_structure, tmp)

            expected_path = os.path.join(tmp, "imsmanifest.xml")

            self.assertEqual(manifest.file_path, expected_path)
            self.assertTrue(os.path.exists(expected_path))

            ET.parse(expected_path)

    def test_manifest_root_has_required_attributes(self):
        test_structure = SimpleNamespace(
            list=[
                section(
                    section_id="section1",
                    list_tasks=[
                        task("task11")
                    ]
                )
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Manifest(test_structure, tmp)

            self.assertEqual(manifest.root.tag, "manifest")
            self.assertEqual(
                manifest.root.attrib["identifier"],
                "assessmenttest_manifest"
            )
            self.assertIn("xmlns", manifest.root.attrib)
            self.assertIn("xmlns:imsqti", manifest.root.attrib)
            self.assertIn("xsi:schemaLocation", manifest.root.attrib)

    def test_manifest_contains_assessmenttest_resource(self):
        test_structure = SimpleNamespace(
            list=[
                section(
                    section_id="section1",
                    list_tasks=[
                        task("task11")
                    ]
                )
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Manifest(test_structure, tmp)

            assessmenttest_resource = manifest.root.find(
                "./resources/resource[@identifier='id_assessmenttest']"
            )

            self.assertIsNotNone(assessmenttest_resource)
            self.assertEqual(
                assessmenttest_resource.attrib["type"],
                "imsqti_test_xmlv2p1"
            )
            self.assertEqual(
                assessmenttest_resource.attrib["href"],
                "assessmenttest.xml"
            )

            assessmenttest_file = assessmenttest_resource.find(
                "./file[@href='assessmenttest.xml']"
            )

            self.assertIsNotNone(assessmenttest_file)

    def test_manifest_contains_task_resources_and_dependencies(self):
        test_structure = SimpleNamespace(
            list=[
                section(
                    section_id="section1",
                    list_tasks=[
                        task("task11"),
                        task("task12")
                    ]
                )
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Manifest(test_structure, tmp)

            resources = manifest.root.find("resources")
            self.assertIsNotNone(resources)

            task11_resource = resources.find(
                "./resource[@identifier='id_task11']"
            )
            task12_resource = resources.find(
                "./resource[@identifier='id_task12']"
            )

            self.assertIsNotNone(task11_resource)
            self.assertIsNotNone(task12_resource)

            self.assertEqual(
                task11_resource.attrib["type"],
                "imsqti_item_xmlv2p1"
            )
            self.assertEqual(
                task11_resource.attrib["href"],
                "task11.xml"
            )

            task11_file = task11_resource.find("./file[@href='task11.xml']")
            task12_file = task12_resource.find("./file[@href='task12.xml']")

            self.assertIsNotNone(task11_file)
            self.assertIsNotNone(task12_file)

            assessmenttest_resource = resources.find(
                "./resource[@identifier='id_assessmenttest']"
            )

            dependency_task11 = assessmenttest_resource.find(
                "./dependency[@identifierref='id_task11']"
            )
            dependency_task12 = assessmenttest_resource.find(
                "./dependency[@identifierref='id_task12']"
            )

            self.assertIsNotNone(dependency_task11)
            self.assertIsNotNone(dependency_task12)

    def test_manifest_adds_section_and_task_images_to_assessmenttest_resource(self):
        test_structure = SimpleNamespace(
            list=[
                section(
                    section_id="section1",
                    images_used=[
                        image("SECTION_IMAGE", "section.png")
                    ],
                    list_tasks=[
                        task(
                            "task11",
                            images_used=[
                                image("TASK_IMAGE", "task.png")
                            ]
                        )
                    ]
                )
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Manifest(test_structure, tmp)

            assessmenttest_resource = manifest.root.find(
                "./resources/resource[@identifier='id_assessmenttest']"
            )

            section_image_file = assessmenttest_resource.find(
                "./file[@href='media/section.png']"
            )
            task_image_file = assessmenttest_resource.find(
                "./file[@href='media/task.png']"
            )

            self.assertIsNotNone(section_image_file)
            self.assertIsNotNone(task_image_file)

    def test_manifest_adds_variant_dependent_image_templates(self):
        test_structure = SimpleNamespace(
            list=[
                section(
                    section_id="section1",
                    list_tasks=[
                        task(
                            "task11",
                            variant_dependent_images=[
                                variant_dependent_image("V_BILD_1"),
                                variant_dependent_image("V_BILD_2")
                            ]
                        )
                    ]
                )
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Manifest(test_structure, tmp)

            assessmenttest_resource = manifest.root.find(
                "./resources/resource[@identifier='id_assessmenttest']"
            )

            template_1 = assessmenttest_resource.find(
                "./file[@href='templates/task11/V_BILD_1.xml']"
            )
            template_2 = assessmenttest_resource.find(
                "./file[@href='templates/task11/V_BILD_2.xml']"
            )

            self.assertIsNotNone(template_1)
            self.assertIsNotNone(template_2)

    def test_manifest_adds_redtick_css_for_each_task(self):
        test_structure = SimpleNamespace(
            list=[
                section(
                    section_id="section1",
                    list_tasks=[
                        task("task11"),
                        task("task12")
                    ]
                )
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Manifest(test_structure, tmp)

            assessmenttest_resource = manifest.root.find(
                "./resources/resource[@identifier='id_assessmenttest']"
            )

            css_task11 = assessmenttest_resource.find(
                "./file[@href='files/task11/redtick-display-none.css']"
            )
            css_task12 = assessmenttest_resource.find(
                "./file[@href='files/task12/redtick-display-none.css']"
            )

            self.assertIsNotNone(css_task11)
            self.assertIsNotNone(css_task12)

    def test_manifest_adds_editordata_resource_and_file_reference(self):
        test_structure = SimpleNamespace(
            list=[
                section(
                    section_id="section1",
                    list_tasks=[
                        task("task11")
                    ]
                )
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Manifest(test_structure, tmp)

            resources = manifest.root.find("resources")

            editordata_resource = resources.find(
                "./resource[@identifier='id_editordata']"
            )

            self.assertIsNotNone(editordata_resource)
            self.assertEqual(editordata_resource.attrib["type"], "webcontent")
            self.assertEqual(
                editordata_resource.attrib["href"],
                "files/assessmenttest/editordata.json"
            )

            editordata_file = editordata_resource.find(
                "./file[@href='files/assessmenttest/editordata.json']"
            )

            self.assertIsNotNone(editordata_file)

            assessmenttest_resource = resources.find(
                "./resource[@identifier='id_assessmenttest']"
            )

            editordata_reference = assessmenttest_resource.find(
                "./file[@href='files/assessmenttest/editordata.json']"
            )

            self.assertIsNotNone(editordata_reference)


if __name__ == "__main__":
    unittest.main()