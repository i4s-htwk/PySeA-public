import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
import copy

from backend.utils import Image, Response
from backend.QTI_Paket import AssessmentTest, Manifest, EditorData
from pathlib import Path

class CreateTest:
    def __init__(self, teststructure, images, item_body, responses, configurations, tables, feedbacks, selections, matchings, graphical_assignment, variants, output_dir):
        PROJECT_ROOT = Path(__file__).resolve().parent.parent
        temp_dir = PROJECT_ROOT / "tmp_dir"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        graphical_assignment.prepare_all()
        responses.open_excelfiles()

        EditorData(configurations, feedbacks, images, item_body, responses, selections, matchings, graphical_assignment, tables, variants, teststructure, output_dir)

        ### ändern
        store_images = images.to_dict()
        if "images" in store_images:
            for bild in store_images["images"]:
                teststructure.images_used.append(
                    Image(bild["href"], bild["id"], bild["width"], bild["height"], bild["ratio"]))
                teststructure.path_images = store_images["path_images"]

        if variants.use_variants:
            self.add_variants(variants, teststructure, responses, item_body, feedbacks)
        self.variant_dependent_tables_to_tasks(teststructure)

        max_score = 0
        current_parent_id = None
        for section in teststructure.list:
            for task in section.list_tasks:
                if variants.use_variants and task.id == variants.task_id:
                    task.create_assessmentitem_variant_assignment(teststructure.images_used, item_body, responses, feedbacks, variants, temp_dir)
                    max_score += 1
                else:
                    score = task.create_assessmentitem(teststructure.images_used, configurations.answer_acc, item_body, responses,
                                               tables, feedbacks, selections, matchings, graphical_assignment, variants, configurations, temp_dir)
                    if task.parent_id is None or task.parent_id != current_parent_id:
                        max_score += score
                        current_parent_id = task.parent_id

        test_path = AssessmentTest(configurations, teststructure.list, teststructure.images_used, item_body, variants, max_score, tables, temp_dir)
        manifest_path = Manifest(teststructure, temp_dir)
        self.create_template_folder(teststructure, teststructure.images_used, temp_dir)
        zip_destination_folder = os.path.join(output_dir, configurations.title.replace(" ", "")+".zip")
        os.makedirs(os.path.dirname(zip_destination_folder), exist_ok=True)

        graphical_media_paths = {}
        for assignment in graphical_assignment.items.values():
            for media_path in assignment.get_media_paths():
                file_name = os.path.basename(media_path)
                graphical_media_paths[file_name] = media_path
        def get_image_source_path(href: str) -> str:
            if href in graphical_media_paths:
                return graphical_media_paths[href]
            return os.path.join(teststructure.path_images, href)

        with zipfile.ZipFile(zip_destination_folder, "w") as zipf:
            written_files = set()
            def write_once(source_path, arcname):
                if arcname in written_files:
                    return
                zipf.write(source_path, arcname=arcname)
                written_files.add(arcname)
            write_once(os.path.join(temp_dir, os.path.basename(test_path.file_path)),os.path.basename(test_path.file_path))
            write_once(os.path.join(temp_dir, os.path.basename(manifest_path.file_path)),os.path.basename(manifest_path.file_path))
            templates_path = os.path.join(temp_dir, "templates")

            for root, dirs, files in os.walk(templates_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.join("templates", os.path.relpath(full_path, templates_path))
                    write_once(full_path, arcname)

            for section_obj in teststructure.list:
                for f in section_obj.images_used:
                    href = f.href
                    path_image = get_image_source_path(href)
                    write_once(path_image, os.path.join("media", href))

                for task_obj in section_obj.list_tasks:
                    task_xml_path = os.path.join(temp_dir, task_obj.id + ".xml")
                    write_once(task_xml_path, os.path.basename(task_obj.id + ".xml"))

                    for f in task_obj.images_used:
                        href = f.href
                        path_image = get_image_source_path(href)
                        write_once(path_image, os.path.join("media", href))

            for task, selection in selections.items.items():
                css_content = ".notansweredbutcorrect {\n    display: none;\n}"
                css_path = os.path.join(temp_dir, "redtick-display-none.css")

                with open(css_path, "w", encoding="utf-8") as f:
                    f.write(css_content)

                write_once(css_path, os.path.join("files", task, "redtick-display-none.css"))
        responses.close_excelfiles()



    def add_variants(self, variants, teststructure, responses, item_body, feedbacks):
        teststructure.add_variants(variants)
        responses.add_item(variants.task_id)
        responses[variants.task_id].responses.append(Response("RESPONSE", "0"))
        item_body.update_item(variants.task_id, variants.item_body)
        feedbacks.set_feedback_correct(variants.task_id, variants.feedback["feedback_correct"].value)
        feedbacks.add_feedback_incorrect(variants.task_id, variants.feedback["feedback_incorrect"].value)

    def create_template_folder(self, teststructure, images, temp_dir):
        base_path = os.path.join(temp_dir, "templates")
        os.makedirs(base_path, exist_ok=True)

        image_by_id = {image.id: image for image in images}
        for section in teststructure.list:
            for task in section.list_tasks:
                if not task.variant_dependent_images:
                    continue

                task_folder = os.path.join(base_path, str(task.id))
                if os.path.exists(task_folder):
                    shutil.rmtree(task_folder)
                os.makedirs(task_folder, exist_ok=True)

                for vdi in task.variant_dependent_images:
                    file_path = os.path.join(task_folder, f"{vdi.id}.xml")
                    elements = []
                    for entry in vdi.images.values():
                        image_id = entry.get("image_id")
                        if not image_id:
                            continue
                        image = image_by_id.get(image_id)
                        if not image:
                            continue
                        template_inline = ET.Element(
                            "templateInline",
                            {
                                "templateIdentifier": vdi.id,
                                "showHide": "show",
                                "identifier": image_id})

                        ET.SubElement(template_inline,"img",{"src": f"media/{image.href}","alt": "Image","width": image.width,"height": image.height})
                        elements.append(template_inline)

                    with open(file_path, "w", encoding="utf-8") as file:
                        for element in elements:
                            file.write(ET.tostring(element, encoding="unicode"))
                            file.write("\n")

    def variant_dependent_tables_to_tasks(self, teststructure):
        for section in teststructure.list:
            updated_tasks = []

            for task in section.list_tasks:
                if not task.variant_dependent_tables:
                    updated_tasks.append(task)
                    continue

                for i, vdt in enumerate(task.variant_dependent_tables):
                    for j, (key, table) in enumerate(vdt.tables.items()):
                        new_task = copy.deepcopy(task)
                        new_task.id = f"{task.id}_{i + 1}_{j + 1}"
                        new_task.parent_id = task.id

                        new_vdt = copy.deepcopy(vdt)
                        new_vdt.tables[key]["task_id"] = new_task.id
                        new_task.variant_dependent_tables = [new_vdt]

                        updated_tasks.append(new_task)

            section.list_tasks = updated_tasks


