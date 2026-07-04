"""
dd_obs_websockets.py

Thin wrapper around obsws-python that exposes the same simple method names
obscountdowntimer.py already calls:

    set_source_visibility(scene_name, source_name, visible)
    set_text(source_name, text)
    set_source_transform(transform_dict)

Requires: pip install obsws-python --break-system-packages
Requires: OBS > Tools > WebSocket Server Settings > "Enable WebSocket server" checked.
"""

import obsws_python as obs
from obs_config import OBS_WS_HOST, OBS_WS_PORT, OBS_WS_PASSWORD, DEFAULT_SCENE


class OBSWebsocketsManager:
    def __init__(self, host=OBS_WS_HOST, port=OBS_WS_PORT, password=OBS_WS_PASSWORD,
                 default_scene=DEFAULT_SCENE):
        self.default_scene = default_scene
        self.client = obs.ReqClient(host=host, port=port, password=password, timeout=3)
        version = self.client.get_version()
        print(f"[OBS] Connected — OBS {version.obs_version}, WebSocket {version.obs_web_socket_version}")

    def _find_group_containing(self, scene_name, source_name):
        """Sources nested inside a Group aren't visible to GetSceneItemId on the
        parent scene - OBS treats each Group as its own mini-scene. So if a
        direct lookup fails, walk the scene's items, find any Groups, and
        search inside each one for the source."""
        try:
            items = self.client.get_scene_item_list(scene_name).scene_items
        except Exception:
            return None

        for item in items:
            if item.get("isGroup"):
                group_name = item.get("sourceName")
                try:
                    group_items = self.client.get_group_scene_item_list(group_name).scene_items
                except Exception:
                    continue
                if any(gi.get("sourceName") == source_name for gi in group_items):
                    return group_name
        return None

    def _get_scene_item_id(self, scene_name, source_name):
        # Try a direct lookup first.
        try:
            resp = self.client.get_scene_item_id(scene_name, source_name)
            return scene_name, resp.scene_item_id
        except Exception:
            pass

        # Not found directly - maybe it's nested inside a group in that scene.
        group_name = self._find_group_containing(scene_name, source_name)
        if group_name:
            try:
                resp = self.client.get_scene_item_id(group_name, source_name)
                return group_name, resp.scene_item_id
            except Exception as e:
                print(f"[OBS] Found '{source_name}' in group '{group_name}' but couldn't get its ID: {e}")
                return None, None

        print(f"[OBS] Couldn't find '{source_name}' in scene '{scene_name}' or any of its groups")
        return None, None

    def set_source_visibility(self, scene_name, source_name, visible):
        effective_scene, item_id = self._get_scene_item_id(scene_name, source_name)
        if item_id is None:
            return
        try:
            self.client.set_scene_item_enabled(effective_scene, item_id, visible)
        except Exception as e:
            print(f"[OBS] Couldn't set visibility for '{source_name}': {e}")

    def set_text(self, source_name, text):
        # Text (GDI+/FreeType2) sources are inputs, not scene items,
        # so this doesn't need a scene name at all.
        try:
            self.client.set_input_settings(source_name, {"text": text}, True)
        except Exception as e:
            print(f"[OBS] Couldn't set text for '{source_name}': {e}")

    def set_source_transform(self, transform, scene_name=None, source_name=None):
        # obscountdowntimer.py calls this once for the text source and once
        # for the background, passing source_name explicitly for the latter.
        scene_name = scene_name or self.default_scene
        source_name = source_name or "??? Timer Text - Seconds ???"
        effective_scene, item_id = self._get_scene_item_id(scene_name, source_name)
        if item_id is None:
            return
        try:
            self.client.set_scene_item_transform(effective_scene, item_id, transform)
        except Exception as e:
            print(f"[OBS] Couldn't set transform for '{source_name}': {e}")
