#!/usr/bin/env python3
"""
Process Research Photos Pipeline

Transforms raw_data/*.md (with YAML frontmatter + images) into:
1. Optimized images in assets/images/ (primary + variants)
2. Thumbnails in assets/thumbs/
3. GeoJSON in assets/data/
4. Jekyll-ready .md files in _photos/

Inspired by convert_photos_coords.py for location/GeoJSON processing.
"""

import logging
import pathlib
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple
import yaml
import json

try:
    import frontmatter
    from PIL import Image
    import geopandas as gpd
    from shapely.geometry import Point, Polygon, LineString
except ImportError as e:
    print(f"ERROR: Missing required package: {e}")
    print("Install with: pip install python-frontmatter Pillow geopandas shapely pandas")
    exit(1)

# ============================================================================
# Configuration & Constants
# ============================================================================

# Paths (computed relative to script location)
SCRIPT_DIR = pathlib.Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAW_DATA_DIR = PROJECT_ROOT / "raw_data"
PHOTOS_OUTPUT_DIR = PROJECT_ROOT / "_photos"
ASSETS_DIR = PROJECT_ROOT / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
THUMBS_DIR = ASSETS_DIR / "thumbs"
MAPS_DATA_DIR = ASSETS_DIR / "maps_data"
VARIANTS_DIR = IMAGES_DIR / "variants"
VARIANTS_THUMBS_DIR = THUMBS_DIR / "variants"

# Image processing
THUMBNAIL_SIZE = (150, 150)
THUMBNAIL_QUALITY = 85
IMAGE_QUALITY = 90
MAX_IMAGE_WIDTH = 2000
RGB_BACKGROUND_COLOR = (255, 255, 255)
IMAGE_MODES_WITH_ALPHA = ("RGBA", "LA", "P")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".webm"}

# Coordinate validation sets
REQUIRED_COORD_SETS = {
    "origin": {"latitude_origin", "longitude_origin"},
    "vertices": {"latitude_vertex_left", "longitude_vertex_left",
                 "latitude_vertex_right", "longitude_vertex_right"},
}

# Geometry keys to remove from location
GEOMETRY_KEYS_TO_REMOVE = {
    "origin_geojson", "line_of_sight_geojson", "fov_geojson",
    "origin_wkt", "line_of_sight_wkt", "fov_wkt"
}
# Required frontmatter fields
REQUIRED_FIELDS = {"title", "date", "location", "labels"}

# Setup logging
def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    return logger


# ============================================================================
# Image Processing Utilities
# ============================================================================

def convert_image_to_rgb(img: Image.Image) -> Image.Image:
    """Convert image to RGB, handling transparency with white background."""
    if img.mode not in IMAGE_MODES_WITH_ALPHA:
        return img
    rgb_img = Image.new("RGB", img.size, RGB_BACKGROUND_COLOR)
    alpha_mask = img.split()[-1] if img.mode == "RGBA" else None
    rgb_img.paste(img, mask=alpha_mask)
    return rgb_img


# ============================================================================
# Image Processing
# ============================================================================

def slug_from_path(filepath: pathlib.Path) -> str:
    """Generate slug from .md filename (remove .md extension)."""
    return filepath.stem


def optimize_image(
    input_path: pathlib.Path,
    output_path: pathlib.Path,
    max_width: int = MAX_IMAGE_WIDTH,
    quality: int = IMAGE_QUALITY
) -> bool:
    """Optimize image: convert color space, resize if needed, compress, and save."""
    try:
        # Load and convert image to RGB
        img = Image.open(input_path)
        img = convert_image_to_rgb(img)
        
        # Resize if wider than max_width
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Ensure output directory exists and save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, quality=quality, optimize=True)
        
        logger.debug(f"✓ Optimized: {input_path.name} → {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to optimize {input_path.name}: {e}")
        return False


def create_thumbnail(
    input_path: pathlib.Path,
    output_path: pathlib.Path,
    size: Tuple[int, int] = THUMBNAIL_SIZE,
    quality: int = THUMBNAIL_QUALITY
) -> bool:
    """Create square thumbnail by center-cropping and resizing."""
    try:
        # Load and convert image to RGB
        img = Image.open(input_path)
        img = convert_image_to_rgb(img)
        
        # Center-crop to square
        min_dim = min(img.width, img.height)
        left = (img.width - min_dim) // 2
        top = (img.height - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))
        
        # Resize to target thumbnail size
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        # Ensure output directory exists and save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, quality=quality, optimize=True)
        
        logger.debug(f"✓ Thumbnail: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to create thumbnail for {input_path.name}: {e}")
        return False


# ============================================================================
# Location & GeoJSON Processing (adapted from convert_photos_coords.py)
# ============================================================================

def calculate_boresight_point(lat_left: float, lon_left: float, lat_right: float, lon_right: float) -> tuple:
    """
    Calculate boresight as the midpoint between the two vertices.
    Returns (lat_boresight, lon_boresight).
    """
    lat_boresight = (lat_left + lat_right) / 2.0
    lon_boresight = (lon_left + lon_right) / 2.0
    return lat_boresight, lon_boresight


def create_geojson_point(lat: float, lon: float) -> Dict:
    """Create a GeoJSON Point geometry."""
    return {
        "type": "Point",
        "coordinates": [lon, lat]
    }


def create_geojson_polygon(lat_origin: float, lon_origin: float, lat_left: float, lon_left: float,
                          lat_right: float, lon_right: float) -> Dict:
    """Create a GeoJSON Polygon geometry for field of view."""
    return {
        "type": "Polygon",
        "coordinates": [[
            [lon_origin, lat_origin],
            [lon_left, lat_left],
            [lon_right, lat_right],
            [lon_origin, lat_origin]
        ]]
    }


