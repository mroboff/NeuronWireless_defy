# Keyboard Curator fork of the Defy wireless firmware

This is [Keyboard Curator](https://github.com/mroboff/keyboard-curator)'s
fork of Dygma's `NeuronWireless_defy`, the firmware of the Neuron 2 in the
wireless Dygma Defy. It is Dygma's released firmware with additions the
stock firmware and Bazecor do not offer, configured from Keyboard Curator
over the same Focus protocol. GPL-3.0, as Dygma's.

| | |
|---|---|
| Base | Dygma `N2_Defy_v2.2.1` (`421a18fbce696fab718d600918813cc5e0d4cbb7`), the firmware shipped as Defy v2.2.1 |
| Branch | `curator`: the base, then the fork's commits on top |
| Libraries | [mroboff/NeuronWirelessLibs](https://github.com/mroboff/NeuronWirelessLibs) `curator`, which points at [mroboff/Kaleidoscope-Dygma](https://github.com/mroboff/Kaleidoscope-Dygma) `curator`, where the new plugins live |
| Version | `v2.2.1-curator.N`, as the keyboard reports it to `version` |
| Releases | tags `v2.2.1-curator.N`, built by GitHub Actions: `Wireless_neuron.hex`, Dygma's `keyscanner.bin`, `SHA256SUMS`, `manifest.json` |

## What the fork adds

**Chords (combos).** Several keys pressed together send another key.
Chords are stored in EEPROM and set over Focus; Bazecor has never offered
them. Plugin `ChordsDygma` in the Kaleidoscope fork.

**Per-key hold and tap timing.** Stock firmware keeps one hold timeout for
every dual-use key and one timing set for every superkey. A table in
EEPROM gives single keys their own values. Plugin `KeyTimingDygma`; Qukeys
and Superkey read the table.

Everything else is Dygma's code, unchanged, including the side (keyscanner)
firmware, which the fork does not build or touch.

## Building

Dygma's requirements: GNU make, `gcc-arm-none-eabi` 10.3, Python 3 with
the `intelhex` package, and Nordic's nRF5 SDK 17.1.0 unpacked into
`libraries/SDK/nRF5_SDK_17.1.0_ddde560`.

```sh
git clone --branch curator https://github.com/mroboff/NeuronWireless_defy
cd NeuronWireless_defy
git -c url.https://github.com/.insteadOf=git@github.com: submodule update --init --recursive
curl -sSLo sdk.zip https://nsscprodmedia.blob.core.windows.net/prod/software-and-other-downloads/sdks/nrf5/binaries/nrf5_sdk_17.1.0_ddde560.zip
echo "5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061  sdk.zip" | sha256sum -c -
mkdir -p libraries/SDK && unzip -q sdk.zip -d libraries/SDK && rm sdk.zip
```

On NixOS or with Nix, `shell.nix` provides the exact toolchain (GCC ARM
10.3.1 from nixpkgs 24.05, the last release carrying it):

```sh
nix-shell --run 'make -C build release -j8 SHELL=$(which bash) DEFY_FW_VERSION=v2.2.1-curator.dev'
```

On Debian or Ubuntu, `apt install gcc-arm-none-eabi python3-intelhex make`
and the same `make` line (`SHELL=/bin/bash` is already the Makefile's
default there). The `insteadOf` setting is needed because Dygma's nested
submodules name SSH URLs; the fork's own `.gitmodules` files use HTTPS.

The build writes `build/release/NeuronWireless_defy_final.hex`: the
application merged with Dygma's prebuilt `rf_host_device` image, the file
Dygma publishes as `Wireless_neuron.hex`. `DEFY_FW_VERSION` is what the
keyboard reports to `version`; CI sets it from the tag.

Two things differ from Dygma's README: the Makefile hard-codes
`SHELL = /bin/bash`, which does not exist on NixOS, so the shell is passed
on the command line; and the version is passed in rather than edited.

Checked on 2026-10-13: the stock `N2_Defy_v2.2.1` tag built this way is the
same size class as Dygma's published `Wireless_neuron.hex` (171,080 bytes
of image against 171,072, both from `0x27000`), with byte differences
throughout from the different build host. It has not been flashed to a
keyboard yet; the first flash of a stock build and of the fork is the
owner's hardware check, with Bazecor's firmware update as the way back.

## Flashing

### With Bazecor

Bazecor's firmware update accepts a custom firmware folder (the "Custom
firmware" option on the update screen). The folder must hold
`Wireless_neuron.hex` and `keyscanner.bin`; a release of this fork
carries both, the keyscanner image being Dygma's own from the base
release, unchanged. Bazecor then updates the Neuron and, if they differ,
the sides.

### What Bazecor does, for Keyboard Curator's own installer

Facts read from Bazecor's source (`src/api/flash`, GPL-3.0; nothing
copied), for the wireless Defy:

