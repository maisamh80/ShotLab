from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageOps


def _palette(
    image: Image.Image,
    count: int = 5,
) -> tuple[list[str], list[float]]:
    sample = image.copy()
    sample.thumbnail((360, 240), Image.Resampling.LANCZOS)
    quantized = sample.quantize(colors=count, method=Image.Quantize.MEDIANCUT)
    raw_palette = quantized.getpalette() or []
    colors = quantized.getcolors(maxcolors=256) or []
    entries = sorted(colors, reverse=True)[:count]
    total_pixels = sum(pixel_count for pixel_count, _ in entries)
    result: list[str] = []
    percentages: list[float] = []
    for pixel_count, index in entries:
        start = index * 3
        rgb = raw_palette[start : start + 3]
        if len(rgb) == 3:
            result.append("#{:02X}{:02X}{:02X}".format(*rgb))
            percentages.append(
                round(pixel_count * 100.0 / max(total_pixels, 1), 1)
            )
    if percentages:
        percentages[0] = round(
            percentages[0] + 100.0 - sum(percentages),
            1,
        )
    while len(result) < count:
        result.append(result[-1] if result else "#000000")
        percentages.append(0.0)
    return result, percentages


def analyze_image(
    path: Path,
) -> dict[str, list[str] | list[float]]:
    """Extract only the objective five-color palette requested by the user."""
    with Image.open(path) as source:
        image = source.convert("RGB")
        colors, percentages = _palette(image)
    return {
        "dominant_colors": colors,
        "color_percentages": percentages,
    }


def aggregate_palette(
    analyses: list[dict],
    count: int = 5,
) -> list[str]:
    """Build a coverage-weighted mood palette from several frame palettes."""
    target_count = max(1, int(count))
    weighted_colors: dict[tuple[int, int, int], float] = {}
    for analysis in analyses:
        colors = list(analysis.get("dominant_colors", []))
        percentages = list(analysis.get("color_percentages", []))
        fallback_weight = 100.0 / max(len(colors), 1)
        for index, value in enumerate(colors):
            clean = str(value).strip().lstrip("#")
            if len(clean) != 6:
                continue
            try:
                rgb = tuple(
                    int(clean[offset : offset + 2], 16)
                    for offset in (0, 2, 4)
                )
            except ValueError:
                continue
            try:
                weight = (
                    float(percentages[index])
                    if index < len(percentages)
                    else fallback_weight
                )
            except (TypeError, ValueError):
                weight = fallback_weight
            if weight <= 0:
                continue
            weighted_colors[rgb] = weighted_colors.get(rgb, 0.0) + weight

    if not weighted_colors:
        return []

    points = list(weighted_colors.items())
    cluster_count = min(target_count, len(points))
    centroids: list[tuple[float, float, float]] = [
        tuple(
            float(channel)
            for channel in max(points, key=lambda item: item[1])[0]
        )
    ]

    def distance_squared(
        first: tuple[int, int, int] | tuple[float, float, float],
        second: tuple[float, float, float],
    ) -> float:
        return sum(
            (float(left) - right) ** 2
            for left, right in zip(first, second)
        )

    while len(centroids) < cluster_count:
        candidate, _weight = max(
            points,
            key=lambda item: (
                item[1]
                * min(
                    distance_squared(item[0], centroid)
                    for centroid in centroids
                )
            ),
        )
        new_centroid = tuple(float(channel) for channel in candidate)
        if new_centroid in centroids:
            break
        centroids.append(new_centroid)

    cluster_weights: list[float] = [0.0 for _ in centroids]
    for _iteration in range(18):
        channel_totals = [
            [0.0, 0.0, 0.0]
            for _ in centroids
        ]
        cluster_weights = [0.0 for _ in centroids]
        for rgb, weight in points:
            cluster_index = min(
                range(len(centroids)),
                key=lambda index: distance_squared(
                    rgb,
                    centroids[index],
                ),
            )
            cluster_weights[cluster_index] += weight
            for channel_index, channel in enumerate(rgb):
                channel_totals[cluster_index][channel_index] += (
                    channel * weight
                )

        updated = []
        for index, centroid in enumerate(centroids):
            if cluster_weights[index] <= 0:
                updated.append(centroid)
                continue
            updated.append(
                tuple(
                    total / cluster_weights[index]
                    for total in channel_totals[index]
                )
            )
        if all(
            distance_squared(previous, current) < 0.25
            for previous, current in zip(centroids, updated)
        ):
            centroids = updated
            break
        centroids = updated

    ordered = sorted(
        zip(cluster_weights, centroids),
        key=lambda item: item[0],
        reverse=True,
    )
    result = [
        "#{:02X}{:02X}{:02X}".format(
            *(
                max(0, min(255, round(channel)))
                for channel in centroid
            )
        )
        for weight, centroid in ordered
        if weight > 0
    ]
    while result and len(result) < target_count:
        result.append(result[-1])
    return result[:target_count]


def make_thumbnail(source_path: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as source:
        image = source.convert("RGB")
        image.thumbnail((480, 270), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (480, 270), "#080a0b")
        x = (canvas.width - image.width) // 2
        y = (canvas.height - image.height) // 2
        canvas.paste(image, (x, y))
        canvas.save(destination, "JPEG", quality=88, optimize=True)


def prepare_imported_image(
    source_path: Path,
    destination: Path,
    max_width: int | None,
) -> None:
    """Normalize a user-imported still to an RGB JPEG at the selected size."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        if max_width is not None and image.width > max_width:
            height = max(1, round(image.height * max_width / image.width))
            image = image.resize(
                (max_width, height),
                Image.Resampling.LANCZOS,
            )
        image.save(destination, "JPEG", quality=94, optimize=True)


def _hex_to_lab(value: str) -> tuple[float, float, float]:
    clean = value.strip().lstrip("#")
    if len(clean) != 6:
        raise ValueError(f"Invalid HEX color: {value}")
    try:
        red, green, blue = (
            int(clean[index : index + 2], 16) / 255.0
            for index in (0, 2, 4)
        )
    except ValueError as exc:
        raise ValueError(f"Invalid HEX color: {value}") from exc

    def linear(channel: float) -> float:
        return (
            channel / 12.92
            if channel <= 0.04045
            else ((channel + 0.055) / 1.055) ** 2.4
        )

    red, green, blue = linear(red), linear(green), linear(blue)
    x = (red * 0.4124564 + green * 0.3575761 + blue * 0.1804375) / 0.95047
    y = red * 0.2126729 + green * 0.7151522 + blue * 0.0721750
    z = (red * 0.0193339 + green * 0.1191920 + blue * 0.9503041) / 1.08883

    def pivot(component: float) -> float:
        return (
            component ** (1.0 / 3.0)
            if component > 0.008856
            else 7.787 * component + 16.0 / 116.0
        )

    x, y, z = pivot(x), pivot(y), pivot(z)
    return 116.0 * y - 16.0, 500.0 * (x - y), 200.0 * (y - z)


def color_distance(first: str, second: str) -> float:
    """Return a perceptual CIE76 distance between two HEX colors."""
    try:
        first_lab = _hex_to_lab(first)
        second_lab = _hex_to_lab(second)
    except ValueError:
        return math.inf
    return math.sqrt(
        sum(
            (first_component - second_component) ** 2
            for first_component, second_component in zip(
                first_lab,
                second_lab,
            )
        )
    )


def closest_palette_distance(colors: list[str], target: str) -> float:
    if not colors:
        return math.inf
    return min(color_distance(color, target) for color in colors)
