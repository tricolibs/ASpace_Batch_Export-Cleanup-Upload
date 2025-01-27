import os
import re
import time

from as_xtf_GUI import logger
from pathlib import Path
from lxml import etree

extent_regex = re.compile(r"(^\W)")
unitdate_regex = re.compile(r"\bunitdate\b")
barcode_regex = re.compile(r"\[(.*?)\]")
atid_regex = re.compile(r"Archivists Toolkit Database")
archon_regex = re.compile(r"Archon Instance")
dao_regex = re.compile(r"(\bdao\b)")


@logger.catch
class EADRecord:
    """
    Modify an EAD.xml file for web display and EAD2002 compliance.
    """
    cert_attrib = ["circa", "ca.", "c", "approximately", "probably", "c.", "between", "after"]
    extent_chars = ["(", ")", "[", "]", "{", "}"]

    def __init__(self, file_root):
        """
        Must contain file root as generated by lxml module.

        Args:
            file_root (lxml.Element object): an lxml.element root to be edited by different methods in the class
        """
        self.root = file_root
        """(lxml.Element object): an lxml.element root to be edited by different methods in the class"""
        self.results = ""
        """str: filled with result information when methods are performed"""
        self.eadid = file_root[0][0].text
        """str: contains the EADID for a record"""
        self.daos = False
        """bool: determines whether there are digital objects in a record"""

    def add_eadid(self):
        """
        Takes the resource identifier as listed in ArchivesSpace and copies it to the element in the EAD.xml file.
        Returns:
            None
        """
        if self.eadid is None:
            for child in self.root[1][0]:
                if "unitid" in str(child.tag):
                    if "type" in child.attrib:
                        if "Archivists Toolkit Database::RESOURCE" != child.attrib["type"]:
                            self.eadid = child.text
                            self.root[0][0].text = self.eadid
                    else:
                        self.eadid = child.text
                        self.root[0][0].text = self.eadid
            print(f"Added {str(self.eadid)} as eadid")
            # self.results += "Added " + str(self.eadid) + " as eadid\n"

    def delete_empty_notes(self):
        """
        Searches for every <p> element and checks if there is content in the element. If not, it is deleted.

        Returns:
            None
        """
        count1_notes = 0
        count2_notes = 0
        for child in self.root.findall(".//*"):
            if child.tag == '{urn:isbn:1-931666-22-9}p':  # {urn:isbn:1-931666-22-9}p dependency on using urn:isbn:
                count1_notes += 1
                if child.text is None and list(child) is None:
                    parent = child.getparent()
                    parent.remove(child)
                    count2_notes += 1
        print(f"Found {str(count1_notes)} <p>'s in {str(self.eadid)} and removed {str(count2_notes)} empty notes")
        # self.results += "We found " + str(count1_notes) + " <p>'s in " + str(self.eadid) + " and removed " + str(
        #     count2_notes) + " empty notes\n"

    def edit_extents(self):
        """
        Deletes empty <extent> elements and removes brackets, braces, and parentheses if they begin with them.

        Returns:
            None
        """
        count_ext1 = 0
        count_ext2 = 0
        count_ext3 = 0
        for child in self.root.iter():
            if "extent" in child.tag:
                count_ext1 += 1
                if child.text is not None:  # got "NoneType" object for RBRL/044/CFH
                    extent_content = child.text.strip()
                    match = extent_regex.match(child.text)
                    if match:  # Converts this: "(8x10") NEGATIVE [negative missing] b/w"  to this: "8x10" NEGATIVE ...
                        for character in extent_content:
                            if character in EADRecord.extent_chars:
                                extent_content.replace(character, "")
                        count_ext3 += 1
                elif child.text is None:
                    parent = child.getparent()
                    try:
                        parent.remove(child)
                    except Exception as e:
                        print("Could not remove empty extent field, error:\n" + str(e) + "\n")
                        # self.results += ("Could not remove empty extent field, error:\n" + str(e) + "\n")
                    count_ext2 += 1
        print(f"Found {str(count_ext1)} <extent>'s in {str(self.eadid)} and removed {str(count_ext2)} empty extents "
              f"and corrected {str(count_ext3)} extent descriptions starting with (), [], or {{}}")
        # self.results += "We found " + str(count_ext1) + " <extent>'s in " + str(self.eadid) + " and removed " + str(
        #     count_ext2) + " empty extents and corrected " + str(
        #     count_ext3) + " extent descriptions starting with `(), [], or {}`\n"

    def add_certainty_attr(self):
        """
        Adds the attribute certainty="approximate" to all dates that include words in cert_attrib list.

        Returns:
            None
        """
        count_ud = 0
        count_appr = 0
        for child in self.root.findall(".//*"):
            if unitdate_regex.search(child.tag):
                count_ud += 1
                unitdate_text = child.text.split()
                for date in unitdate_text:
                    if date in EADRecord.cert_attrib:
                        child.set("certainty", "approximate")
                        count_appr += 1
        print(f"Found {str(count_ud)} unitdates in {str(self.eadid)} and set {str(count_appr)} certainty attributes")
        # self.results += "We found " + str(count_ud) + " unitdates in " + str(self.eadid) + " and set " + str(
        #     count_appr) + " certainty attributes\n"

    def add_label_attr(self):
        """
        Adds attribute label="Mixed Materials" to any container element that does not already have a label attribute.

        Returns:
            None
        """
        count_lb = 0
        count_cont = 0
        for child in self.root.iter():
            if "container" in child.tag:
                if "label" not in child.attrib:
                    child.attrib["label"] = "Mixed Materials"
                    count_lb += 1
                    count_cont += 1
                else:
                    count_cont += 1
        print(f"Found {str(count_cont)} containers in {str(self.eadid)} and set {str(count_lb)} label attributes")
        # self.results += "We found " + str(count_cont) + " containers in " + str(self.eadid) + " and set " + str(
        #     count_lb) + " label attributes\n"

    def strip_langmaterial(self):
        """
        Removes ending period from <langmaterial> element in EAD exports.
        Returns:
            None
        """
        for element in self.root.iter():
            if "langmaterial" in element.tag:
                parent_element = element
                child_count = 0
                for child_element in parent_element:
                    child_count += 1
                    if len(parent_element) == child_count:
                        try:
                            child_element.tail = None
                            print("Removed trailing period and whitespace from <langmaterial>")
                            # self.results += "We removed trailing period and whitespace from <langmaterial>\n"
                        except Exception as e:
                            print(f"There was an error removing trailing period and whitespace from langmaterial: {e}")
                            # self.results += f"There was an error removing trailing period and whitespace from " \
                            #                 f"langmaterial: {e}\n"

    def delete_empty_containers(self):
        """
        Searches an EAD.xml file for all container elements and deletes any that are empty.

        Returns:
            None
        """
        count1_notes = 0
        count2_notes = 0
        for child in self.root.iter():
            if "container" in child.tag:
                count1_notes += 1
                if child.text is None:
                    self.results += "Found empty container, deleting..."
                    parent = child.getparent()
                    parent.remove(child)
                    self.results += "Removed empty container\n"
                    count2_notes += 1
        print(f"Found {str(count1_notes)} <container>'s in {str(self.eadid)} and removed {str(count2_notes)} empty "
              f"containers")
        # self.results += "We found " + str(count1_notes) + " <container>'s in " + str(self.eadid) + " and removed " + \
        #                 str(count2_notes) + " empty containers\n"

    def update_barcode(self):
        """
        This adds a physloc element to an element when a container has a label attribute.

        It takes an appended barcode to the label and makes it the value of the physloc tag.

        Returns:
            None
        """
        count1_barcodes = 0
        count2_barcodes = 0
        for child in self.root.iter():
            if "container" in child.tag:
                attributes = child.attrib
                if 'label' in attributes:
                    count1_barcodes += 1
                    match = barcode_regex.search(attributes["label"])
                    if match:
                        count2_barcodes += 1
                        barcode = match.group(1)
                        # child.set("containerid", match.group(1)) -- set as attribute to container
                        parent = child.getparent()
                        barcode_tag = etree.SubElement(parent, "physloc", type="barcode")
                        barcode_tag.text = "{}".format(barcode)
        print(f"Found {str(count1_barcodes)} <container labels>'s in {str(self.eadid)} and added {str(count2_barcodes)}"
              f" barcodes in the physloc tag")
        # self.results += "We found " + str(count1_barcodes) + " <container labels>'s in " + str(self.eadid) + \
        #                 " and added " + str(count2_barcodes) + " barcodes in the physloc tag\n"

    def remove_at_leftovers(self):
        """
        Finds any unitid element with an Archivists Toolkit unique identifier. Deletes that element.

        Returns:
            None
        """
        count1_at = 0
        count2_at = 0
        for element in self.root.iter():
            if "unitid" in element.tag:
                attributes = element.attrib
                count1_at += 1
                if "type" in attributes:
                    match = atid_regex.match(attributes["type"])
                    if match:
                        count2_at += 1
                        parent = element.getparent()
                        parent.remove(element)
        print(f"Found {str(count1_at)} unitids in {str(self.eadid)} and removed {str(count2_at)} Archivists Toolkit "
              f"legacy ids")
        # self.results += "We found " + str(count1_at) + " unitids in " + str(self.eadid) + " and removed " + str(
        #     count2_at) + " Archivists Toolkit legacy ids\n"

    def remove_archon_ids(self):
        """
        Finds any unitid element with an Archon unique identifier. Deletes that element.

        Returns:
            None
        """
        count1_at = 0
        count2_at = 0
        for element in self.root.iter():
            if "unitid" in element.tag:
                attributes = element.attrib
                count1_at += 1
                if "type" in attributes:
                    match = archon_regex.match(attributes["type"])
                    if match:
                        count2_at += 1
                        parent = element.getparent()
                        parent.remove(element)
        print(f"Found {str(count1_at)} unitids in {str(self.eadid)} and removed {str(count2_at)} Archon legacy ids")
        # self.results += "We found " + str(count1_at) + " unitids in " + str(self.eadid) + " and removed " + str(
        #     count2_at) + " Archon legacy ids\n"

    def count_xlinks(self):
        """
        Counts every attribute that occurs in a <dao> element. Removes xlink: prefixes in all attributes.

        Returns:
            None
        """
        count1_xlink = 0
        count2_xlink = 0
        for element in self.root.iter():  # following counts xlink prefixes in EAD.xml file
            search = dao_regex.search(element.tag)
            if search:
                self.daos = True
                count1_xlink += 1
                attributes = element.attrib
                count2_xlink += len(attributes)
        print(f"Found {str(count1_xlink)} digital objects in {str(self.eadid)} and there are {str(count2_xlink)} xlink "
              f"prefaces in attributes")
        # self.results += "We found " + str(count1_xlink) + " digital objects in " + str(self.eadid) + " and there are "
        #                 + str(count2_xlink) + " xlink prefaces in attributes\n"
        ead_string = etree.tostring(self.root, encoding="unicode", pretty_print=True,
                                    doctype='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
        if "xlink" in ead_string:  # remove xlink prefixes if found in EAD.xml file
            del_xlink_attrib = ead_string.replace('xlink:', '')
            clean_xlinks = del_xlink_attrib.encode(encoding="UTF-8")
            self.root = etree.fromstring(clean_xlinks)

    def clean_unused_ns(self):
        """
        Removes any unused namespaces in the EAD.xml file.

        Returns:
            None
        """
        # objectify.deannotate(self.root, cleanup_namespaces=True) # doesn't work
        for element in self.root.getiterator():
            element.tag = etree.QName(element).localname
        etree.cleanup_namespaces(self.root)  # https://lxml.de/api/lxml.etree-module.html#cleanup_namespaces

    def clean_do_dec(self):
        """
        Replaces other namespaces not removed by clean_unused_ns() in the <ead> element with an empty <ead> element.

        Returns:
            None
        """
        ead_string = etree.tostring(self.root, encoding="unicode", pretty_print=True,
                                    doctype='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')  # encoding="unicode" allows non-byte string to be made
        if "xlink" in ead_string:
            del_xlink_attrib = ead_string.replace('xlink:', '')
            if del_xlink_attrib.find('audience="internal"', 0, 62) != -1:  # check if audience="internal" at beginning of <ead>
                xml_string = del_xlink_attrib.replace(
                    '<ead audience="internal" xmlns="urn:isbn:1-931666-22-9" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:isbn:1-931666-22-9 http://www.loc.gov/ead/ead.xsd">',
                    '<ead>')
            elif 'audience="internal"' in del_xlink_attrib:
                xml_string = del_xlink_attrib.replace(
                    '<ead xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" audience="internal" xsi:schemaLocation="urn:isbn:1-931666-22-9 http://www.loc.gov/ead/ead.xsd">',
                    '<ead>')
            else:
                xml_string = del_xlink_attrib.replace(
                    '<ead xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:isbn:1-931666-22-9 http://www.loc.gov/ead/ead.xsd">',
                    '<ead>')
        else:
            if 'audience="internal"' in ead_string:
                xml_string = ead_string.replace(
                    '<ead xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" audience="internal" xsi:schemaLocation="urn:isbn:1-931666-22-9 http://www.loc.gov/ead/ead.xsd">',
                    '<ead>')
            else:
                xml_string = ead_string.replace(
                    '<ead xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:isbn:1-931666-22-9 http://www.loc.gov/ead/ead.xsd">',
                    '<ead>')
        clean_xml = xml_string.encode(encoding="UTF-8")
        return clean_xml

    def clean_suite(self, ead, custom_clean):
        """
        Runs the above methods according to what the user specified in the custom_clean parameter.

        Args:
            ead (EADRecord instance): instance of the class EADRecord
            custom_clean (list): keys used to determine what cleanup methods to run

        Returns:
            clean_xml (bytes): if no cleanup is specified in custom_clean, bytes object with added doctype
            cleaned_root (bytes): if cleanup is specified in custom_clean, bytes object with added doctype
            self.results (str): filled with result information when methods are performed
        """
        cleaned_root = None
        if custom_clean:
            if "_ADD_EADID_" in custom_clean:
                ead.add_eadid()
            if "_DEL_NOTES_" in custom_clean:
                ead.delete_empty_notes()
            if "_CLN_EXTENTS_" in custom_clean:
                ead.edit_extents()
            if "_ADD_CERTAIN_" in custom_clean:
                ead.add_certainty_attr()
            if "_ADD_LABEL_" in custom_clean:
                ead.add_label_attr()
            if "_DEL_LANGTRAIL_" in custom_clean:
                ead.strip_langmaterial()
            if "_DEL_CONTAIN_" in custom_clean:
                ead.delete_empty_containers()
            if "_ADD_PHYSLOC_" in custom_clean:
                ead.update_barcode()
            if "_DEL_ATIDS_" in custom_clean:
                ead.remove_at_leftovers()
            if "_DEL_ARCHIDS_" in custom_clean:
                ead.remove_archon_ids()
            if "_CNT_XLINKS_" in custom_clean:
                ead.count_xlinks()
            if "_DEL_NMSPCS_" in custom_clean:
                ead.clean_unused_ns()
            if "_DEL_ALLNS_" in custom_clean:
                cleaned_root = ead.clean_do_dec()
            if cleaned_root is None:
                ead_string = etree.tostring(self.root, encoding="unicode", pretty_print=True,
                                            doctype='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
                clean_xml = ead_string.encode(encoding="UTF-8")
                return clean_xml, self.results
            else:
                return cleaned_root, self.results
        else:
            ead_string = etree.tostring(self.root, encoding="unicode", pretty_print=True,
                                        doctype='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
            clean_xml = ead_string.encode(encoding="UTF-8")
            return clean_xml, self.results


# cycle through EAD files in source directory
@logger.catch
def cleanup_eads(filepath, custom_clean, output_dir="clean_eads", keep_raw_exports=False):
    """
    Take an EAD.xml file, parse it, clean it, and write it to output folder/directory.

    To learn more about the lxml package, see the documentation: https://lxml.de/

    For an in-depth review on how this code is structured, see the wiki:
    https://github.com/uga-libraries/ASpace_Batch_Export-Cleanup-Upload/wiki/Code-Structure#cleanup_eads

    Args:
        filepath (str): filepath of the EAD record to be cleaned
        custom_clean (list): strings as passed from as_xtf_GUI.py that determines what methods will be run against the lxml element when running the clean_suite() method. The user can specify what they want cleaned in as_xtf_GUI.py, so this is how those specifications are passed.
        output_dir (str): filepath of where the EAD record should be sent after cleaning, as specified by the user ("clean_eads" is default)
        keep_raw_exports (bool): if a user in as_xtf_GUI.py specifies to keep the exports that come from as_export.py, this parameter will prevent the function from deleting those files in source_eads.

    Returns:
        (bool): if True, the XML was valid. If False, the XML was not valid.
        results (str): filled with result information when methods are performed
    """
    filename = Path(filepath).name  # get file name + extension
    fileparent = Path(filepath).parent
    valid_err = ""
    parser = etree.XMLParser(remove_blank_text=True, ns_clean=True)  # clean up redundant namespace declarations
    try:
        tree = etree.parse(filepath, parser=parser)
    except Exception as e:
        valid_err += "Error: {}\n\n" \
                     "File saved in: {}\n".format(e, Path(filepath).parent)
        valid_err += "-" * 139
        return False, valid_err
    ead_root = tree.getroot()
    ead = EADRecord(ead_root)
    clean_ead, results = ead.clean_suite(ead, custom_clean)
    results += "\n" + "-" * 139
    clean_ead_file_root = str(Path(output_dir, '{}'.format(filename)))
    with open(clean_ead_file_root, "wb") as CLEANED_EAD:
        CLEANED_EAD.write(clean_ead)
        CLEANED_EAD.close()
    for file in os.listdir(fileparent):
        source_filepath = str(Path(fileparent, file))
        if not os.path.isdir(source_filepath) and Path(source_filepath).suffix == ".xml":
            file_time = os.path.getmtime(source_filepath)
            current_time = time.time()
            delete_time = current_time - 5356800  # This is for 2 months.
            if file_time <= delete_time:  # If a file is more than 2 months old, delete
                os.remove(source_filepath)
    if keep_raw_exports is False:  # prevents program from rerunning cleanup on cleaned files
        os.remove(filepath)
        return True, results
    else:
        results += "\nKeeping raw ASpace exports in {}\n".format(fileparent)
        return True, results