def create_geojson_linestring(lat_origin: float, lon_origin: float, lat_boresight: float, lon_boresight: float) -> Dict:
    """Create a GeoJSON LineString geometry for line of sight."""
    return {
        "type": "LineString",
        "coordinates": [
            [lon_origin, lat_origin],
            [lon_boresight, lat_boresight]
        ]
    }


def extract_location(location_data: List[Dict]) -> Tuple[Optional[Point], Optional[Polygon]]:
    """
    Extract origin Point and FOV Polygon from frontmatter location array.
    
    Expected format (matching your raw_data structure):
        location:
          - latitude_origin: 41.355
          - longitude_origin: 14.371
          - latitude_vertex_left: 41.356
          - longitude_vertex_left: 14.372
          - latitude_vertex_right: 41.354
          - longitude_vertex_right: 14.370
    
    Note: Each coordinate is in a separate dict entry in the list.
    
    Returns: (origin_point, fov_polygon)
    """
    try:
        if not location_data or not isinstance(location_data, list):
            logger.warning("Location data missing or not a list")
            return None, None
        
        # Collect all coordinate values from the location list
        coords = {}
        for loc_dict in location_data:
            if isinstance(loc_dict, dict):
                coords.update(loc_dict)
        
        # Extract origin
        origin = None
        if "latitude_origin" in coords and "longitude_origin" in coords:
            origin = Point(coords["longitude_origin"], coords["latitude_origin"])
            logger.debug(f"  Found origin: {origin}")
        
        if not origin:
            logger.warning("No origin coordinates found in location data")
            return None, None
        
        # Create FOV polygon if vertices present
        fov = None
        if "latitude_vertex_left" in coords and "longitude_vertex_left" in coords and \
           "latitude_vertex_right" in coords and "longitude_vertex_right" in coords:
            vertex_left = Point(coords["longitude_vertex_left"], coords["latitude_vertex_left"])
            vertex_right = Point(coords["longitude_vertex_right"], coords["latitude_vertex_right"])
            fov = Polygon([origin, vertex_left, vertex_right, origin])
            logger.debug(f"  Created FOV polygon")
        
        return origin, fov
        
    except Exception as e:
        logger.error(f"Failed to extract location: {e}")
        return None, None


def extract_coords_from_location(location_data: Any) -> Dict:
    """Extract all coordinate key-value pairs from location dict."""
    if isinstance(location_data, dict):
        return dict(location_data)
    if isinstance(location_data, list):
        merged: Dict = {}
        for item in location_data:
            if isinstance(item, dict):
                merged.update(item)
        return merged
    return {}


def normalize_location_data(location_data: Any) -> Dict:
    """Normalize location payload to a single dict shape."""
    normalized = extract_coords_from_location(location_data)
    for key in GEOMETRY_KEYS_TO_REMOVE:
        normalized.pop(key, None)
    return normalized


def is_numeric_coordinate(value: Any) -> bool:
    """Return True when a coordinate value is non-empty and numeric."""
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def validate_coordinates(coords: Dict, coord_set: str) -> bool:
    """Check if required coordinates are present and numeric."""
    required_keys = REQUIRED_COORD_SETS.get(coord_set, set())
    return all(k in coords and is_numeric_coordinate(coords.get(k)) for k in required_keys)


def diagnose_location_keys(coords: Dict, source: str = "") -> None:
    """Log a detailed diff of found vs expected coordinate keys.
    Uses difflib to flag likely typos so the user can fix them quickly."""
    import difflib
    all_required = set().union(*REQUIRED_COORD_SETS.values())
    found_keys = set(coords.keys())
    missing = all_required - found_keys
    unexpected = found_keys - all_required

    prefix = f"  [{source}]" if source else " "

    if not missing:
        return  # nothing to diagnose

    logger.error(f"{prefix} Location key diagnosis:")
    logger.error(f"{prefix}   Expected keys : {sorted(all_required)}")
    logger.error(f"{prefix}   Found keys    : {sorted(found_keys)}")
    logger.error(f"{prefix}   Missing keys  : {sorted(missing)}")

    # Suggest fixes for each missing key
    for key in sorted(missing):
        candidates = difflib.get_close_matches(key, found_keys, n=3, cutoff=0.6)
        if candidates:
            logger.error(
                f"{prefix}   TYPO? '{key}' not found — did you mean: {candidates}?"
            )
    if unexpected:
        logger.warning(f"{prefix}   Unrecognised keys (possible typos): {sorted(unexpected)}")


def add_geojson_to_location(location_data: Any) -> Dict:
    """Add GeoJSON geometry strings to the location dict."""
    if not location_data:
        return {}
    location_dict = normalize_location_data(location_data)
    coords = extract_coords_from_location(location_dict)
    # Validate origin is present
    if not validate_coordinates(coords, "origin"):
        logger.warning("  Cannot generate GeoJSON: missing origin coordinates")
        diagnose_location_keys(coords, source="add_geojson_to_location")
        return location_dict
    # Create origin_geojson
    lat_origin = float(coords["latitude_origin"])
    lon_origin = float(coords["longitude_origin"])
    origin_geom = create_geojson_point(lat_origin, lon_origin)
    location_dict["origin_geojson"] = json.dumps(origin_geom)
    # Create fov_geojson and line_of_sight_geojson if vertices present
    if validate_coordinates(coords, "vertices"):
        lat_left = float(coords["latitude_vertex_left"])
        lon_left = float(coords["longitude_vertex_left"])
        lat_right = float(coords["latitude_vertex_right"])
        lon_right = float(coords["longitude_vertex_right"])
        fov_geom = create_geojson_polygon(lat_origin, lon_origin, lat_left, lon_left, lat_right, lon_right)
        location_dict["fov_geojson"] = json.dumps(fov_geom)
        if is_numeric_coordinate(coords.get("latitude_boresight")) and is_numeric_coordinate(coords.get("longitude_boresight")):
            lat_bs = float(coords["latitude_boresight"])
            lon_bs = float(coords["longitude_boresight"])
        else:
            lat_bs, lon_bs = calculate_boresight_point(lat_left, lon_left, lat_right, lon_right)
        los_geom = create_geojson_linestring(lat_origin, lon_origin, lat_bs, lon_bs)
        location_dict["line_of_sight_geojson"] = json.dumps(los_geom)
    return location_dict


