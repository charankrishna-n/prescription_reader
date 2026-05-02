import sys
import pickle
import difflib

MEDICINES = [
    "augmentin", "enzoflam", "pantoprazole", "hexigel", "paracetamol",
    "amoxicillin", "metformin", "atorvastatin", "omeprazole", "cetirizine",
    "azithromycin", "ibuprofen", "aspirin", "metronidazole", "ciprofloxacin",
]


def load_model(model_path: str):
    """Load Keras model saved with Keras 3.x into a Keras 2.x environment."""
    import tensorflow as tf

    try:
        model = tf.keras.models.load_model(model_path, compile=False)
        return model
    except TypeError:
        pass

    import h5py
    import json
    import tensorflow.keras as keras

    # ── Rebuild architecture ─────────────────────────────────────────────────
    with h5py.File(model_path, "r") as f:
        raw_cfg = json.loads(f.attrs["model_config"])

    layers_cfg = raw_cfg["config"]["layers"]
    rebuilt = keras.Sequential()

    for lc in layers_cfg:
        cls_name = lc["class_name"]
        cfg = lc["config"]

        if cls_name == "InputLayer":
            rebuilt.add(keras.layers.InputLayer(input_shape=cfg["batch_shape"][1:]))
            continue

        layer_cls = getattr(keras.layers, cls_name)

        for bad_key in ("dtype", "quantization_config", "optional",
                        "module", "registered_name", "synchronized"):
            cfg.pop(bad_key, None)

        if isinstance(cfg.get("activation"), dict):
            cfg["activation"] = cfg["activation"].get("class_name", "linear")

        rebuilt.add(layer_cls.from_config(cfg))

    # ── Copy weights ─────────────────────────────────────────────────────────
    # h5 structure: model_weights/{layer_name}/sequential/{layer_name}/{w_name}
    with h5py.File(model_path, "r") as f:
        wg = f["model_weights"]
        for layer in rebuilt.layers:
            name = layer.name
            expected = layer.get_weights()
            if not expected or name not in wg:
                continue

            outer = wg[name]
            sub_keys = list(outer.keys())
            if not sub_keys:
                continue

            inner = outer[sub_keys[0]]   # e.g. "sequential"
            if name in inner:
                inner = inner[name]      # e.g. "conv2d"

            # Load all datasets from this group
            datasets = {k: inner[k][()] for k in inner.keys()
                        if hasattr(inner[k], "shape")}

            # Match each expected weight tensor by shape (order-safe)
            ordered = []
            used = set()
            for exp_w in expected:
                for k, arr in datasets.items():
                    if k not in used and arr.shape == exp_w.shape:
                        ordered.append(arr)
                        used.add(k)
                        break

            if len(ordered) == len(expected):
                layer.set_weights(ordered)

    return rebuilt


def load_labels(pkl_path: str) -> dict:
    """Load label_to_char_map.pkl with numpy._core compatibility shim."""
    import numpy
    import numpy.core.multiarray
    sys.modules.setdefault("numpy._core", numpy.core)
    sys.modules.setdefault("numpy._core.multiarray", numpy.core.multiarray)
    with open(pkl_path, "rb") as f:
        label_map = pickle.load(f)
    return {int(k): v for k, v in label_map.items()}


def clean_text(raw: str) -> str:
    """Lowercase, strip noise chars, fuzzy-match medicine names."""
    text = raw.lower().strip()
    cleaned_chars = [c for c in text if c.isalnum() or c == " "]
    text = "".join(cleaned_chars)

    words = text.split()
    corrected = []
    for word in words:
        if len(word) < 3:
            corrected.append(word)
            continue
        matches = difflib.get_close_matches(word, MEDICINES, n=1, cutoff=0.75)
        corrected.append(matches[0] if matches else word)

    return " ".join(corrected)
