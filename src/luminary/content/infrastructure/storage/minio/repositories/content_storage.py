from luminary_files.infrastructure.storage.minio.repositories.file_storage import (
    MinioFileStorage,
)

from luminary.content.application.interfaces.repositories.content_storage import (
    IContentStorage,
)


# NOTE: Since interfaces and implementation are the same for now, no reason to duplicate
class MinioContentStorage(MinioFileStorage, IContentStorage): ...
