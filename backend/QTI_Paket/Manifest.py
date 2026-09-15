import xml.etree.ElementTree as ET

from .utils import write_xml_document

class Manifest:
    def __init__(self, test_struktur, temp_dir):
        self.root = ET.Element("manifest", attrib={
            "xmlns": "http://www.imsglobal.org/xsd/imscp_v1p1",
            "xmlns:imsqti": "http://www.imsglobal.org/xsd/imsqti_v2p1",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/qti/qtiv2p1/qtiv2p1_imscpv1p2_v1p0.xsd http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1p1.xsd http://www.imsglobal.org/xsd/imsqti_metadata_v2p1 http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_metadata_v2p1p1.xsd http://ltsc.ieee.org/xsd/LOM http://www.imsglobal.org/xsd/imsmd_loose_v1p3p2.xsd http://www.w3.org/1998/Math/MathML http://www.w3.org/Math/XMLSchema/mathml2/mathml2.xsd",
            "identifier": "assessmenttest_manifest"})

        self.resourcen_block(test_struktur.list)
        self.file_path = write_xml_document(self.root, "imsmanifest.xml", temp_dir)

    def resourcen_block(self, test_struktur):
        resources = ET.SubElement(self.root, "resources")

        resource_assessmenttest = ET.SubElement(resources, "resource",{"identifier": "id_assessmenttest","type": "imsqti_test_xmlv2p1","href": "assessmenttest.xml"})
        ET.SubElement(resource_assessmenttest, "file", {"href": "assessmenttest.xml"})
        for sektion_obj in test_struktur:
            for f in sektion_obj.images_used:
                    ET.SubElement(resource_assessmenttest, "file", {"href": "media/"+f.href})
            for aufgabe_obj in sektion_obj.list_tasks:
                for f in aufgabe_obj.images_used:
                    ET.SubElement(resource_assessmenttest, "file", {"href": "media/" + f.href})
                for vdi in aufgabe_obj.variant_dependent_images:
                    ET.SubElement(resource_assessmenttest, "file", {"href": "templates/"+aufgabe_obj.id+"/"+vdi.id+".xml"})
                ET.SubElement(resource_assessmenttest, "dependency", {"identifierref": "id_"+str(aufgabe_obj.id)})
                ET.SubElement(resource_assessmenttest, "file", {"href": "files/"+aufgabe_obj.id+"/redtick-display-none.css"})

        # Separate Resource für Editor-Daten + Abhängigkeit vom Test
        resource_editordata = ET.SubElement(resources, "resource", {
            "identifier": "id_editordata",
            "type": "webcontent",
            "href": "files/assessmenttest/editordata.json"
        })
        ET.SubElement(resource_editordata, "file", {"href": "files/assessmenttest/editordata.json"})
        ET.SubElement(resource_assessmenttest, "file", {"href": "files/assessmenttest/editordata.json"})

        for sektion_obj in test_struktur:
            for aufgabe_obj in sektion_obj.list_tasks:
                resource_aufgabe = ET.SubElement(resources, "resource",{"identifier": "id_"+str(aufgabe_obj.id),"type": "imsqti_item_xmlv2p1","href": str(aufgabe_obj.id)+".xml"})
                ET.SubElement(resource_aufgabe, "file", {"href": str(aufgabe_obj.id)+".xml"})
