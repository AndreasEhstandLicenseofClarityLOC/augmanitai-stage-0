#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 34 — Strip phantom related-cards in V11.2 pages.

V11.2-pages have <a class='related-card' href='<slug>.html'>...</a> blocks
pointing to slugs that don't exist in our atlas. Strip those broken cross-refs.

Also: rewrite remaining relative .html-links to proper /augmanitai-stage-0/atlas/<slug>/ URLs.
"""
import re, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"
BASE_URL = "https://andreasehstandlicenseofclarityloc.github.io/augmanitai-stage-0"


def main():
    existing = {d.name for d in ATLAS.iterdir() if d.is_dir()}
    print(f"Atlas existing slugs: {len(existing)}")

    n_stripped = 0
    n_rewritten = 0
    n_files = 0

    for d in ATLAS.iterdir():
        if not d.is_dir(): continue
        fp = d / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        orig = c

        # Find ALL <a ... href='<target>.html' class='related-card'>...</a> patterns
        def card_replacer(m):
            nonlocal n_stripped, n_rewritten
            href = m.group(1)
            # extract slug from href (could be 'foo.html' or 'foo-bar.html')
            slug_m = re.match(r"^([a-z0-9-]+)\.html$", href)
            if not slug_m:
                return m.group(0)
            target_slug = slug_m.group(1)
            if target_slug in existing:
                # rewrite href to proper path
                new = m.group(0).replace(f"href='{href}'", f"href='/augmanitai-stage-0/atlas/{target_slug}/'")
                new = new.replace(f'href="{href}"', f'href="/augmanitai-stage-0/atlas/{target_slug}/"')
                n_rewritten += 1
                return new
            else:
                # target doesn't exist → strip whole card
                n_stripped += 1
                return ""

        # related-card with single quotes
        c = re.sub(
            r"<a\s+href='([a-z0-9-]+\.html)'\s+class='related-card'>.*?</a>",
            card_replacer, c, flags=re.DOTALL
        )
        # related-card with double quotes
        c = re.sub(
            r'<a\s+href="([a-z0-9-]+\.html)"\s+class="related-card">.*?</a>',
            card_replacer, c, flags=re.DOTALL
        )

        # Strip ALL other <a> with relative .html that points to non-existent slug
        def link_strip(m):
            href = m.group(1)
            slug_m = re.match(r"^([a-z0-9-]+)\.html$", href)
            if not slug_m:
                return m.group(0)
            target = slug_m.group(1)
            if target not in existing:
                # remove link, keep visible text
                inner = m.group(2)
                return inner
            else:
                # rewrite to proper URL
                return f'<a href="/augmanitai-stage-0/atlas/{target}/">{m.group(2)}</a>'

        # Generic <a href='X.html'>text</a>
        c = re.sub(
            r"<a\s+href='([a-z0-9-]+\.html)'[^>]*>([^<]*)</a>",
            link_strip, c
        )
        c = re.sub(
            r'<a\s+href="([a-z0-9-]+\.html)"[^>]*>([^<]*)</a>',
            link_strip, c
        )

        if c != orig:
            fp.write_text(c, encoding="utf-8")
            n_files += 1

    print(f"Cards stripped (phantom targets): {n_stripped}")
    print(f"Cards/links rewritten to canonical URL: {n_rewritten}")
    print(f"Files modified: {n_files}")


if __name__ == "__main__":
    main()
