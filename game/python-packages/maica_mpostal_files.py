# -*- coding: utf-8 -*-
import os
import shutil
import uuid


def path_is_within(file_path, root_path):
    if not file_path or not root_path:
        return False

    try:
        candidate = os.path.realpath(os.path.abspath(os.path.normpath(file_path)))
        root = os.path.realpath(os.path.abspath(os.path.normpath(root_path)))
        relative = os.path.relpath(candidate, root)
    except (TypeError, ValueError, OSError):
        return False

    return (
        relative != os.curdir
        and relative != os.pardir
        and not relative.startswith(os.pardir + os.sep)
    )


class MPostalAttachmentStore(object):
    """Owns original MPostal attachments while a reply is pending."""

    def __init__(self, root_path):
        if not root_path:
            raise ValueError("MPostal attachment store requires a root path")
        self.root_path = os.path.realpath(
            os.path.abspath(os.path.normpath(root_path))
        )

    @staticmethod
    def _display_path(file_path):
        return os.path.normpath(file_path).replace('\\', '/')

    def ensure(self):
        if os.path.isdir(self.root_path):
            return
        if os.path.exists(self.root_path):
            raise IOError("MPostal attachment store path is not a directory")
        try:
            os.makedirs(self.root_path)
        except OSError:
            if not os.path.isdir(self.root_path):
                raise

    def contains(self, file_path):
        return path_is_within(file_path, self.root_path)

    def stage(self, source_path):
        if not source_path:
            return None
        if not os.path.isfile(source_path):
            raise IOError("MPostal attachment source does not exist")
        if self.contains(source_path):
            return self._display_path(source_path)

        self.ensure()
        extension = os.path.splitext(source_path)[1] or '.mms'
        destination = os.path.join(
            self.root_path,
            uuid.uuid4().hex + extension,
        )
        try:
            shutil.move(source_path, destination)
        except Exception:
            if os.path.exists(source_path) and os.path.isfile(destination):
                try:
                    os.remove(destination)
                except Exception:
                    pass
            raise
        return self._display_path(destination)

    def restore(self, managed_path, destination_path):
        if not self.contains(managed_path):
            raise ValueError("Refusing to restore an unmanaged MPostal attachment")
        if not os.path.isfile(managed_path):
            return False
        if os.path.exists(destination_path):
            raise IOError("MPostal attachment restore destination already exists")
        shutil.move(managed_path, destination_path)
        return True

    def delete(self, managed_path):
        if not managed_path:
            return True
        if not self.contains(managed_path):
            return False
        if not os.path.exists(managed_path):
            return True
        if not os.path.isfile(managed_path):
            return False
        os.remove(managed_path)
        return True