1. Over Focus, Bazecor sends `upgrade.start` (the Neuron releases all keys,
   resets the sides and checks them) and later `upgrade.neuron`, which
   calls the Neuron's `Runtime.rebootBootloader()`. `upgrade.neuron` is
   refused unless `upgrade.start` ran first.
2. The Neuron reappears as a USB serial device with product ID `0x0013`
   (the keyboard itself is `0x35ef:0x0012`), the nRF52833 bootloader. The
   Neuron's light pulses blue.
3. The bootloader speaks a text protocol at 115200 baud. Bazecor parses the
   Intel HEX file into data records with their extended segment and linear
   addresses, then:
   - `E<start>#` with the first record's address as eight hex digits
     erases from there to the end of the application area (Bazecor always
     uses this form, which also erases the Bluetooth pairings; the
     alternative `E<start>,<length>#` with `0x72000 - start` keeps them);
   - for each packet of up to 4096 bytes: `U<size>#`, then the raw bytes
     (Bazecor writes them in chunks of 200), then `W<address>,<size>#`,
     with every number as eight hex digits, waiting for the bootloader's
     answer after each command (an `A` byte);
   - `S#` starts the application. The bootloader also sends an information
     block of more than 40 bytes (device id, bootloader version, flash
     start, program space start, erase and write alignment, maximum data
     length) which Bazecor reads but does not act on.
4. After the Neuron restarts, Bazecor waits for the keyboard's serial port
   to return, then flashes each side through the Neuron with the
   `upgrade.keyscanner.*` commands, and ends with `upgrade.end`.

The fork's Neuron image replaces only the Neuron; the sides keep Dygma's
keyscanner firmware. If the Neuron is left in its bootloader by a failed
write, Bazecor's firmware update (or a second attempt) flashes it again:
the bootloader itself is never written.

### Wired Defy

The wired Defy's Neuron is an RP2040 (`Dygmalab/NeuronWired`), flashed as
a UF2 drive (`Wired_neuron.uf2` in Dygma's releases). The fork does not
build it. Its Focus commands are the same apart from the wireless ones
(`wireless.*`, `hardware.side_power`), so the chords and timing plugins
would port, but that is separate work.

## Focus commands the fork adds

Every value is a decimal number; lists are space-separated on one line.
`help` lists these commands only when the EEPROM has room for their
tables, which it has after everything stock firmware stores.

### `chords.map`

Get: the whole map. Set: the whole map. Each chord is

```
result layers timeout key1 key2 ... keyN 0
```

- `result`: the key code sent, in the same vocabulary as `keymap.custom`
  (a plain or modified key, a layer action, a macro `53852+n`, a
  superkey `53980+n`, ...).
- `layers`: a bitmask of the layers the chord works on, bit *n* for layer
  *n*; `0` means every layer.
- `timeout`: the chord's own timeout in milliseconds, or `0` for
  `chords.timeout`.
- keys: the keymap positions of the chord's keys plus one (`1` to `80` on
  the Defy, where `keymap.custom` has 80 values per layer), two to six of
  them, closed with a `0`.

The map ends with `0 0`, like `superkeys.map`; an erased map reads as
`0 0`. Room: `chords.memory` bytes (512), two per value; at most 32
chords are kept. A chord is matched against the top active layer at the
moment of the press.

### `chords.timeout`

Get or set the timeout used by chords whose own is `0`, in milliseconds.
Default 50.

### `chords.memory`

The map's room in bytes. Read-only.

### `timing.map`

Get or set the per-key timing table. Each entry is nine values:

```
key layer hold overlap minHold minPrior skHold skOverlap skTimeout
```

- `key`: the keymap position plus one.
- `layer`: `0` for every layer, otherwise the layer number plus one. An
  entry for the key's own layer wins over one for every layer.
- `hold`, `overlap`, `minHold`, `minPrior`: the Qukeys values for a
  dual-use key at that position (`qukeys.holdTimeout`,
  `qukeys.overlapThreshold`, `qukeys.minimumHoldTime`,
  `qukeys.minimumPriorInterval`), in the same units.
- `skHold`, `skOverlap`, `skTimeout`: the superkey values
  (`superkeys.holdstart`, `superkeys.overlap`, `superkeys.timeout`).