def validate_frontmatter_geo(metadata: Dict, filepath: pathlib.Path) -> Tuple[bool, str]:
    """Validate only geo-required frontmatter fields."""
    missing = REQUIRED_FIELDS - set(metadata.keys())
    if missing:
        msg = f"{filepath.name}: Missing fields for GeoJSON: {missing}"
        logger.error(msg)
        return False, msg
    return True, ""


# ============================================================================
# Frontmatter Processing
# ============================================================================

def validate_frontmatter(post: frontmatter.Post, filepath: pathlib.Path) -> Tuple[bool, str]:
    """
    Validate that frontmatter contains required fields.
    Returns: (is_valid, error_message)
    """
    missing = REQUIRED_FIELDS - set(post.metadata.keys())
    
    if missing:
        msg = f"{filepath.name}: Missing fields: {missing}"
        logger.error(msg)
        return False, msg
    
    images = post.metadata.get("images")
    if images is not None:
        if not isinstance(images, list) or not images:
            msg = f"{filepath.name}: 'images' must be a non-empty list"
            logger.error(msg)
            return False, msg

        for idx, image_obj in enumerate(images, start=1):
            if not isinstance(image_obj, dict):
                msg = f"{filepath.name}: images[{idx}] must be an object"
                logger.error(msg)
                return False, msg

            image_file = image_obj.get("file")
            if not image_file:
                msg = f"{filepath.name}: images[{idx}] missing required key: file"
                logger.error(msg)
                return False, msg

            image_path = RAW_DATA_DIR / image_file
            if not image_path.exists():
                msg = f"{filepath.name}: image file not found: {image_file}"
                logger.error(msg)
                return False, msg
    else:
        # Legacy fallback schema: primary_image (+ optional variants)
        primary_image = post.metadata.get("primary_image")
        if not primary_image:
            msg = f"{filepath.name}: missing image data (expected 'images' array or 'primary_image')"
            logger.error(msg)
            return False, msg

        image_path = RAW_DATA_DIR / primary_image
        if not image_path.exists():
            msg = f"{filepath.name}: primary_image not found: {primary_image}"
            logger.error(msg)
            return False, msg

        variants = post.metadata.get("variants", [])
        if variants and not isinstance(variants, list):
            msg = f"{filepath.name}: 'variants' must be a list"
            logger.error(msg)
            return False, msg

        for idx, variant in enumerate(variants, start=1):
            if not isinstance(variant, dict):
                msg = f"{filepath.name}: variants[{idx}] must be an object"
                logger.error(msg)
                return False, msg
            variant_file = variant.get("file")
            if not variant_file:
                msg = f"{filepath.name}: variants[{idx}] missing required key: file"
                logger.error(msg)
                return False, msg
            variant_path = RAW_DATA_DIR / variant_file
            if not variant_path.exists():
                msg = f"{filepath.name}: variant file not found: {variant_file}"
                logger.error(msg)
                return False, msg
    
    return True, ""


def normalize_images_from_metadata(metadata: Dict) -> List[Dict[str, Any]]:
    """Normalize image schema to a single list format.

    Preferred input schema:
      images: [{file, is_primary?, type?, note?, alt?}, ...]

    Legacy fallback schema:
      primary_image: "..."
      variants: [{file, type?, note?, alt?}, ...]
    """
    images = metadata.get("images")
    normalized: List[Dict[str, Any]] = []

    if isinstance(images, list) and images:
        for image_obj in images:
            if not isinstance(image_obj, dict):
                continue
            image_file = image_obj.get("file")
            if not image_file:
                continue
            normalized.append({
                "file": image_file,
                "is_primary": bool(image_obj.get("is_primary", False)),
                "type": image_obj.get("type", ""),
                "note": image_obj.get("note", ""),
                "alt": image_obj.get("alt", ""),
            })
        return normalized

    primary_image = metadata.get("primary_image")
    if primary_image:
        normalized.append({
            "file": primary_image,
            "is_primary": True,
            "type": "original",
            "note": "",
            "alt": "",
        })

    variants = metadata.get("variants", [])
    if isinstance(variants, list):
        for variant in variants:
            if not isinstance(variant, dict):
                continue
            variant_file = variant.get("file")
            if not variant_file:
                continue
            normalized.append({
                "file": variant_file,
                "is_primary": False,
                "type": variant.get("type", ""),
                "note": variant.get("note", ""),
                "alt": variant.get("alt", ""),
            })

    return normalized


