"""
pest_map.py — Mapping of detected pest classes to actionable farming suggestions.
Covers all 12 classes present in data/data.yaml.
"""

# ---------------------------------------------------------------------------
# Master mapping: class name (lowercase) → list of recommendations
# ---------------------------------------------------------------------------
PEST_SOLUTION_MAP: dict[str, list[str]] = {
    "ants": [
        "Apply diatomaceous earth around plant bases to create a physical barrier.",
        "Use boric acid bait stations away from edible parts.",
        "Remove aphid colonies that ants may be farming — treat aphids first.",
        "Spray diluted orange-peel extract (d-limonene) around entry points.",
    ],
    "bees": [
        "Bees are generally beneficial pollinators — avoid pesticide use.",
        "If a hive is present near crops, contact a local beekeeper for safe relocation.",
        "Plant bee-repelling herbs (mint, eucalyptus) around sensitive areas if needed.",
    ],
    "beetles": [
        "Apply Imidacloprid (systemic insecticide) as a soil drench or foliar spray.",
        "Hand-pick adult beetles during early morning and drop in soapy water.",
        "Use neem oil (Azadirachtin) spray at 2–3 mL/litre every 7 days.",
        "Introduce natural predators such as ground beetles and parasitic wasps.",
        "Rotate crops annually to break the beetle life cycle.",
    ],
    "caterpillars": [
        "Apply Bacillus thuringiensis (Bt) spray — a biological, crop-safe insecticide.",
        "Use spinosad-based insecticides for heavy infestations.",
        "Hand-pick egg masses and young larvae from the undersides of leaves.",
        "Install pheromone traps to monitor and reduce moth populations.",
        "Encourage natural predators: birds, parasitic wasps, and ground beetles.",
    ],
    "earthworms": [
        "Earthworms are highly beneficial — do NOT use pesticides against them.",
        "Their presence indicates healthy soil; focus on preserving organic matter.",
        "If overabundant in containers, improve drainage to reduce moisture.",
    ],
    "earwigs": [
        "Set up cardboard traps moistened with soy sauce/fish oil — collect and dispose daily.",
        "Apply diatomaceous earth around the base of plants.",
        "Remove garden debris, mulch, and dense ground cover where earwigs shelter.",
        "Use iron phosphate-based baits (safe for pets and wildlife).",
    ],
    "grasshoppers": [
        "Apply Nosema locustae (biological control) to bait grasshoppers early in season.",
        "Use kaolin clay spray to deter feeding on crops.",
        "Till soil in autumn to expose egg pods to predators and cold.",
        "Install floating row covers to protect vulnerable seedlings.",
        "Encourage natural predators: birds, robber flies, and blister beetles.",
    ],
    "moths": [
        "Install pheromone traps to reduce adult moth populations and monitor pressure.",
        "Apply Bacillus thuringiensis (Bt) targeting caterpillar (larval) stage.",
        "Use UV/black-light traps at night to attract and capture adult moths.",
        "Spray pyrethrin-based insecticide as a last resort for severe infestations.",
    ],
    "slugs": [
        "Apply iron phosphate pellets (Sluggo) — effective and safe for wildlife.",
        "Scatter crushed eggshells or copper tape around vulnerable plants.",
        "Set beer traps at soil level: slugs are attracted and drown.",
        "Reduce irrigation frequency to limit soil moisture that slugs prefer.",
        "Hand-pick at night using a torch; dispose in salt or soapy water.",
    ],
    "snails": [
        "Use iron phosphate-based bait (Ferramol) around plants.",
        "Create copper tape barriers around raised beds and containers.",
        "Hand-pick during night or early morning after rain.",
        "Introduce natural predators such as hedgehogs and ground beetles.",
        "Reduce dense mulch layers where snails hide during the day.",
    ],
    "wasps": [
        "Parasitic wasps are beneficial — check if they are pest-hunting before acting.",
        "For aggressive colonies near workers, use commercial wasp-freeze spray at dusk.",
        "Hang fake wasp nests (decoys) to deter colony establishment.",
        "Seal cracks and crevices in farm structures to prevent nesting.",
        "Avoid sweet food waste near crops that attracts foraging wasps.",
    ],
    "weevils": [
        "Apply Imidacloprid or Chlorpyrifos as a soil drench for larval control.",
        "Use neem oil spray (2–3 mL/litre) every 7–10 days on foliage.",
        "Introduce entomopathogenic nematodes (Steinernema or Heterorhabditis) to soil.",
        "Shake plants over a white cloth in the morning — adults are slow and fall off.",
        "Store harvested grain with diatomaceous earth to prevent storage weevils.",
    ],
}

# ---------------------------------------------------------------------------
# Severity thresholds mapped to urgency labels
# ---------------------------------------------------------------------------
_SEVERITY_THRESHOLDS = [
    (0.85, "🔴 High"),
    (0.60, "🟡 Medium"),
    (0.00, "🟢 Low"),
]


def get_suggestions(class_name: str) -> list[str]:
    """
    Return a list of suggestions for a given pest class name.

    Args:
        class_name: Detected pest class (case-insensitive).

    Returns:
        List of suggestion strings. Returns a generic tip if class not found.
    """
    key = class_name.strip().lower()
    return PEST_SOLUTION_MAP.get(
        key,
        [
            f"No specific recommendation found for '{class_name}'.",
            "Consult a local agricultural extension officer for guidance.",
        ],
    )


def severity_label(confidence: float) -> str:
    """
    Return a human-readable severity label based on detection confidence.

    Args:
        confidence: Model confidence score [0, 1].

    Returns:
        Severity label string.
    """
    for threshold, label in _SEVERITY_THRESHOLDS:
        if confidence >= threshold:
            return label
    return "🟢 Low"


def get_full_pest_info(class_name: str, confidence: float) -> dict:
    """
    Return a complete pest info dictionary for a single detection.

    Args:
        class_name: Detected pest class name.
        confidence: Model confidence score.

    Returns:
        Dict with pest, confidence, severity, and suggestions.
    """
    return {
        "pest": class_name,
        "confidence": round(float(confidence), 4),
        "severity": severity_label(confidence),
        "suggestions": get_suggestions(class_name),
    }
