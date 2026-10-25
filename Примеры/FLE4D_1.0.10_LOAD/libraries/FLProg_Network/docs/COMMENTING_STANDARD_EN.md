# Commenting standard

Every `src/**/*.h` and `src/**/*.cpp` source file, plus every executable
example, contains two comment layers: purpose/architecture notes and an
extended maintenance contract.

The extended contract records state ownership, call order, the cooperative
lifecycle, profile/platform boundaries and cases where a change requires a
separate compatibility or hardware gate.

Comments do not repeat code line by line and do not replace the API reference.
When behavior changes, update the corresponding language edition in the same
change. Documents, `library.properties`, `keywords.txt` and images are data,
so they retain headings, dates, status and history rather than artificial
comments.
