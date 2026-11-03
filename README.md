# Brendan Comedy Group

The bizarro twin of [londoncomedygroup.com](https://londoncomedygroup.com), live at
[brendancomedygroup.com](https://brendancomedygroup.com).

This repo doesn't hold a copy of the site. Every hour (and on every push) the workflow
checks out the London repo, runs `bizarro.py` over it and deploys the result to Pages.
New shows on the London site appear here automatically.

What `bizarro.py` changes:

- Ridwan and Brendan swap places: names, photos, credits and the catch game (now Catch Ridwan).
- London Comedy Group and Brendan Comedy Group swap names.
- A pride theme (`overlay/assets/bizarro.css`) and the Brendan gallery (`overlay/gallery/`).
- The London "sister site" banner points back to London.

Show times, venues and ticket links are never touched. Canonical links stay on
londoncomedygroup.com so the two sites don't compete in search.

Edit the jokes in the `COPY` list in `bizarro.py`. If London rewords one of those lines,
the build prints a warning and skips that joke instead of failing.

Preview locally: `python3 bizarro.py ../robertenciu86-cmyk.github.io /tmp/bcg`