A value of `65535` means "the keyboard's value for this field". The list
ends with a key of `0`; the keyboard sends `0` after the last entry. At
most `timing.capacity` entries (48). The layer is the one the key was
looked up on (so a key seen through a transparent layer uses its own
layer's entry).

### `timing.capacity`, `timing.defaults`

Read-only: the number of entries the table holds, and the keyboard's
current values for the seven fields, in the order above.

## How it works inside

Findings from reading the firmware, recorded for the feature work:

- **Plugins and events.** The sketch (`src/mainDefy.cpp`) lists the plugins
  in `KALEIDOSCOPE_INIT_PLUGINS`; every key event runs through each
  plugin's `onKeyswitchEvent(Key &, KeyAddr, uint8_t state)` in that
  order, and a plugin that returns `EVENT_CONSUMED` stops it. Plugins
  re-inject events with `handleKeyswitchEvent`, guarding against seeing
  their own injection with a flag (the `INJECTED` state bit would make
  Qukeys and the superkeys ignore the event entirely). Chords is placed
  before `keyRoleManager`, which wraps Qukeys and the superkeys handler,
  so that a chord's keys are held back before anything decides what they
  do, and a chord's result is seen by those plugins as a physical press at
  the chord's first key.
- **How keys are decided.** `keyRoleManager` turns superkeys that have only
  a tap and a hold action into Qukeys dual-use codes in the keymap itself
  (`transform_keymap_superkeys_to_qukeys`); the rest are handled by
  `SuperkeysHandler` with one `Superkey` object per configured superkey
  and a `Timeline` that keeps presses in order. Qukeys queues presses and
  decides the head of the queue by hold timeout, overlap on rollover,
  minimum hold time and minimum prior interval. The fork gives both a
  per-key lookup: Qukeys loads the head key's timing when it identifies
  the head; a Superkey copies the shared timing and overrides it from the
  table when its key is pressed.
- **EEPROM.** 8 KB of emulated EEPROM in the last two application flash
  pages. `EEPROMSettings` hands out slices in the order plugins ask
  (`requestSlice`), keyed by a checksum of the slice sizes stored with a
  version byte in the first four bytes. Stock 2.2.1 uses about 6.3 KB:
  keymap 1600 (10 layers × 80 keys × 2), colormap 890, palette 64,
  superkeys 1548, macros 2048, and small settings. The fork asks for its
  slices last (chords 516 bytes, timing 576 bytes), so every stock slice
  keeps its place in both directions, and re-seals the checksum instead
  of marking the settings invalid when the layout grows. Erased flash
  reads as `0xFF`, which both plugins treat as empty. Going back to stock
  firmware leaves the two slices behind, harmlessly; stock's
  `settings.valid?` then reports false until its checksum is re-sealed,
  which nothing in Bazecor acts on.
- **Focus.** Each plugin answers `onFocusEvent(command)`: `handleHelp`
  adds its commands to `help`, `Focus.isEOL()` tells a get from a set,
  `Focus.read(uint16_t &)` parses the next number and `Focus.send(...)`
  writes values. A command's handler returns `EVENT_CONSUMED` once
  handled.
- **Versions.** `version` returns `DEFY_FW_VERSION` from the build;
  `hardware.firmware` returns the Neuron version (`v2.2.1`); Bazecor
  compares `version` to its release list with semver, so a suffix like
  `-curator.1` sorts as a prerelease of 2.2.1 and Bazecor offers Dygma's
  2.2.1 as an "update", which is the way back.

## Rebasing on a Dygma release

The fork's commits sit on top of the base tag in each repository. To move
to a newer Dygma release: in `Kaleidoscope-Dygma`, rebase `curator` onto
the commit the new release's libraries point at; in `NeuronWirelessLibs`,
rebase onto the new libraries commit and re-point the Kaleidoscope
submodule; here, rebase onto the new tag, update the submodule pointer,
and change `BASE` in `tools/manifest.py` and `BASE_TAG` in the workflow.
Dygma's main branch after 2.2.1 moved the plugins into a
`kaleidoscope_adapter` submodule and a `ConfigManager` with a fixed
configuration struct, so the next rebase is a port rather than a merge:
the plugins' logic carries over, the storage calls change.

## Status

- Builds: the stock tag and the fork, on NixOS with the nix shell, and in
  CI on Ubuntu 22.04 with Dygma's toolchain versions.
- Not yet run on a keyboard: the owner's Defy wireless is the first.
  The order to follow is in Keyboard Curator's `docs/release-checklist.md`
  (flash a stock build first, confirm `version`, go back with Bazecor,
  then the fork).
