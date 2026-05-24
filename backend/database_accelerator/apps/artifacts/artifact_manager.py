import json
import os
from datetime import datetime


class ArtifactManager:
    def register_artifact(self, registry, name, path, artifact_type='file'):
        registry[name] = {
            'path': path,
            'type': artifact_type,
            'registered_at': datetime.now().isoformat(),
            'version': registry.get(name, {}).get('version', 0) + 1,
        }
        return registry

    def export_artifact(self, artifact_path, content):
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        mode = 'wb' if isinstance(content, bytes) else 'w'
        kwargs = {} if isinstance(content, bytes) else {'encoding': 'utf-8'}
        with open(artifact_path, mode, **kwargs) as handle:
            handle.write(content)
        return artifact_path

    def validate_artifact(self, artifact_path):
        return os.path.exists(artifact_path) and os.path.getsize(artifact_path) > 0

    def track_versions(self, artifact_registry_path, artifact_registry):
        with open(artifact_registry_path, 'w', encoding='utf-8') as handle:
            json.dump(artifact_registry, handle, indent=2)
        return artifact_registry_path


artifact_manager = ArtifactManager()
