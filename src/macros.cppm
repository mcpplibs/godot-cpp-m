module;
#include <godot_cpp/core/version.hpp>
namespace mwrap_godot_cpp_capture {
inline constexpr auto value_GODOT_VERSION_MAJOR = GODOT_VERSION_MAJOR;
inline constexpr auto value_GODOT_VERSION_MINOR = GODOT_VERSION_MINOR;
inline constexpr auto value_GODOT_VERSION_PATCH = GODOT_VERSION_PATCH;
inline constexpr auto value_GODOT_VERSION_STATUS = GODOT_VERSION_STATUS;
}
#undef GODOT_VERSION_MAJOR
#undef GODOT_VERSION_MINOR
#undef GODOT_VERSION_PATCH
#undef GODOT_VERSION_STATUS

export module mcpplibs.mwrap.godot_cpp.macros;

export namespace mcpplibs::mwrap::godot_cpp::macros {
inline constexpr auto GODOT_VERSION_MAJOR = mwrap_godot_cpp_capture::value_GODOT_VERSION_MAJOR;
inline constexpr auto GODOT_VERSION_MINOR = mwrap_godot_cpp_capture::value_GODOT_VERSION_MINOR;
inline constexpr auto GODOT_VERSION_PATCH = mwrap_godot_cpp_capture::value_GODOT_VERSION_PATCH;
inline constexpr auto GODOT_VERSION_STATUS = mwrap_godot_cpp_capture::value_GODOT_VERSION_STATUS;

}
