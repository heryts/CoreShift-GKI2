<!-- SPDX-License-Identifier: MPL-2.0 -->

# CoreShift-GKI2

CoreShift-GKI2 is a GitHub Actions-based Android GKI kernel builder, forked and extended from [CoreShift-GKI](https://github.com/CoreShiftD/CoreShift-GKI) with a much wider set of root manager integrations (KernelSU forks, MidoriSU hook variants, SUSFS4KSU) and additional zram compressor/backend support.

It helps you build flashable custom GKI kernels without setting up a full Android kernel build environment locally. You choose a kernel family, root manager, and optional features in GitHub Actions, then download the generated output.

> Custom kernels can bootloop your device. Use this only if you know how to recover with recovery or fastboot.

## What CoreShift-GKI2 Builds

CoreShift-GKI2 can build Android GKI kernels for supported Android kernel families and package them into flashable AnyKernel zip files.

It is designed for:

- Android power users
- Root users
- Custom ROM users
- Kernel testers
- Users who can recover from a bad kernel flash

It is not a universal compatibility layer. A build that boots on one device, ROM, or Android version may not boot on another.

## Supported Kernel Families

| Android GKI family | Kernel version |
| --- | --- |
| Android 12 GKI | `5.10` |
| Android 14 GKI | `6.1` |
| Android 15 GKI | `6.6` |
| Android 16 GKI | `6.12` |

Your selected GKI version must match your device and ROM. `6.12` is newer and less battle-tested than `5.10`/`6.1`/`6.6` — expect rougher edges around some optional features.

## Supported Root Manager Choices

| Choice | Meaning |
| --- | --- |
| `Vanilla` | No root manager |
| `KernelSU` | Official KernelSU |
| `KernelSU-Backslashxx` | backslashxx/KernelSU fork |
| `KernelSU-Next` | KernelSU-Next (official upstream) |
| `KSUN-Susfs-Hookless` | KernelSU-Next hookless-SUSFS fork (MirahSyakilla) |
| `KowSU` | KowSU |
| `ResukiSU` | ReSukiSU |
| `MidoriSU-BranchLink` | MidoriSU Manager, branch-link hijacking hook mode |
| `MidoriSU-Syscall-Table-Tamper` | MidoriSU Manager, syscall-table tampering hook mode |
| `MidoriSU-XX-Manual-Deinlined` | MidoriSU Manager, manual hook mode, de-inlined SUSFS |
| `MidoriSU-Deinlined` | MidoriSU Manager, de-inlined SUSFS (staged/prerequisite patch chain) |
| `MidoriSU-KOW-Deinlined` | MidoriSU Manager on KowSU, de-inlined SUSFS |
| `MidoriSU-Next-Deinlined` | MidoriSU Manager on KernelSU-Next, de-inlined SUSFS |
| `MidoriSU-Resuki-Deinlined` | MidoriSU Manager on ReSukiSU, de-inlined SUSFS |

For your first root build, choose one manager and keep advanced features off. Confirm the kernel boots before enabling SUSFS or other extra features.

## Build Workflows

| Workflow | Purpose | Notes |
| --- | --- | --- |
| **Build Kernel** | Build one manual kernel with stable defaults. | Single-build flow. Choose Google LTS, maintained, Pixel, or custom source with `source_mode`. Good first choice. |
| **Custom Kernel Build** | Build one kernel with advanced manual feature options. | Single-build flow. Choose Google LTS, maintained, Pixel, or custom source with `source_mode`. |
| **Build Kernel Release Matrix** | Build the curated stable release set. | Recommended release path. Uses Google/AOSP LTS sources. |
| **Build Experimental Kernel Release Matrix** | Build curated maintained-source/custom experimental release sets. | Experimental path. Uses maintained GitHub `kernel/common` defaults and may break build, Wi-Fi, modules, root, KMI/KCFI, or boot. |
| **Build Pixel Kernel Release Matrix** | Build curated official Pixel-source prerelease sets. | Pixel-specific experimental path. UI asks only for Pixel branch; validated variants come from `.github/matrix/release_pixel.json`. |

Most users should start with **Build Kernel**. Use **Custom Kernel Build** only when you need extra control. Use the experimental release matrix only for maintained/custom release testing. Use the Pixel matrix workflow for official Pixel source testing.

## Quick Start

1. Fork this repository.
2. Open the **Actions** tab in your fork.
3. Choose a workflow.
4. Select your kernel version, manager, and options.
5. Run the workflow.
6. Download the generated AnyKernel zip or artifact.
7. Flash only after confirming you selected the correct GKI version for your device.

## Recommended Starting Points

| Goal | Recommended settings |
| --- | --- |
| First test build | `Vanilla`, thin LTO, advanced options off |
| First root build | One root manager, SUSFS off, BBG off |
| SUSFS build | Confirm the same manager boots first, then enable SUSFS |
| BBG build | Confirm the non-BBG build boots first, then enable BBG |
| Debug build | Enable debug features only when troubleshooting |

Start small. Boot a basic build first, then add one advanced feature at a time.

## Option Guide

| Option | Meaning |
| --- | --- |
| `kernel_version` | Target Android GKI family: `5.10`, `6.1`, or `6.6`. |
| `manager` | Root manager integration. Use `Vanilla` for no root manager. |
| `manager_ref` | Optional manager git ref, commit, or tag for advanced testing. |
| `source_mode` | Manual Build/Custom source choice. `google-lts` keeps the synced Google/AOSP LTS source; `maintained` uses the same maintained source mapping as the experimental release workflow; `pixel` uses an official Google Pixel kernel manifest branch; `custom` uses `source_repo`. |
| `pixel_branch` | Official Pixel kernel manifest branch used only when `source_mode=pixel`. Pixel mode is experimental and Pixel 6+ specific. |
| `source_repo` | Custom replacement Git repository for `kernel/common`, used only when `source_mode=custom`. |
| `source_ref` | Optional branch, tag, or commit for maintained/custom source replacement. Not guaranteed stable. |
| `kmi_bypass` | Experimental maintained/custom source workaround. Defaults to `off`; when set to `on`, bypasses strict Kleaf KMI symbol-list checks for incompatible replacement sources only. |
| `lto` | Link-time optimization. `thin` is the safest default. |
| `susfs` | SUSFS4KSU support. Advanced root-hiding/spoofing feature. Compatibility depends on the selected manager and the exact `kernel/common` source tree. |
| `baseband_guard` | Baseband Guard support. Advanced protection feature. |
| `container_features` | Enables container-related kernel options in custom builds. |
| `performance_features` | Enables performance-oriented options. Use only when needed. |
| `debug_features` | Enables debugging/tracing options. Not needed for normal use. |
| `strict_config` | Fails the build if required config options are missing. |
| `legacy_kmi_check` | Controls the legacy 5.10 KMI check behavior. |
| `publish_mode` | Chooses release output, artifact output, or both. |

Some workflows intentionally hide low-level fragment toggles to keep normal builds simpler and safer. Stable release matrix builds stay fixed and curated on Google/AOSP LTS sources. Experimental release matrix builds use maintained default source repos and optional source override.

### Release Matrix Files

- Stable release matrix workflow reads `.github/matrix/release.json`.
- Experimental release matrix workflow reads `.github/matrix/release_exp.json` for maintained/custom profiles.
- Pixel release matrix workflow reads `.github/matrix/release_pixel.json`.
- `.github/matrix/release.json` contains only curated Google/AOSP-supported stable release variants.
- `.github/matrix/release_exp.json` contains curated maintained-source experimental variants.
- `.github/matrix/release_pixel.json` contains curated official Pixel-manifest experimental variants.

### Source Modes

Manual **Build Kernel** and **Custom Kernel Build** are single-build flows, not matrices. They support these source modes:

- `google-lts`: keep the Google/AOSP LTS source synced by the Android kernel manifest. No `kernel/common` replacement is performed, and expected-Clang materialization is skipped.
- `maintained`: replace `kernel/common` with the maintained source repo for the selected kernel family, using the same mapping as the experimental release workflow. Expected-Clang materialization runs after replacement.
- `pixel`: sync an official Google Pixel kernel manifest branch selected by `pixel_branch`. No maintained GitHub source replacement is performed. This mode is experimental, Pixel 6+ only, and not generic GKI LTS.
- `custom`: replace `kernel/common` with `source_repo` and optional `source_ref`. `source_repo` is required. Expected-Clang materialization runs after replacement.

Maintained, Pixel, and custom source modes are experimental. They can fail build, KMI, KCFI, module loading, Wi-Fi, root manager integration, or boot even when the Google LTS source path works. Pixel source builds may require Pixel-specific modules, images, and targets, and are not guaranteed to work on non-Pixel devices.

Google LTS, maintained, custom, stable release, and experimental release builds keep strict KMI symbol-list checking enabled by default. The `kmi_bypass` input is an explicit experimental workaround for testing incompatible maintained/custom replacement sources; it is off by default and is ignored for Google LTS. Enabling it can break vendor modules, Wi-Fi, modem, display, touch, audio, or boot, so use it only while testing source trees that cannot currently satisfy Google's symbol list.

### Maintained Source Defaults

The manual `source_mode=maintained` flow and the experimental release workflow use these maintained `kernel/common` repos by default:

- `5.10`: `https://github.com/ramabondanp/android_kernel_common-5.10`
- `6.1`: `https://github.com/ramabondanp/android_kernel_common-6.1`
- `6.6`: `https://github.com/ramabondanp/android_kernel_common-6.6`

These are experimental defaults, not stable release defaults.

### Pixel Source Defaults

The manual `source_mode=pixel` flow and the experimental `source_profile=pixel` matrix use official Google Pixel kernel manifest branches:

- `android14-gs-pixel-6.1`
- `android-gs-raviole-6.1-android16`
- `android-gs-bluejay-6.1-android16`
- `android-gs-akita-6.1-android16`

Pixel source mode is experimental, Pixel 6+ specific, and not generic GKI LTS. It may need Pixel-specific modules or images and can fail on non-Pixel devices. If a Pixel branch does not expose `//common:kernel_aarch64_dist`, the build reports that target mismatch instead of pretending the generic GKI target is valid.

Pixel validation status:

- `android14-gs-pixel-6.1`: release matrix includes validated Vanilla,
  `KernelSU`, `KowSU`, SUSFS, BBG, and SUSFS+BBG combinations.
- `android-gs-raviole-6.1-android16`: manager and BBG variants are validated on
  the manifest source path `aosp`, but SUSFS variants are omitted because the
  core SUSFS patch does not apply cleanly. The workflow maps this branch to
  `KERNEL_COMMON_DIR=kernel/aosp` and `KLEAF_DIST_TARGET=//aosp:kernel_aarch64_dist`.
- `android-gs-bluejay-6.1-android16`: same source-root and target handling as
  Raviole Android 16, with validated manager and BBG variants. SUSFS variants
  are omitted because the core SUSFS patch does not apply cleanly.
- `android-gs-akita-6.1-android16`: source sync failed for the manifest-mapped
  `aosp` and `build/kernel` refs during validation, so it is not in the Pixel
  release matrix.

Unsupported Pixel SUSFS variants are intentionally omitted from
`.github/matrix/release_pixel.json`; the workflow does not dynamically generate
unvalidated combinations.

Pixel variants are expanded because each release artifact represents one
validated feature combination. This avoids generating unsupported combinations
dynamically and makes each release asset explicit about manager, SUSFS, BBG,
source branch, and LTO state. `android14-gs-pixel-6.1` currently has 10
variants: Vanilla, KernelSU, KowSU, KernelSU+SUSFS, and KowSU+SUSFS, each with
BBG off/on. Android 16 Pixel branches currently have 6 variants each: Vanilla,
KernelSU, and KowSU, each with BBG off/on, with SUSFS omitted because the core
SUSFS patch does not apply.

Pixel branches may use source roots and Kleaf packages that differ from generic
GKI. The workflow discovers the manifest path for `kernel/common` and builds the
matching `kernel_aarch64_dist` target instead of forcing every Pixel branch
through `kernel/common` and `//common:kernel_aarch64_dist`.

### Source Policy

- Single-build manual workflows can choose Google LTS, maintained, Pixel, or custom source modes:
  - `Build Kernel`
  - `Custom Kernel Build`
- Stable release matrix uses Google/AOSP LTS sources from `.github/matrix/release.json`.
- Experimental release matrix uses maintained GitHub `kernel/common` defaults from `.github/matrix/release_exp.json`. Custom experimental release runs reuse the maintained matrix shape with explicit `source_repo` / `source_ref`.
- Pixel release matrix uses official Pixel manifests from `.github/matrix/release_pixel.json`; its UI exposes only the Pixel branch selector, and manager/SUSFS/BBG/LTO variants are fixed by the validated matrix.

### SUSFS Note

SUSFS support is validated per manager and per maintained source tree, not just per kernel version.

- `5.10`, `6.1`, and `6.6` are validated on the maintained experimental source path for both `KernelSU` and `KowSU`.
- `KernelSU` and `KowSU` manager compatibility is still patch-source dependent, so custom source overrides can fail even when the default source path works.
- Experimental source replacement and SUSFS together may still break build output, Wi-Fi, vendor modules, root, KMI/KCFI, or boot.

## Safety Checklist

Before flashing any build:

- Back up your current `boot`, `init_boot`, and `vendor_boot` images if your device uses them.
- Keep a known-good kernel, boot image, or ROM package ready.
- Know how to use recovery or fastboot.
- Confirm your device uses the selected GKI kernel family.
- Test a basic build before enabling SUSFS, BBG, container, performance, or debug features.
- Do not flash builds meant for a different Android/GKI family.

Flash at your own risk.

## Compatibility Notes

CoreShift-GKI builds Android GKI kernels, but compatibility still depends on your device, ROM, vendor modules, boot image layout, and Android version.

A kernel may fail to boot if:

- The selected GKI version does not match your ROM.
- Vendor modules are incompatible.
- The boot image layout differs from what the package expects.
- A root manager or advanced patch is incompatible with your kernel family.
- An experimental maintained-source or custom `kernel/common` tree diverges from the expected patch base.
- SUSFS or BBG changes conflict with your device or ROM.

When testing, change one thing at a time.

## Outputs

Custom builds can publish outputs in three modes:

| Mode | Output |
| --- | --- |
| `artifact` | Uploads build artifacts through GitHub Actions. |
| `release` | Creates a GitHub release. |
| `both` | Uploads artifacts and creates a release. |

Typical outputs include:

- Flashable AnyKernel zip
- Raw kernel `Image`
- Exported kernel config
- `compiler-version.txt`

Most users should flash the **AnyKernel zip**, not the raw `Image`.

### Compiler Metadata

Builds use the toolchain selected by the Android kernel source/build system. `compiler-version.txt` records the compiler visible after the build so users can compare it with `uname -a` or `/proc/version`.

After boot, compare it with:

- `uname -a`
- `cat /proc/version`

### Artifact Note

GitHub downloads artifacts as zip files. To avoid a zip-inside-zip problem, artifact mode may upload a staged AnyKernel tree instead of uploading an already zipped package.

## Troubleshooting

| Problem | What to try |
| --- | --- |
| Build failed | Re-run with fewer options. Start from `Vanilla` and thin LTO. |
| Device bootloops | Restore your boot images or flash a known-good kernel. |
| Full LTO build was killed | Use thin LTO. Full LTO needs more memory. |
| Experimental maintained-source build breaks boot or modules | Go back to the stable release matrix workflow or test a simpler maintained-source build first. |
| Root manager is not detected | Build the manager without SUSFS first, then test SUSFS separately. |
| SUSFS does not work | Confirm the same manager boots without SUSFS first. |
| BBG causes issues | Test the same build with BBG off, then compare logs. |
| Feature does not work | Rebuild with only that feature enabled. |
| Wrong kernel version | Rebuild with the GKI version used by your ROM/device. |

## Recovery Reminder

A successful build does not guarantee a successful boot. Keep recovery access ready before flashing.

## License

This project is licensed under the Mozilla Public License 2.0. See [LICENSE](LICENSE).
