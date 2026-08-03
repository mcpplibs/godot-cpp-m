// Behavioral test for the `godot_cpp` module: the same godot-cpp API as
// always, reached with `import godot_cpp;` and no #include at all.
//
// The assertions mirror the compat.godot-cpp test on purpose -- if the module
// re-export changed behaviour, these are the numbers that would move.
// Everything here is pure math, so no running Godot process is needed;
// anything routed through the gdextension_interface_* pointers (String, Array,
// class registration) is out of scope for a standalone binary.

import std;
import godot_cpp;

namespace {

bool close(double a, double b) {
    return std::fabs(a - b) < 1e-5;
}

} // namespace

int main() {
    using namespace godot;

    // out-of-line definitions from compat.godot-cpp's src/variant/*.cpp
    const bool vec2_ok = close(Vector2(3, 4).length(), 5.0) &&
                         close(Vector2(3, 4).normalized().length(), 1.0);

    const Vector3 cross = Vector3(1, 0, 0).cross(Vector3(0, 1, 0));
    const bool vec3_ok = cross == Vector3(0, 0, 1) &&
                         close(Vector3(2, 3, 6).length(), 7.0);

    const bool basis_ok = close(Basis().orthonormalized().determinant(), 1.0);

    const bool color_ok = Color(1.0f, 0.0f, 0.0f, 1.0f).to_rgba32() == 0xff0000ffu;

    const AABB box(Vector3(0, 0, 0), Vector3(2, 3, 4));
    const AABB other(Vector3(1, 1, 1), Vector3(4, 4, 4));
    const bool aabb_ok = close(box.get_volume(), 24.0) &&
                         box.intersects(other) &&
                         close(box.intersection(other).get_volume(), 6.0);

    // generated engine bindings, reached through the module
    const bool gen_ok = sizeof(Node) > 0 &&
                        sizeof(Node2D) > 0 &&
                        Node::PROCESS_MODE_INHERIT == 0 &&
                        Node::PROCESS_MODE_DISABLED == 4 &&
                        godot::OK == 0 &&
                        godot::ERR_FILE_NOT_FOUND == 7 &&
                        godot::SIDE_LEFT == 0 &&
                        Variant::OBJECT != Variant::NIL;

    // templates and utilities the module also has to carry
    const bool tmpl_ok = Math::is_equal_approx(1.0f, 1.0f) &&
                         !Math::is_zero_approx(1.0f) &&
                         close(Math::lerp(0.0, 10.0, 0.25), 2.5);

    const bool ok = vec2_ok && vec3_ok && basis_ok && color_ok && aabb_ok &&
                    gen_ok && tmpl_ok;
    std::println("vec2={} vec3={} basis={} color={} aabb={} gen={} tmpl={}",
                 vec2_ok, vec3_ok, basis_ok, color_ok, aabb_ok, gen_ok, tmpl_ok);
    return ok ? 0 : 1;
}
