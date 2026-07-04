"""
Quick sanity check: just connects to OBS and prints its version + scene list.
Run this BEFORE running obscountdowntimer.py to confirm the connection works.

    python3 test_obs_connection.py
"""

from dd_obs_websockets import OBSWebsocketsManager

if __name__ == "__main__":
    print("Attempting to connect to OBS...")
    manager = OBSWebsocketsManager()

    scenes = manager.client.get_scene_list()
    print("\nScenes found in OBS:")
    for scene in scenes.scenes:
        print(f"  - {scene['sceneName']}")

    print("\nIf you see your scene names above, the connection works.")
