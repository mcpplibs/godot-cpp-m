import mcpplibs.mwrap.godot_cpp.macros;
namespace macros = mcpplibs::mwrap::godot_cpp::macros;
int main() { static_assert(macros::GODOT_VERSION_MAJOR == 4); static_assert(macros::GODOT_VERSION_MINOR == 7); return 0; }
