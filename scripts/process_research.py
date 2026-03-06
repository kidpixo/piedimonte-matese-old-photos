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
from typing import Any, Dict, List, Optional, Tuple
import yaml
import json

try:
    import frontmatter
    from PIL import Image
    import geopandas as gpd
    from shapely.geometry import Point, Polygon, LineString
    import pandas as pd
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
DATA_DIR = ASSETS_DIR / "data"
VARIANTS_DIR = IMAGES_DIR / "variants"
VARIANTS_THUMBS_DIR = THUMBS_DIR / "variants"

# Image processing
THUMBNAIL_SIZE = (150, 150)
THUMBNAIL_QUALITY = 85
IMAGE_QUALITY = 90
MAX_IMAGE_WIDTH = 2000
RGB_BACKGROUND_COLOR = (255, 255, 255)
IMAGE_MODES_WITH_ALPHA = ("RGBA", "LA", "P")

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
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


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
        
        logger.info(f"✓ Optimized: {input_path.name} → {output_path}")
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
        
        logger.info(f"✓ Thumbnail: {output_path}")
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


def extract_coords_from_location(location_data: dict) -> Dict:
    """Extract all coordinate key-value pairs from location dict."""
    return dict(location_data) if isinstance(location_data, dict) else {}


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


def add_geojson_to_location(location_data: dict) -> dict:
    """Add GeoJSON geometry strings to the location dict."""
    if not location_data or not isinstance(location_data, dict):
        return location_data
    coords = extract_coords_from_location(location_data)
    # Validate origin is present
    if not validate_coordinates(coords, "origin"):
        logger.warning("  Cannot generate GeoJSON: missing origin coordinates")
        return location_data
    # Create origin_geojson
    lat_origin = float(coords["latitude_origin"])
    lon_origin = float(coords["longitude_origin"])
    origin_geom = create_geojson_point(lat_origin, lon_origin)
    location_data["origin_geojson"] = json.dumps(origin_geom)
    # Create fov_geojson and line_of_sight_geojson if vertices present
    if validate_coordinates(coords, "vertices"):
        lat_left = float(coords["latitude_vertex_left"])
        lon_left = float(coords["longitude_vertex_left"])
        lat_right = float(coords["latitude_vertex_right"])
        lon_right = float(coords["longitude_vertex_right"])
        fov_geom = create_geojson_polygon(lat_origin, lon_origin, lat_left, lon_left, lat_right, lon_right)
        location_data["fov_geojson"] = json.dumps(fov_geom)
        if is_numeric_coordinate(coords.get("latitude_boresight")) and is_numeric_coordinate(coords.get("longitude_boresight")):
            lat_bs = float(coords["latitude_boresight"])
            lon_bs = float(coords["longitude_boresight"])
        else:
            lat_bs, lon_bs = calculate_boresight_point(lat_left, lon_left, lat_right, lon_right)
        los_geom = create_geojson_linestring(lat_origin, lon_origin, lat_bs, lon_bs)
        location_data["line_of_sight_geojson"] = json.dumps(los_geom)
    return location_data


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


def process_location_data(metadata: Dict) -> None:
    location_data = metadata.get("location")
    if not location_data:
        return
    coords = extract_coords_from_location(location_data)
    if validate_coordinates(coords, "origin"):
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
    metadata["location"] = add_geojson_to_location(location_data)


def process_post(filepath: pathlib.Path) -> Optional[Dict]:
    """Process a single .md file through the complete pipeline.
    
    Pipeline:
    1. Read markdown with frontmatter
    2. Validate required fields
    3. Optimize images (primary + variants)
    4. Extract coordinates and generate GeoJSON
    5. Return processed metadata
    """
    logger.info(f"\nProcessing: {filepath.name}")
    
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
    process_location_data(metadata)
    
    # Step 5: Store markdown body for later output
    metadata["_body"] = post.content
    
    logger.info(f"✓ Successfully processed: {slug}")
    return metadata


# ============================================================================
# GeoJSON Generation
# ============================================================================

def generate_geojson(all_metadata: List[Dict]) -> bool:
    """
    Aggregate all processed photos into GeoJSON files using geopandas.
    Follows the pattern from convert_photos_coords.py:
    - photos_origin.geojson (Point features)
    - photos_fov.geojson (Polygon features)
    """
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        origins_data = []
        fovs_data = []
        
        for metadata in all_metadata:
            if metadata.get("_origin"):
                origins_data.append({
                    "title": metadata.get("title", ""),
                    "date": str(metadata.get("date", "")),
                    "labels": ",".join(metadata.get("labels", [])),
                    "geometry": metadata["_origin"],
                })
            
            if metadata.get("_fov"):
                fovs_data.append({
                    "title": metadata.get("title", ""),
                    "date": str(metadata.get("date", "")),
                    "geometry": metadata["_fov"],
                })
        
        if not origins_data and not fovs_data:
            logger.warning("No valid location data to generate GeoJSON")
            return False
        
        # Write origins GeoJSON (Point features)
        if origins_data:
            origins_gdf = gpd.GeoDataFrame(origins_data, crs="EPSG:4326")
            origins_path = DATA_DIR / "photos_origin.geojson"
            origins_gdf.to_file(origins_path, driver="GeoJSON")
            logger.info(f"✓ Generated: {origins_path} ({len(origins_gdf)} points)")
        
        # Write FOV GeoJSON (Polygon features)
        if fovs_data:
            fovs_gdf = gpd.GeoDataFrame(fovs_data, crs="EPSG:4326")
            fovs_path = DATA_DIR / "photos_fov.geojson"
            fovs_gdf.to_file(fovs_path, driver="GeoJSON")
            logger.info(f"✓ Generated: {fovs_path} ({len(fovs_gdf)} polygons)")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate GeoJSON: {e}")
        return False


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
        
        logger.info(f"✓ Created: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write Jekyll markdown for {slug}: {e}")
        return False


# ============================================================================
# Main Pipeline
# ============================================================================

def main():
    """Main processing pipeline - orchestrates the complete workflow."""
    logger.info("=" * 70)
    logger.info("Research Photo Processing Pipeline")
    logger.info("=" * 70)
    logger.info(f"Raw data: {RAW_DATA_DIR}")
    logger.info(f"Output: {PHOTOS_OUTPUT_DIR}")
    
    # Validate raw_data directory
    if not RAW_DATA_DIR.exists():
        logger.error(f"raw_data directory not found: {RAW_DATA_DIR}")
        return False
    
    # Find all markdown files to process
    md_files = list(RAW_DATA_DIR.glob("*.md"))
    if not md_files:
        logger.warning("No .md files found in raw_data/")
        return False
    
    logger.info(f"\nFound {len(md_files)} .md files to process\n")
    
    # Process each markdown file
    processed_metadata = []
    success_count = 0
    
    for filepath in sorted(md_files):
        metadata = process_post(filepath)
        if metadata:
            processed_metadata.append(metadata)
            
            # Write processed file to Jekyll format
            slug = slug_from_path(filepath)
            if write_jekyll_markdown(slug, metadata):
                success_count += 1
    
    # Aggregate all geometries into GeoJSON files
    if processed_metadata:
        generate_geojson(processed_metadata)
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info(f"✓ Processing complete: {success_count}/{len(md_files)} files processed")
    logger.info("=" * 70)
    
    return success_count > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
