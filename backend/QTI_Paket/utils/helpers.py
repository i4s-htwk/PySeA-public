import os
import xml.etree.ElementTree as ET

def insert_v_image(placeholder, p, item_body_tag, item):
    ET.SubElement(p, "include", {"href": "templates/" + item.id + "/" + placeholder + ".xml", "type": "text/xml"})
    div = ET.SubElement(item_body_tag, "div", {"style": "display:none;", "data-onyx-editor": "template-nonref"})
    ET.SubElement(div, "include", {"href": "templates/" + item.id + "/" + placeholder + ".xml", "type": "text/xml"})

def insert_image(placeholder, p, item, images):
    f = next((bild for bild in images if bild.id == placeholder), None)
    ET.SubElement(p, "img", {"src": "media/" + f.href, "width": f.width, "height": f.height, "id": f.id})
    item.images_used.append(f)

def append_text(p, text):
    if len(p):
        p[-1].tail = (p[-1].tail or "") + text
    else:
        p.text = (p.text or "") + text

def write_xml_document(root_tag, file_name, temp_dir):
    file_path = os.path.join(temp_dir, file_name)
    tree = ET.ElementTree(root_tag)
    tree.write(file_path, encoding="utf-8", xml_declaration=True)

    return file_path