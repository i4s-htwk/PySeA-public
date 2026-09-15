from .TaskFacade import TaskFacade
from .SectionFacade import SectionFacade
from backend.stores import TestStore, StoreConfigurations, StoreImages, StoreVariants


class TestFacade:
    """Provides an interface for creating and managing a test.

    The class encapsulates access to the underlying stores and offers methods
    for editing the test structure, global settings, and images. This allows
    the calling code to work without directly interacting with the internal
    data structures of ``TestStore``.
    """

    def __init__(self, title=None):
        self.test_store = TestStore()
        if title: self.test_store.store_configurations.title = title

    def get_settings(self) -> StoreConfigurations:
        """Return the current test settings.
        Returns:
            A ``StoreConfiguration`` object that can be used to configure the test.
        """
        return self.test_store.store_configurations

    def add_section(self, title=None) -> SectionFacade:
        """Create a new section in the test.
        Args:
            title: Optional title of the section.
        Returns:
            A ``SectionFacade`` object that can be used as an interface for
            editing the newly created section.
        """
        section = self.test_store.test_structure.add_section(title)
        self.test_store.store_item_body.add_item(section.id)
        self.test_store.store_tables.add_item(section.id)
        return SectionFacade(self.test_store, section.id)

    def delete_object(self, object_id):
        """Delete an object from the test structure and all related stores.

        The object can be either a section or a task. When deleting a task,
        the method only removes it if the containing section still has more
        than one task.
        Args:
            object_id: The ID of the object to delete.
        """
        id_map = {}
        current_obj_ts = self.test_store.test_structure.get_object(object_id)
        if "section" in object_id:
            id_map = self.test_store.test_structure.delete_section(current_obj_ts)
        elif "task" in object_id and len(self.test_store.test_structure.list[current_obj_ts.section_nr - 1].list_tasks) > 1:
            id_map = self.test_store.test_structure.list[current_obj_ts.section_nr - 1].delete_task(current_obj_ts)
        self.test_store.store_item_body.delete_item(id_map)
        self.test_store.store_responses.delete_item(id_map)
        self.test_store.store_tables.delete_item(id_map)
        self.test_store.store_feedback.delete_item(id_map)
        self.test_store.store_selections.delete_item(id_map)

    def load_images(self, path) -> StoreImages:
        """Load images from the given path.
        Args:
            path: Path to the image source or directory.
        Returns:
            A ``StoreImages`` object that stores all images and can be used for editing the images.
        """
        return self.test_store.store_images.load_images(path)

    def create_test(self, path):
        """Create and save the test at the given path.

        At the given path, a ZIP file containing the created test and a JSON file that can be used to reload the test are created.
        Args:
            path: Target path where the test should be created.
        """
        self.test_store.create_test(path)

    @staticmethod
    def load_test(path_file) -> "TestFacade":
        """Load a test from a JSON file and return a matching test.
        Args:
            path_file: Path to the JSON file.
        Returns:
            A ``TestFacade`` instance whose ``test_store`` was loaded from the file.
        """
        test_store_f = TestFacade()
        test_store = TestStore.load_test(path_file)
        test_store_f.test_store = test_store
        return test_store_f

    def variants(self, assignment_type) -> StoreVariants:
        """Enable the use of variants for the test.
        Returns:
            A ``StoreVariants`` object that can be used to edit the assignment of variants.
        """
        self.test_store.store_variants.use_variants = True
        self.test_store.store_variants.set_assignment(assignment_type)
        return self.test_store.store_variants