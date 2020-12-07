from typing import List, Dict

from .transform import Transform
from .. import Image


class IntensityTransform(Transform):
    """Transform that modifies voxel intensities only."""
    def get_images_dict(self, sample) -> Dict[str, Image]:
        return sample.get_images_dict(intensity_only=True, include=self.include, exclude=self.exclude)

    def get_images(self, sample) -> List[Image]:
        return sample.get_images(intensity_only=True, include=self.include, exclude=self.exclude)

    def arguments_are_dict(self) -> bool:
        """Check if main arguments are dict.

        Return True if the type of all attributes specified in the
        :attr:`args_names` have ``dict`` type.
        """
        args = [getattr(self, name) for name in self.args_names]
        are_dict = [isinstance(arg, dict) for arg in args]
        if all(are_dict):
            return True
        elif not any(are_dict):
            return False
        else:
            message = 'Either all or none of the arguments must be dicts'
            raise ValueError(message)
