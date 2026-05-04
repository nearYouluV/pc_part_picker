def extract_features(item: dict) -> dict:
    features_map = {}

    for group in item.get("feature_groups", []):

        for feature in group.get("features", []):
            name = feature.get("name_en")
            if name == 'Color' or 'Accessories' in name:
                continue

            values = feature.get("values_en")  or feature.get("values") # fallback to non-English values if English ones are not available

            if not values:
                continue
            if name == "memory_suffix":
                features_map[name] = feature.get("suffix_en")
            else:
                features_map[name] = values[0].get("value")

    return features_map



def split_features(features: dict, mapping: dict):
    mapped = {}
    other = {}

    mapping_values = set(mapping.values())

    for key, value in features.items():
        if key in mapping_values:
            mapped[key] = value
        else:
            other[key] = value

    return mapped, other