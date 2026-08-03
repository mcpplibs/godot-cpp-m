// A complete Godot 4.5 GDExtension -- registered class, bound methods,
// entry point -- written with `import godot_cpp;`.
//
// Compare with upstream's C++ version of the same example: the only
// difference is the first three lines. Everything below is ordinary
// godot-cpp.

#include <godot-cpp-m/macros.h>   // GDCLASS, GDREGISTER_CLASS, D_METHOD, the entry-point plumbing

import godot_cpp;

using namespace godot;

class Summator : public RefCounted {
    GDCLASS(Summator, RefCounted)

protected:
    static void _bind_methods() {
        ClassDB::bind_method(D_METHOD("add", "value"), &Summator::add);
        ClassDB::bind_method(D_METHOD("reset"), &Summator::reset);
        ClassDB::bind_method(D_METHOD("get_total"), &Summator::get_total);
    }

public:
    void add(double p_value) { total += p_value; }
    void reset() { total = 0.0; }
    double get_total() const { return total; }

private:
    double total = 0.0;
};

namespace {

void initialize_summator(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
        return;
    }
    GDREGISTER_CLASS(Summator);
}

void uninitialize_summator(ModuleInitializationLevel) {}

} // namespace

extern "C" GDExtensionBool GDE_EXPORT summator_library_init(
        GDExtensionInterfaceGetProcAddress p_get_proc_address,
        GDExtensionClassLibraryPtr p_library,
        GDExtensionInitialization *r_initialization) {
    GDExtensionBinding::InitObject init_obj(p_get_proc_address, p_library, r_initialization);

    init_obj.register_initializer(initialize_summator);
    init_obj.register_terminator(uninitialize_summator);
    init_obj.set_minimum_library_initialization_level(MODULE_INITIALIZATION_LEVEL_SCENE);

    return init_obj.init();
}