def process_images(slug: str, metadata: Dict) -> bool:
    """Process all images: optimize each and create thumbnails.

    Uses images[] schema when present, with first image as default primary unless
    an item has is_primary=true.
    """
    normalized_images = normalize_images_from_metadata(metadata)
    if not normalized_images:
        logger.warning("  No images found to process")
        return False

    primary_index = 0
    for idx, image_obj in enumerate(normalized_images):
        if image_obj.get("is_primary"):
            primary_index = idx
            break

    processed_images: List[Dict[str, Any]] = []
    processed_variants: List[Dict[str, Any]] = []

    for idx, image_obj in enumerate(normalized_images):
        image_file = image_obj["file"]
        image_path = RAW_DATA_DIR / image_file

        if not image_path.exists():
            logger.warning(f"  Image not found: {image_file}")
            continue

        image_name = pathlib.Path(image_file).name
        is_primary = idx == primary_index

        if is_primary:
            optimized_path = IMAGES_DIR / f"{slug}-main.jpg"
            thumb_path = THUMBS_DIR / f"{slug}.jpg"
        else:
            optimized_path = VARIANTS_DIR / slug / image_name
            thumb_path = VARIANTS_THUMBS_DIR / slug / image_name

        optimize_ok = optimize_image(image_path, optimized_path)
        thumb_ok = create_thumbnail(image_path, thumb_path)

        processed_obj = {
            "file": str(optimized_path.relative_to(PROJECT_ROOT)) if optimize_ok else "",
            "thumb": str(thumb_path.relative_to(PROJECT_ROOT)) if thumb_ok else "",
            "type": image_obj.get("type", ""),
            "note": image_obj.get("note", ""),
            "alt": image_obj.get("alt", ""),
            "is_primary": is_primary,
        }
        processed_images.append(processed_obj)

        if is_primary:
            if optimize_ok:
                metadata["processed_primary_image"] = processed_obj["file"]
            if thumb_ok:
                metadata["processed_primary_thumb"] = processed_obj["thumb"]
            metadata["primary_image"] = image_file
        else:
            processed_variants.append({
                "file": processed_obj["file"],
                "thumb": processed_obj["thumb"],
                "type": processed_obj["type"],
                "note": processed_obj["note"],
                "alt": processed_obj["alt"],
            })

    if processed_images:
        metadata["images"] = processed_images
        metadata["processed_images"] = processed_images
        metadata["variants"] = processed_variants
        return True

    return False


def process_location_data(metadata: Dict, source: str = "") -> None:
    location_data = metadata.get("location")
    if not location_data:
        return
    location_dict = normalize_location_data(location_data)
    coords = extract_coords_from_location(location_dict)
    if not validate_coordinates(coords, "origin"):
        logger.warning(f"  [{source or 'location'}] Skipping location: origin coordinates missing or invalid")
        diagnose_location_keys(coords, source=source or "location")
        metadata["location"] = location_dict
        return
    lat_origin = float(coords["latitude_origin"])
    lon_origin = float(coords["longitude_origin"])
    metadata["_origin"] = Point(lon_origin, lat_origin)
    if validate_coordinates(coords, "vertices"):
        lat_left = float(coords["latitude_vertex_left"])
        lon_left = float(coords["longitude_vertex_left"])
        lat_right = float(coords["latitude_vertex_right"])
        lon_right = float(coords["longitude_vertex_right"])
        vertex_left = Point(lon_left, lat_left)
        vertex_right = Point(lon_right, lat_right)
        origin = Point(lon_origin, lat_origin)
        metadata["_fov"] = Polygon([origin, vertex_left, vertex_right, origin])
    metadata["location"] = add_geojson_to_location(location_dict)


def process_post(filepath: pathlib.Path) -> Optional[Dict]:
    """Process a single .md file through the complete pipeline.
    
    Pipeline:
    1. Read markdown with frontmatter
    2. Validate required fields
    3. Optimize images (primary + variants)
    4. Extract coordinates and generate GeoJSON
    5. Return processed metadata
    """
    logger.info(f"Processing: {filepath.name}")
    
    # Step 1: Read and parse markdown file
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
    except Exception as e:
        logger.error(f"Failed to read {filepath.name}: {e}")
        return None
    
    # Step 2: Validate frontmatter has required fields
    is_valid, error_msg = validate_frontmatter(post, filepath)
    if not is_valid:
        return None
    
    slug = slug_from_path(filepath)
    metadata = post.metadata.copy()
    
    # Step 3: Process images
    process_images(slug, metadata)
    
    # Step 4: Extract location and generate GeoJSON
    process_location_data(metadata, source=filepath.name)
    
    # Step 5: Store markdown body for later output
    metadata["_body"] = post.content
    
    logger.info(f"✓ Successfully processed: {slug}")
    return metadata


