# godot-cpp-m runnable template checkpoint

Latest main b19f8247338b564057d363878ef39ed16dc07c58 was cloned from the organization repository. Keep the existing godotengine.godot-cpp-m package and import godot_cpp API. Candidate 10.0.0-rc1.1 appends one wrapper revision to SDK 10.0.0-rc1 (Godot 4.6); the SDK is unchanged. No merge, tag or release is authorized here.

The default math template uses the full self.name dependency key and runs vector/cross-product/color checks without an engine. Existing engine objects and GDCLASS registration still need a Godot process loading the extension. The README has 42 lines and links details in docs/usage.md. The manifest explicitly names src/godot_cpp.cppm as its library entry, avoiding the current client's missing-interface packaging advisory. The summator extension now declares the matching Godot 4.6 minimum and native CI builds its shared-library shape on all three platforms; actual engine loading is not claimed.

The client pin and .xlings.json use mcpp 2026.10.24.1. Local LLVM 23.1.3 and GCC 16.1.0 strict module/macro suites both pass two binaries. Actual default mcpp new + strict build + run passes with both compilers, printing vector length 5 and cross product (0,0,1), with a real out-of-line color result checked. The explicit library-entry recheck passes. The Linux LLVM summator shared library strictly builds; engine loading and native Windows/macOS verification remain pending. The extension has no C++ module entry of its own and the client's associated advisory is not a missing wrapper interface.

All local heavy checks run serially under mwrap-tests.slice (16 logical CPUs, 32 GiB max on this 32-CPU/62-GiB host), taskset 0-15 and MCPP_JOBS=6. Resource-supervised checks stop their own process group below 6 GiB free disk or 20% available host memory. Completed task diagnostic directories were removed after checking active process references; source logs and immutable archives remain.

Before release readiness: native source/template CI must pass, and the exact immutable archive must be registered and consumed by index tests. No mcpp engine sources are changed.
