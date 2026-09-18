"""
Geospatial validation for GeoJSON polygon submissions.

Validates:
- GeoJSON structure (type, coordinates)
- Polygon type
- Coordinate validity (lng/lat bounds)
- Ring closure
- Minimum vertices
- Maximum vertices (complexity limit)
- Maximum area (size limit)
- Geometry validity via Shapely

This is a pure validation module with no database access.
"""

from typing import Any

from shapely.geometry import Polygon, shape
from shapely.validation import explain_validity

from app.core.exceptions import GeospatialValidationError

# Limits
MAX_VERTICES = 10000
MAX_AREA_SQ_DEGREES = 100.0  # ~roughly 100 sq degrees, very generous
MIN_VERTICES = 4  # Minimum for a closed triangle


def validate_geojson_geometry(geojson: dict[str, Any]) -> Polygon:
    """
    Validate a GeoJSON geometry object and return a Shapely Polygon.

    Args:
        geojson: A GeoJSON geometry dict with 'type' and 'coordinates'.

    Returns:
        A valid Shapely Polygon.

    Raises:
        GeospatialValidationError: If validation fails at any step.
    """
    # Step 1: Validate structure
    if not isinstance(geojson, dict):
        raise GeospatialValidationError("GeoJSON must be a JSON object")

    geom_type = geojson.get("type")
    coordinates = geojson.get("coordinates")

    if geom_type is None:
        raise GeospatialValidationError("Missing 'type' field in GeoJSON geometry")
    if coordinates is None:
        raise GeospatialValidationError("Missing 'coordinates' field in GeoJSON geometry")

    # Step 2: Validate polygon type
    if geom_type != "Polygon":
        raise GeospatialValidationError(
            f"Expected geometry type 'Polygon', got '{geom_type}'",
            detail={"received_type": geom_type},
        )

    # Step 3: Validate coordinates structure
    if not isinstance(coordinates, list) or len(coordinates) == 0:
        raise GeospatialValidationError("Polygon coordinates must be a non-empty array of rings")

    # Validate exterior ring
    exterior_ring = coordinates[0]
    if not isinstance(exterior_ring, list):
        raise GeospatialValidationError("Exterior ring must be an array of coordinate pairs")

    # Step 4: Validate vertex count
    if len(exterior_ring) < MIN_VERTICES:
        raise GeospatialValidationError(
            f"Polygon must have at least {MIN_VERTICES} coordinates "
            f"(including closing vertex), got {len(exterior_ring)}"
        )

    total_vertices = sum(len(ring) for ring in coordinates if isinstance(ring, list))
    if total_vertices > MAX_VERTICES:
        raise GeospatialValidationError(
            f"Polygon exceeds maximum vertex count of {MAX_VERTICES} "
            f"(has {total_vertices} vertices)"
        )

    # Step 5: Validate each coordinate pair
    for ring_idx, ring in enumerate(coordinates):
        if not isinstance(ring, list):
            raise GeospatialValidationError(f"Ring {ring_idx} must be an array of coordinate pairs")
        for coord_idx, coord in enumerate(ring):
            if not isinstance(coord, (list, tuple)) or len(coord) < 2:
                raise GeospatialValidationError(
                    f"Invalid coordinate at ring {ring_idx}, position {coord_idx}: "
                    f"expected [longitude, latitude]"
                )
            lng, lat = coord[0], coord[1]
            if not isinstance(lng, (int, float)) or not isinstance(lat, (int, float)):
                raise GeospatialValidationError(
                    f"Coordinate values must be numbers at ring {ring_idx}, position {coord_idx}"
                )
            if lng < -180 or lng > 180:
                raise GeospatialValidationError(
                    f"Longitude {lng} out of range [-180, 180] "
                    f"at ring {ring_idx}, position {coord_idx}"
                )
            if lat < -90 or lat > 90:
                raise GeospatialValidationError(
                    f"Latitude {lat} out of range [-90, 90] "
                    f"at ring {ring_idx}, position {coord_idx}"
                )

    # Step 6: Validate ring closure
    for ring_idx, ring in enumerate(coordinates):
        if isinstance(ring, list) and len(ring) >= 2:
            if ring[0] != ring[-1]:
                raise GeospatialValidationError(
                    f"Ring {ring_idx} is not closed: first coordinate must equal last coordinate"
                )

    # Step 7: Build Shapely geometry and validate
    try:
        polygon = shape(geojson)
    except Exception as e:
        raise GeospatialValidationError(f"Failed to parse geometry: {e}")

    if not isinstance(polygon, Polygon):
        raise GeospatialValidationError("Parsed geometry is not a Polygon")

    if not polygon.is_valid:
        reason = explain_validity(polygon)
        raise GeospatialValidationError(f"Invalid polygon geometry: {reason}")

    if polygon.is_empty:
        raise GeospatialValidationError("Polygon geometry is empty")

    # Step 8: Validate area bounds
    area = polygon.area  # In square degrees (approximate)
    if area > MAX_AREA_SQ_DEGREES:
        raise GeospatialValidationError(
            f"Polygon area ({area:.2f} sq degrees) exceeds maximum "
            f"allowed ({MAX_AREA_SQ_DEGREES} sq degrees)"
        )

    return polygon
