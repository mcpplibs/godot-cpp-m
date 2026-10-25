import unittest
from gen_module_cppm import Scanner


class StableDeclarations(unittest.TestCase):
    def test_warning_wrappers_and_record_attributes_preserve_real_names(self):
        scanner = Scanner()
        scanner.scan('''namespace godot {
GODOT_GCC_WARNING_PUSH
GODOT_GCC_WARNING_IGNORE("-Wclass-memaccess")
template <class T> class _WARN_UNUSED_ HashSet { T value; };
GODOT_GCC_WARNING_POP
class _WARN_UNUSED_ List {};
GODOT_PUSH_IGNORE_DEPRECATION()
void normal_function();
GODOT_POP_IGNORE_DEPRECATION()
}''')
        names = scanner.exported("godot")
        self.assertEqual(set(names), {"HashSet", "List", "normal_function"})
        self.assertNotIn("_WARN_UNUSED_", names)
        self.assertNotIn("GODOT_GCC_WARNING_IGNORE", names)


if __name__ == "__main__":
    unittest.main()
