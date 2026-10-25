# godot-cpp-m

> godot-cpp as a C++23 module for mcpp — the same API, reached with `import mcpplibs.mwrap.godot_cpp;`.
>
> Targets **Godot 4.7** (`compat.godot-cpp` 10.0.0). Other engine API profiles require a matching generated provider.

```cpp
import std;
import mcpplibs.mwrap.godot_cpp;

int main() {
    godot::Vector2 v{3, 4};
    std::println("{}", v.length());   // 5 — the same godot-cpp you already know, no #include
}
```

- **Nothing forked, nothing reimplemented.** Upstream's sources and its
  pre-generated GDExtension bindings arrive through the
  [`compat.godot-cpp`](https://github.com/mcpplibs/mcpp-index) index package,
  which compiles all 1022 translation units directly — no SCons, no CMake, and
  no Python anywhere in the build. This repository is only the module layer.
- **The whole `godot` namespace is re-exported**, generated from the headers
  rather than curated by hand: ~1750 names, every engine class, every builtin
  Variant type, the global enums *and their enumerators* (so `godot::OK` and
  `godot::ERR_FILE_NOT_FOUND` still spell the same), `godot::Math`, the
  templates.
- **Macros keep working too**, through an optional side header — see below.

## Install

```toml
[dependencies]
"mcpplibs.mwrap.godot_cpp" = "10.0.0"   # Upstream-default Godot 4.7 API
```

The version tracks upstream godot-cpp. A numeric wrapper revision may follow
the upstream version: candidate `10.0.0` still uses SDK `10.0.0`.
The historical upstream mapping is:

| package version | upstream tag | engine |
|---|---|---|
| `10.0.0` | `10.0.0-stable` | Godot 4.7 (upstream-default API) |

## Macros

C++ named modules cannot export macros, and GDExtension code is written in
them: `GDCLASS`, `GDREGISTER_CLASS`, `GDVIRTUAL_*`, `D_METHOD`,
`memnew`/`memdelete`, the `ERR_*` family. A translation unit that registers
classes includes the side header next to the import:

```cpp
#include <godot-cpp-m/macros.h>
import mcpplibs.mwrap.godot_cpp;

using namespace godot;

class Player : public Node2D {
    GDCLASS(Player, Node2D)
protected:
    static void _bind_methods() {
        ClassDB::bind_method(D_METHOD("get_speed"), &Player::get_speed);
    }
public:
    void _process(double delta) override { /* ... */ }
    double get_speed() const { return speed; }
private:
    double speed = 1.0;
};
```

The headers it pulls in denote the same global-module entities the module
re-exports (they sit in the module's global module fragment), so mixing the
include and the import this way is well-formed. `tests/godot_cpp_macros.cpp`
covers exactly this shape. Any other upstream header can be included the same
way — they are all on the include path.

## Hash function ownership

Upstream `10.0.0-stable` defines the float/double hash functions out of line.
The wrapper uses those original definitions and no longer shadows hashfuncs.hpp.
The generator retains support for reproducing legacy releases that required the
small linkage shim; it removes that obsolete shim for the stable source layout.

## Example

`examples/summator/` is a complete GDExtension — registered class, bound
methods, entry point — built as the shared library Godot loads, written with
`import mcpplibs.mwrap.godot_cpp;`:

```sh
cd examples/summator && mcpp build
# then drop the library + summator.gdextension into a matching Godot 4.7 project
```

## Regenerating the module

`src/godot_cpp.cppm` is generated, not hand-written. After a `compat.godot-cpp`
version bump:

```sh
python3 tools/gen_module_cppm.py --shim-out include/godot_cpp/templates/hashfuncs.hpp \
  <godot-cpp-checkout-with-gen/> > src/godot_cpp.cppm
mcpp test
```

The checkout has to be one that has already run upstream's
`binding_generator.py` — which is exactly what the `compat.godot-cpp` archive
contains, so unpacking that is the simplest source.

## Tests

```sh
mcpp test
```

- `tests/godot_cpp_module.cpp` — the module surface: Variant math whose
  definitions live in the library's `.cpp` files (so it can only pass if the
  library really linked), plus generated engine classes and global enums.
- `tests/godot_cpp_macros.cpp` — the macro surface: a `GDCLASS` subclass with a
  bound method and an overridden engine virtual, next to the import.

Neither runs engine code: anything routed through the `gdextension_interface_*`
function pointers needs a Godot process that has loaded the extension.

## License

MIT for the module layer. Upstream godot-cpp is MIT as well.
