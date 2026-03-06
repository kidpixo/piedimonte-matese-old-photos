# New prompt ([gemini](https://gemini.google.com/app/7d30c20d349ce17b))


Act as a senior software engineer. I am refactoring a Jekyll site (Lanyon-based) into a high-integrity research database. We are moving from manual file management to a Python-driven data pipeline hosted on a VPS via Docker.

1. Data Architecture & Workflow:
    Archive Layer: archive/ (private) holds raw scans/notes.
    Source Layer: raw_data/ holds the "Master" files. Each entry is a [slug].md file and its primary [slug].jpg.
    Generated Layer: site_source/_photos/ is an auto-generated Jekyll collection.
    Editorial Layer: site_source/_topics/ contains manual Markdown essays.

2. Task: The Python Pipeline (scripts/process_research.py)
Write a script using python-frontmatter and Pillow that:

    Scans raw_data/*.md.
    Validates: Ensures Frontmatter contains title, date, location: {lat, lng}, and labels.
    Handles Variants: If the Frontmatter contains a variants list of image filenames, process those images in addition to the primary_image.
    Image Processing: Optimizes images to assets/images/ and creates 150x150 square thumbnails in assets/thumbs/.
    GeoJSON: Aggregates all photo locations into assets/data/points.geojson for a Leaflet map.
    Collection Generation: Writes a new .md file to site_source/_photos/ for every entry, preserving your long-form research text from the body of the raw file.

3. Task: Jekyll Configuration & Relational Logic

    _config.yml: Register photos and topics collections. Set output: true. Exclude archive/, raw_data/, and scripts/.
    _layouts/topic.html: This layout must allow for a manual essay ({{ content }}). It must also use a featured_photos array (containing id and commentary) to "Join" with the photos collection using Liquid:
    {% assign photo = site.photos | where: "slug", item.id | first %}.
    _layouts/photo.html: Update to display the primary image, any variants listed in frontmatter, and the GeoJSON-ready coordinates.

4. Task: Infrastructure & Deployment
    Dockerfile: Create a multi-stage build.
        Stage 1: Python environment to run the processing script and generate the GeoJSON/Photos.
        Stage 2: Ruby/Jekyll environment to build the site.
        Stage 3: Minimal Nginx image to serve the _site/ output.

    .dockerignore: Explicitly exclude the archive/ folder to prevent leaking private research material.

    Makefile: Create a make build command that orchestrates the Python script followed by the Jekyll build.

5. Task: Asset Refactor
Update the Lanyon template to move all public/ folder contents (CSS/JS) to assets/. Update _includes/head.html and sidebar.html to reflect these new paths.



If you have four versions of the same bridge, and you discover a new fact about the bridge's architect, you now have to update four files. You will forget one, and your data will drift.

The correct approach for a research project is the "Historical Object" Pattern: One Markdown file represents the event/object, and that file contains an array of visual representations.
1. The "Parent-Variant" Structure

Your raw_data/ file shouldn't just point to one image; it should point to a primary image and a list of variants.

raw_data/monastery-facade.md

```markdown
---
title: "Main Facade - San Pasquale Monastery"
primary_image: "monastery-facade-original.jpg"
variants:
  - file: "monastery-facade-restored-2024.jpg"
    type: "Digital Restoration"
    note: "Color corrected and noise reduced by MDA."
  - file: "monastery-facade-crop-detail.jpg"
    type: "Detail Crop"
    note: "Focus on the stone carving above the main portal."
location:
  lat: 41.376
  lng: 14.372
---
This monastery facade was... (Your research goes here once).
```

2. How the Python Script Handles This

Your script needs to be slightly smarter now. Instead of looking for slug.jpg, it reads the primary_image and the variants array.

    Process Primary: Resizes the main image and creates its thumbnail.

    Process Variants: Loops through the variants list, resizes each one, and puts them into a sub-folder (e.g., assets/photos/variants/monastery-facade/).

    Generate MD: The generated Jekyll file in _photos/ will now have a list of all these processed paths in its frontmatter.