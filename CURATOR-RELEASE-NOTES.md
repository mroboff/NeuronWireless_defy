Dygma Defy wireless firmware, Keyboard Curator fork. Based on Dygma's
`N2_Defy_v2.2.1`, with two additions configured from Keyboard Curator:

- **Chords (combos)**: several keys pressed together send another key.
  Focus commands `chords.map`, `chords.timeout`, `chords.memory`.
- **Per-key hold and tap timing** for dual-use keys and superkeys. Focus
  commands `timing.map`, `timing.capacity`, `timing.defaults`.

Everything else is Dygma's firmware as released. The keyboard reports its
version as `v2.2.1-curator.N`.

**Installing**: with Bazecor's firmware update, choose a custom firmware
folder holding `Wireless_neuron.hex` and `keyscanner.bin` from this
release (the keyscanner image is Dygma's own, unchanged), or install it from
Keyboard Curator's board page. Going back: Bazecor's firmware update,
pointed at Dygma's own release, puts the stock firmware back. Your keys,
superkeys, macros, colors and settings stay where they are either way.

This is experimental firmware, built and checked only against the
firmware's own build; see `CURATOR.md` in the repository for what has
been run on a keyboard.
