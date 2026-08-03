// godot-cpp-m/macros.h -- optional side header for godot-cpp's preprocessor surface.
//
// C++ named modules cannot export MACROS. Everything with linkage comes from
// `import godot_cpp;`; the macro spellings that GDExtension code is written in
// -- GDCLASS, GDREGISTER_CLASS, GDVIRTUAL_*, D_METHOD, memnew/memdelete, the
// ERR_* family, VARIANT_ENUM_CAST -- are preprocessor constructs, so a
// translation unit that registers classes textually includes THIS header next
// to the import:
//
//     #include <godot-cpp-m/macros.h>
//     import godot_cpp;
//
//     class Player : public godot::Node2D {
//         GDCLASS(Player, Node2D)
//     protected:
//         static void _bind_methods() {}
//     public:
//         void _process(double delta) override { /* ... */ }
//     };
//
// The declarations these headers bring in denote the same global-module
// entities the module re-exports (godot-cpp's headers sit in the module's
// global module fragment), so mixing include and import this way is
// well-formed -- and is covered by this repo's tests.
//
// Any upstream header can be included directly the same way; they are all on
// the include path through the compat.godot-cpp dependency.
#ifndef GODOT_CPP_M_MACROS_H
#define GODOT_CPP_M_MACROS_H

#include <godot_cpp/classes/wrapped.hpp>      // GDCLASS / GDEXTENSION_CLASS, GDVIRTUAL_*
#include <godot_cpp/core/class_db.hpp>        // GDREGISTER_*, D_METHOD, ClassDB::bind_method
#include <godot_cpp/core/error_macros.hpp>    // ERR_FAIL_*, WARN_PRINT, CRASH_*
#include <godot_cpp/core/memory.hpp>          // memnew, memdelete, memalloc/memfree
#include <godot_cpp/core/binder_common.hpp>   // VARIANT_ENUM_CAST, VARIANT_BITFIELD_CAST
#include <godot_cpp/core/defs.hpp>            // _ALWAYS_INLINE_, _FORCE_INLINE_, CLAMP/MIN/MAX
#include <godot_cpp/godot.hpp>                // GDExtensionBinding, the entry-point plumbing

#endif // GODOT_CPP_M_MACROS_H
