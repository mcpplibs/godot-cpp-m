// The macro half of the contract: a real GDExtension class declaration --
// GDCLASS, a bound method, an overridden engine virtual -- written next to
// `import godot_cpp;`, with only the side header included.
//
// This is the case a named module cannot cover on its own, so it gets its own
// test: it proves that textually including godot-cpp's headers alongside the
// import is well-formed (they denote the same global-module entities the
// module re-exports), that the GDCLASS machinery instantiates, and that
// everything it emits resolves at link time.
//
// Nothing here RUNS engine code. Instantiating a Wrapped subclass, or calling
// get_class_static() (which builds a StringName), goes through the
// gdextension_interface_* function pointers, and those are null outside a
// Godot process that has loaded the extension. So the class is exercised
// statically: type relationships, and taking the address of the members
// GDCLASS generates -- which still forces them to be emitted and linked.

#include <godot-cpp-m/macros.h>

import std;
import godot_cpp;

using namespace godot;

class TestSprite : public Node2D {
    GDCLASS(TestSprite, Node2D)

protected:
    static void _bind_methods() {
        ClassDB::bind_method(D_METHOD("get_speed"), &TestSprite::get_speed);
        ClassDB::bind_method(D_METHOD("set_speed", "speed"), &TestSprite::set_speed);
    }

public:
    void _process(double delta) override { position_x += speed * delta; }

    double get_speed() const { return speed; }
    void set_speed(double p_speed) { speed = p_speed; }

private:
    double speed = 1.0;
    double position_x = 0.0;
};

int main() {
    // GDCLASS produced a real Node2D subclass with its own state
    const bool hierarchy_ok = std::is_base_of_v<Node2D, TestSprite> &&
                              std::is_base_of_v<Node, TestSprite> &&
                              std::is_base_of_v<Object, TestSprite> &&
                              sizeof(TestSprite) > sizeof(Node2D) &&
                              std::is_same_v<TestSprite::self_type, TestSprite> &&
                              std::is_same_v<TestSprite::parent_type, Node2D>;

    // ODR-use the plumbing GDCLASS generates without calling it: if any of it
    // failed to instantiate or to link, this would not build
    const StringName &(*class_name_fn)() = &TestSprite::get_class_static;
    const StringName &(*parent_name_fn)() = &TestSprite::get_parent_class_static;
    void (*init_fn)() = &TestSprite::initialize_class;
    const bool plumbing_ok = class_name_fn != nullptr && parent_name_fn != nullptr &&
                             init_fn != nullptr;

    // the virtual override really overrides, and the bound accessors are usable
    // as member pointers (which is how ClassDB::bind_method takes them)
    const auto process_ptr = &TestSprite::_process;
    const auto getter = &TestSprite::get_speed;
    const bool members_ok = process_ptr != nullptr && getter != nullptr &&
                            std::is_same_v<decltype(getter), double (TestSprite::*const)() const>;

    // helpers the side header brings along
    const bool helper_ok = MAX(3, 7) == 7 && MIN(3, 7) == 3 && CLAMP(9, 0, 5) == 5;

    const bool ok = hierarchy_ok && plumbing_ok && members_ok && helper_ok;
    std::println("hierarchy={} plumbing={} members={} helper={}",
                 hierarchy_ok, plumbing_ok, members_ok, helper_ok);
    return ok ? 0 : 1;
}