def process_geo_metadata(filepath: pathlib.Path) -> Optional[Dict]:
    """Process a single file for GeoJSON only (no images, no _photos markdown)."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
    except Exception as e:
        logger.error(f"Failed to read {filepath.name} for GeoJSON: {e}")
        return None

    metadata = post.metadata.copy()
    is_valid, _ = validate_frontmatter_geo(metadata, filepath)
    if not is_valid:
        return None

    metadata["slug"] = slug_from_path(filepath)
    process_location_data(metadata, source=filepath.name)
    return metadata


def collect_geojson_metadata(md_files: List[pathlib.Path]) -> List[Dict]:
    """Collect and normalize metadata used for GeoJSON from a list of markdown files."""
    output: List[Dict] = []
    for filepath in sorted(md_files):
        metadata = process_geo_metadata(filepath)
        if metadata:
            output.append(metadata)
    return output


def get_git_raw_data_changes() -> Tuple[List[pathlib.Path], List[str]]:
    """Return changed raw_data markdown paths and deleted markdown slugs from git status."""
    cmd = [
        "git",
        "-C",
        str(PROJECT_ROOT),
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        "raw_data",
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except Exception as e:
        logger.warning(f"Unable to read git status; fallback to all files: {e}")
        return sorted(RAW_DATA_DIR.glob("*.md")), []

    changed_files: set[pathlib.Path] = set()
    deleted_slugs: set[str] = set()
    raw_dir = RAW_DATA_DIR.resolve()

    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        status = line[:2]
        path_part = line[3:].strip()

        old_path = None
        new_path = path_part
        if " -> " in path_part:
            old_path, new_path = path_part.split(" -> ", 1)
            old_path = old_path.strip()
            new_path = new_path.strip()

        if old_path and old_path.startswith("raw_data/") and old_path.endswith(".md") and "R" in status:
            deleted_slugs.add(pathlib.Path(old_path).stem)

        if path_part.startswith("raw_data/") and path_part.endswith(".md") and "D" in status:
            deleted_slugs.add(pathlib.Path(path_part).stem)

        candidate = (PROJECT_ROOT / new_path).resolve()
        if candidate.suffix.lower() == ".md" and candidate.parent == raw_dir and candidate.exists():
            changed_files.add(candidate)

    return sorted(changed_files), sorted(deleted_slugs)


def prune_deleted_photos(slugs: List[str]) -> int:
    """Delete generated _photos markdown for removed raw_data records."""
    removed = 0
    for slug in slugs:
        target = PHOTOS_OUTPUT_DIR / f"{slug}.md"
        if target.exists():
            target.unlink()
            removed += 1
            logger.info(f"Pruned stale output: {target}")
    return removed


def is_image_path(path: pathlib.Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def iter_image_files(base_dir: pathlib.Path) -> List[pathlib.Path]:
    if not base_dir.exists():
        return []
    return sorted([p for p in base_dir.rglob("*") if p.is_file() and is_image_path(p)])


def collect_referenced_raw_images(metadata: Dict) -> set[pathlib.Path]:
    refs: set[pathlib.Path] = set()
    normalized_images = normalize_images_from_metadata(metadata)
    for image_obj in normalized_images:
        image_file = image_obj.get("file")
        if image_file:
            refs.add((RAW_DATA_DIR / image_file).resolve())
    return refs


def expected_generated_assets(slug: str, metadata: Dict) -> Tuple[set[pathlib.Path], set[pathlib.Path]]:
    """Compute expected generated image/thumb files for a raw metadata record."""
    expected_images: set[pathlib.Path] = set()
    expected_thumbs: set[pathlib.Path] = set()

    normalized_images = normalize_images_from_metadata(metadata)
    if not normalized_images:
        return expected_images, expected_thumbs

    primary_index = 0
    for idx, image_obj in enumerate(normalized_images):
        if image_obj.get("is_primary"):
            primary_index = idx
            break

    for idx, image_obj in enumerate(normalized_images):
        image_name = pathlib.Path(image_obj.get("file", "")).name
        is_primary = idx == primary_index
        if is_primary:
            expected_images.add((IMAGES_DIR / f"{slug}-main.jpg").resolve())
            expected_thumbs.add((THUMBS_DIR / f"{slug}.jpg").resolve())
        else:
            expected_images.add((VARIANTS_DIR / slug / image_name).resolve())
            expected_thumbs.add((VARIANTS_THUMBS_DIR / slug / image_name).resolve())

    return expected_images, expected_thumbs


def summarize_check_report(report: Dict, json_output: bool) -> None:
    if json_output:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    logger.info("=== CHECK REPORT ===")
    logger.info(f"raw_md_files={report['stats']['raw_md_files']}")
    logger.info(f"raw_images={report['stats']['raw_images']}")
    logger.info(f"photos_md_files={report['stats']['photos_md_files']}")
    logger.info(f"expected_generated_images={report['stats']['expected_generated_images']}")
    logger.info(f"expected_generated_thumbs={report['stats']['expected_generated_thumbs']}")
    logger.info(f"errors={len(report['errors'])} warnings={len(report['warnings'])}")

    logger.info("-- raw_data/*.md --")
    for item in report["raw_md"]:
        logger.info(
            f"{item['file']} geo_valid={item['geo_valid']} refs={item['referenced_images']}"
        )

    if report["errors"]:
        logger.error("-- Errors --")
        for msg in report["errors"]:
            logger.error(msg)

    if report["warnings"]:
        logger.warning("-- Warnings --")
        for msg in report["warnings"]:
            logger.warning(msg)


def flatten_orphan_groups(orphan_groups: Dict[str, List[pathlib.Path]]) -> List[pathlib.Path]:
    """Flatten and sort orphan files from all groups."""
    all_paths: set[pathlib.Path] = set()
    for paths in orphan_groups.values():
        all_paths.update(paths)
    return sorted(all_paths)


def confirm_orphan_cleanup(total_files: int) -> bool:
    """Prompt user to confirm orphan cleanup."""
    if total_files <= 0:
        return False

    try:
        answer = input(f"Found {total_files} orphan files. Delete them now? [y/N]: ").strip().lower()
    except EOFError:
        logger.warning("No interactive input available; skipping --clean")
        return False

    return answer in {"y", "yes"}


def clean_orphan_files(orphan_groups: Dict[str, List[pathlib.Path]]) -> Dict[str, int]:
    """Delete orphan files discovered during check mode."""
    deleted = 0
    failed = 0

    for path in flatten_orphan_groups(orphan_groups):
        try:
            if path.exists() and path.is_file():
                path.unlink()
                deleted += 1
                logger.info(f"Deleted orphan: {path.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            failed += 1
            logger.error(f"Failed deleting orphan {path}: {e}")

    return {
        "deleted": deleted,
        "failed": failed,
    }


def run_check_mode(
    json_output: bool = False,
    strict_warnings: bool = False,
    clean: bool = False,
    auto_yes: bool = False,
) -> int:
    """Run repository consistency checks.

    Exit codes:
      0 = no errors
      1 = one or more errors
            -1 = warnings found in strict-warnings mode (shell exit code 255)
      2 = internal failure
    """
    try:
        raw_md_files = sorted(RAW_DATA_DIR.glob("*.md"))
        raw_slugs = {p.stem for p in raw_md_files}
        photos_md_files = sorted(PHOTOS_OUTPUT_DIR.glob("*.md")) if PHOTOS_OUTPUT_DIR.exists() else []
        photos_slugs = {p.stem for p in photos_md_files}

        referenced_raw_images: set[pathlib.Path] = set()
        expected_images: set[pathlib.Path] = set()
        expected_thumbs: set[pathlib.Path] = set()

        report: Dict[str, Any] = {
            "stats": {
                "raw_md_files": len(raw_md_files),
                "raw_images": 0,
                "photos_md_files": len(photos_md_files),
                "expected_generated_images": 0,
                "expected_generated_thumbs": 0,
            },
            "raw_md": [],
            "errors": [],
            "warnings": [],
        }

        logger.info(f"Check: scanning {len(raw_md_files)} raw_data/*.md files")

        for filepath in raw_md_files:
            item = {
                "file": filepath.name,
                "geo_valid": False,
                "referenced_images": 0,
            }

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
            except Exception as e:
                report["errors"].append(f"{filepath.name}: failed to read frontmatter: {e}")
                report["raw_md"].append(item)
                continue

            metadata = post.metadata.copy()

            is_valid, msg = validate_frontmatter(post, filepath)
            if not is_valid:
                report["errors"].append(msg)

            location_data = normalize_location_data(metadata.get("location"))
            coords = extract_coords_from_location(location_data)
            geo_valid = validate_coordinates(coords, "origin")
            item["geo_valid"] = geo_valid
            if not geo_valid:
                report["errors"].append(f"{filepath.name}: invalid or missing origin geo coordinates")

            refs = collect_referenced_raw_images(metadata)
            item["referenced_images"] = len(refs)
            referenced_raw_images.update(refs)

            for ref in refs:
                if not ref.exists():
                    report["errors"].append(
                        f"{filepath.name}: referenced image missing: {ref.relative_to(PROJECT_ROOT)}"
                    )

            slug = filepath.stem
            expected_photo = PHOTOS_OUTPUT_DIR / f"{slug}.md"
            if not expected_photo.exists():
                report["warnings"].append(
                    f"{filepath.name}: expected generated markdown missing: {expected_photo.relative_to(PROJECT_ROOT)}"
                )

            exp_images, exp_thumbs = expected_generated_assets(slug, metadata)
            expected_images.update(exp_images)
            expected_thumbs.update(exp_thumbs)

            report["raw_md"].append(item)

        raw_image_files = set(iter_image_files(RAW_DATA_DIR))
        report["stats"]["raw_images"] = len(raw_image_files)

        orphan_raw_images = sorted(raw_image_files - referenced_raw_images)
        for orphan in orphan_raw_images:
            report["warnings"].append(
                f"Orphan raw_data image not referenced by any markdown: {orphan.relative_to(PROJECT_ROOT)}"
            )

        orphan_photos_md = sorted(photos_slugs - raw_slugs)
        for slug in orphan_photos_md:
            orphan_path = PHOTOS_OUTPUT_DIR / f"{slug}.md"
            report["warnings"].append(
                f"Orphan _photos markdown without raw_data source: {orphan_path.relative_to(PROJECT_ROOT)}"
            )

        actual_generated_images: set[pathlib.Path] = set()
        if IMAGES_DIR.exists():
            actual_generated_images.update([p.resolve() for p in IMAGES_DIR.glob("*-main.jpg") if p.is_file()])
        if VARIANTS_DIR.exists():
            actual_generated_images.update([p.resolve() for p in iter_image_files(VARIANTS_DIR)])

        actual_generated_thumbs: set[pathlib.Path] = set()
        if THUMBS_DIR.exists():
            actual_generated_thumbs.update([p.resolve() for p in THUMBS_DIR.glob("*.jpg") if p.is_file()])
        if VARIANTS_THUMBS_DIR.exists():
            actual_generated_thumbs.update([p.resolve() for p in iter_image_files(VARIANTS_THUMBS_DIR)])

        report["stats"]["expected_generated_images"] = len(expected_images)
        report["stats"]["expected_generated_thumbs"] = len(expected_thumbs)

        orphan_generated_images = sorted(actual_generated_images - expected_images)
        for orphan in orphan_generated_images:
            report["warnings"].append(
                f"Orphan generated image in assets/images: {orphan.relative_to(PROJECT_ROOT)}"
            )

        orphan_generated_thumbs = sorted(actual_generated_thumbs - expected_thumbs)
        for orphan in orphan_generated_thumbs:
            report["warnings"].append(
                f"Orphan generated thumb in assets/thumbs: {orphan.relative_to(PROJECT_ROOT)}"
            )

        orphan_groups: Dict[str, List[pathlib.Path]] = {
            "raw_images": orphan_raw_images,
            "photos_markdown": [PHOTOS_OUTPUT_DIR / f"{slug}.md" for slug in orphan_photos_md],
            "generated_images": orphan_generated_images,
            "generated_thumbs": orphan_generated_thumbs,
        }

        summarize_check_report(report, json_output=json_output)

        if clean:
            orphan_files = flatten_orphan_groups(orphan_groups)
            if not orphan_files:
                logger.info("--clean requested, but no orphan files were found")
            elif not auto_yes and not confirm_orphan_cleanup(len(orphan_files)):
                logger.info("--clean cancelled by user")
            else:
                if auto_yes:
                    logger.info("--yes detected: skipping cleanup confirmation prompt")
                cleanup_stats = clean_orphan_files(orphan_groups)
                logger.info(
                    f"Cleanup summary deleted={cleanup_stats['deleted']} failed={cleanup_stats['failed']}"
                )

        if report["errors"]:
            return 1
        if strict_warnings and report["warnings"]:
            logger.error("Strict warnings mode: warnings present, failing check with -1")
            return -1
        return 0
    except Exception as e:
        logger.exception(f"Check mode failed: {e}")
        return 2


def jekyll_slugify(value: str) -> str:
    """Approximate Jekyll slug behavior for collection URLs."""
    if not value:
        return ""
    normalized = value.strip().lower().replace("_", "-")
    normalized = re.sub(r"[^a-z0-9\-]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized)
    return normalized.strip("-")


def derive_photo_post_rel_url(metadata: Dict) -> str:
    """Build relative collection URL for the photo post from primary image filename."""
    images = metadata.get("images")
    primary_file = ""

    if isinstance(images, list) and images:
        primary = next((img for img in images if img.get("is_primary")), images[0])
        if isinstance(primary, dict):
            primary_file = primary.get("file", "")

    if primary_file:
        stem = pathlib.Path(primary_file).stem
        page_slug = jekyll_slugify(stem.replace("-main", ""))
        if page_slug:
            return f"/photos/{page_slug}/"

    fallback = metadata.get("slug") or metadata.get("title") or ""
    fallback_slug = jekyll_slugify(str(fallback))
    return f"/photos/{fallback_slug}/" if fallback_slug else ""


# ============================================================================
# GeoJSON Generation
# ============================================================================

def generate_geojson(all_metadata: List[Dict]) -> Dict[str, Any]:
    """
    Aggregate all processed photos into GeoJSON files using geopandas.
    Follows the pattern from convert_photos_coords.py:
    - photos_origin.geojson (Point features)
    - photos_fov.geojson (Polygon features)
    """
    try:
        MAPS_DATA_DIR.mkdir(parents=True, exist_ok=True)

        origins_data = []
        fovs_data = []
        lov_data = []

        for metadata in all_metadata:
            # Determine filename/slug
            slug = metadata.get('slug') if metadata.get('slug') else metadata.get('title', '')
            photo_post_rel_url = derive_photo_post_rel_url(metadata)
            # Try to get primary image filename
            filename = ''
            images = metadata.get('images')
            if images and isinstance(images, list) and len(images) > 0:
                primary = next((img for img in images if img.get('is_primary')), images[0])
                filename = primary.get('file', '')
            else:
                filename = metadata.get('primary_image', slug)

            # Points (origin)
            if metadata.get("_origin"):
                origins_data.append({
                    "title": metadata.get("title", ""),
                    "date": str(metadata.get("date", "")),
                    "labels": ",".join(metadata.get("labels", [])),
                    "filename": filename,
                    "photo_post_rel_url": photo_post_rel_url,
                    "text": metadata.get("title", ""),
                    "geometry": metadata["_origin"],
                })
            # Polygons (fov)
            if metadata.get("_fov"):
                fovs_data.append({
                    "title": metadata.get("title", ""),
                    "date": str(metadata.get("date", "")),
                    "filename": filename,
                    "text": metadata.get("title", ""),
                    "geometry": metadata["_fov"],
                })
            # Lines (lov)
            # Try to extract line_of_sight_geojson from location
            loc = metadata.get("location")
            if loc and isinstance(loc, dict):
                lov_geojson = loc.get("line_of_sight_geojson")
                if lov_geojson:
                    try:
                        geom = json.loads(lov_geojson)
                        # Convert to shapely geometry
                        line = LineString(geom["coordinates"])
                        lov_data.append({
                            "title": metadata.get("title", ""),
                            "date": str(metadata.get("date", "")),
                            "filename": filename,
                            "text": metadata.get("title", ""),
                            "geometry": line,
                        })
                    except Exception as e:
                        logger.warning(f"Failed to parse line_of_sight_geojson for {metadata.get('title','')}: {e}")

        if not origins_data and not fovs_data and not lov_data:
            logger.warning("No valid location data to generate GeoJSON")
            return {
                "ok": False,
                "origins": 0,
                "fovs": 0,
                "lov": 0,
            }

        # Write origins GeoJSON (Point features)
        if origins_data:
            origins_gdf = gpd.GeoDataFrame(origins_data, crs="EPSG:4326")
            origins_path = MAPS_DATA_DIR / "photos_origin.geojson"
            origins_gdf.to_file(origins_path, driver="GeoJSON")
            logger.debug(f"Generated: {origins_path} ({len(origins_gdf)} points)")

        # Write FOV GeoJSON (Polygon features)
        if fovs_data:
            fovs_gdf = gpd.GeoDataFrame(fovs_data, crs="EPSG:4326")
            fovs_path = MAPS_DATA_DIR / "photos_fov.geojson"
            fovs_gdf.to_file(fovs_path, driver="GeoJSON")
            logger.debug(f"Generated: {fovs_path} ({len(fovs_gdf)} polygons)")

        # Write LOV GeoJSON (Line features)
        if lov_data:
            lov_gdf = gpd.GeoDataFrame(lov_data, crs="EPSG:4326")
            lov_path = MAPS_DATA_DIR / "photos_lov.geojson"
            lov_gdf.to_file(lov_path, driver="GeoJSON")
            logger.debug(f"Generated: {lov_path} ({len(lov_gdf)} lines)")

        return {
            "ok": True,
            "origins": len(origins_data),
            "fovs": len(fovs_data),
            "lov": len(lov_data),
        }

    except Exception as e:
        logger.error(f"Failed to generate GeoJSON: {e}")
        return {
            "ok": False,
            "origins": 0,
            "fovs": 0,
            "lov": 0,
        }


# ============================================================================
# Jekyll Output
# ============================================================================

def format_frontmatter_indented(metadata: Dict) -> str:
    """Format metadata dict into YAML frontmatter with proper indentation.
    
    Features:
    - Removes internal keys (prefixed with _)
    - Properly indents lists and nested dicts
    - Preserves type information (strings, numbers, booleans)
    - Wraps with --- delimiters
    """
    # Remove internal keys (those starting with _)
    jekyll_metadata = {k: v for k, v in metadata.items() if not k.startswith("_")}

    yaml_body = yaml.safe_dump(
        jekyll_metadata,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )

    if not yaml_body.endswith("\n"):
        yaml_body += "\n"

    return f"---\n{yaml_body}---"


def write_jekyll_markdown(slug: str, metadata: Dict) -> bool:
    """
    Write processed metadata + body as Jekyll .md file in _photos/.
    Uses indented frontmatter formatting for better readability.
    """
    try:
        PHOTOS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        output_path = PHOTOS_OUTPUT_DIR / f"{slug}.md"
        
        # Create indented frontmatter
        frontmatter_str = format_frontmatter_indented(metadata)
        
        # Combine with body
        content = frontmatter_str + "\n\n" + metadata.get("_body", "")
        
        # Write file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.debug(f"Created: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write Jekyll markdown for {slug}: {e}")
        return False


# ============================================================================
# Main Pipeline
# ============================================================================

def main():
    """Main processing pipeline - orchestrates the complete workflow."""
    import argparse
    parser = argparse.ArgumentParser(description="Process research photos and generate GeoJSON.")
    parser.add_argument('-l', '--log', dest='loglevel', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set logging level (default: INFO)')
    parser.add_argument('-c', '--check', action='store_true', help='Run integrity checks across raw_data, _photos and generated assets')
    parser.add_argument('-C', '--clean', action='store_true', help='With --check, delete orphan files after a confirmation prompt')
    parser.add_argument('-y', '--yes', action='store_true', help='With --check --clean, skip cleanup confirmation prompt')
    parser.add_argument('-j', '--json', action='store_true', help='With --check, emit machine-readable JSON report')
    parser.add_argument('-w', '--strict-warnings', action='store_true', help='With --check, treat warnings as failure (returns -1, shell exit 255)')
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("geo", help="Generate GeoJSON only from all raw_data/*.md")
    subparsers.add_parser("all", help="Process all raw_data/*.md to _photos and regenerate GeoJSON")
    changed_parser = subparsers.add_parser("changed", help="Process only git-changed raw_data/*.md to _photos")
    changed_parser.add_argument("-p", "--prune", action="store_true", help="Remove stale _photos/*.md for deleted raw_data/*.md")
    args = parser.parse_args()

    loglevel = getattr(logging, args.loglevel.upper(), logging.INFO)
    global logger
    logger = setup_logging(loglevel)

    logger.info("Research Photo Processing Pipeline")
    logger.info(f"Raw data: {RAW_DATA_DIR}")
    logger.info(f"Output: {PHOTOS_OUTPUT_DIR}")

    if args.json and not args.check:
        parser.error("--json can only be used together with --check")

    if args.strict_warnings and not args.check:
        parser.error("--strict-warnings can only be used together with --check")

    if args.clean and not args.check:
        parser.error("--clean can only be used together with --check")

    if args.yes and not args.check:
        parser.error("--yes can only be used together with --check")

    if args.yes and not args.clean:
        parser.error("--yes can only be used together with --clean")

    if args.check and args.command:
        parser.error("--check cannot be combined with subcommands (geo/all/changed)")

    # Validate raw_data directory
    if not RAW_DATA_DIR.exists():
        logger.error(f"raw_data directory not found: {RAW_DATA_DIR}")
        return 2 if args.check else False

    if args.check:
        return run_check_mode(
            json_output=bool(args.json),
            strict_warnings=bool(args.strict_warnings),
            clean=bool(args.clean),
            auto_yes=bool(args.yes),
        )

    # Find all markdown files to process
    all_md_files = sorted(RAW_DATA_DIR.glob("*.md"))
    if not all_md_files:
        logger.warning("No .md files found in raw_data/")
        return False

    mode = args.command or "geo"
    logger.info(f"Mode: {mode}")

    if mode == "geo":
        geojson_metadata = collect_geojson_metadata(all_md_files)
        geo_stats = generate_geojson(geojson_metadata)
        logger.info(
            f"Summary mode=geo files={len(all_md_files)} geo_ok={geo_stats['ok']} "
            f"origins={geo_stats['origins']} fovs={geo_stats['fovs']} lov={geo_stats['lov']}"
        )
        return bool(geo_stats["ok"])

    if mode == "changed":
        changed_files, deleted_slugs = get_git_raw_data_changes()
        logger.info(
            f"Changed scope files={len(changed_files)} deleted={len(deleted_slugs)} prune={bool(getattr(args, 'prune', False))}"
        )

        success_count = 0
        for filepath in changed_files:
            metadata = process_post(filepath)
            if metadata:
                slug = slug_from_path(filepath)
                if write_jekyll_markdown(slug, metadata):
                    success_count += 1
                if loglevel == logging.DEBUG:
                    logger.debug(f"Processed file: {filepath.name}")

        pruned_count = 0
        if getattr(args, "prune", False):
            pruned_count = prune_deleted_photos(deleted_slugs)

        logger.info(
            f"Summary mode=changed changed_files={len(changed_files)} posts_written={success_count} pruned={pruned_count}"
        )
        return True

    # mode == "all"
    success_count = 0
    for filepath in all_md_files:
        metadata = process_post(filepath)
        if metadata:
            slug = slug_from_path(filepath)
            if write_jekyll_markdown(slug, metadata):
                success_count += 1
            if loglevel == logging.DEBUG:
                logger.debug(f"Processed file: {filepath.name}")

    geojson_metadata = collect_geojson_metadata(all_md_files)
    geo_stats = generate_geojson(geojson_metadata)

    logger.info(
        f"Summary mode=all files={len(all_md_files)} posts_written={success_count} "
        f"geo_ok={geo_stats['ok']} origins={geo_stats['origins']} fovs={geo_stats['fovs']} lov={geo_stats['lov']}"
    )

    return success_count > 0 and bool(geo_stats["ok"])


if __name__ == "__main__":
    result = main()
    if isinstance(result, int):
        exit(result)
    exit(0 if result else 1)
