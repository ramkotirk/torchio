import warnings
from typing import Union, Sequence, Dict

import torch
import numpy as np
from torchvision.transforms import Compose as PyTorchCompose

from ...data.subject import Subject
from .. import Transform
from . import RandomTransform


TypeTransformsDict = Union[Dict[Transform, float], Sequence[Transform]]


class Compose(Transform):
    """Compose several transforms together.

    Args:
        transforms: Sequence of instances of
            :class:`~torchio.transforms.Transform`.
        p: Probability that this transform will be applied.

    .. note::
        This is a thin wrapper of :class:`torchvision.transforms.Compose`.
    """
    def __init__(self, transforms: Sequence[Transform], p: float = 1):
        super().__init__(p=p)
        if not transforms:
            raise ValueError('The list of transforms is empty')
        for transform in transforms:
            if not callable(transform):
                message = (
                    'One or more of the objects passed to the Compose transform'
                    f' are not callable: "{transform}"'
                )
                raise TypeError(message)
        self.transform = PyTorchCompose(transforms)
        self.transforms = self.transform.transforms

    def __len__(self):
        return len(self.transforms)

    def __getitem__(self, index) -> Transform:
        return self.transforms[index]

    def __repr__(self) -> str:
        return self.transform.__repr__()

    def apply_transform(self, subject: Subject) -> Subject:
        return self.transform(subject)

    def is_invertible(self) -> bool:
        return all(t.is_invertible() for t in self.transforms)

    def inverse(self) -> Transform:
        transforms = []
        for transform in self.transforms:
            if transform.is_invertible():
                transforms.append(transform.inverse())
            else:
                message = f'Skipping {transform.name} as it is not invertible'
                warnings.warn(message, RuntimeWarning)
        transforms.reverse()
        return Compose(transforms)


class OneOf(RandomTransform):
    """Apply only one of the given transforms.

    Args:
        transforms: Dictionary with instances of
            :class:`~torchio.transforms.Transform` as keys and
            probabilities as values. Probabilities are normalized so they sum
            to one. If a sequence is given, the same probability will be
            assigned to each transform.
        p: Probability that this transform will be applied.

    Example:
        >>> import torchio as tio
        >>> colin = tio.datasets.Colin27()
        >>> transforms_dict = {
        ...     tio.RandomAffine(): 0.75,
        ...     tio.RandomElasticDeformation(): 0.25,
        ... }  # Using 3 and 1 as probabilities would have the same effect
        >>> transform = tio.OneOf(transforms_dict)
        >>> transformed = transform(colin)

    """
    def __init__(
            self,
            transforms: TypeTransformsDict,
            p: float = 1,
            ):
        super().__init__(p=p)
        self.transforms_dict = self._get_transforms_dict(transforms)

    def apply_transform(self, subject: Subject) -> Subject:
        weights = torch.Tensor(list(self.transforms_dict.values()))
        index = torch.multinomial(weights, 1)
        transforms = list(self.transforms_dict.keys())
        transform = transforms[index]
        transformed = transform(subject)
        return transformed

    def _get_transforms_dict(
            self,
            transforms: TypeTransformsDict,
            ) -> Dict[Transform, float]:
        if isinstance(transforms, dict):
            transforms_dict = dict(transforms)
            self._normalize_probabilities(transforms_dict)
        else:
            try:
                p = 1 / len(transforms)
            except TypeError as e:
                message = (
                    'Transforms argument must be a dictionary or a sequence,'
                    f' not {type(transforms)}'
                )
                raise ValueError(message) from e
            transforms_dict = {transform: p for transform in transforms}
        for transform in transforms_dict:
            if not isinstance(transform, Transform):
                message = (
                    'All keys in transform_dict must be instances of'
                    f'torchio.Transform, not "{type(transform)}"'
                )
                raise ValueError(message)
        return transforms_dict

    @staticmethod
    def _normalize_probabilities(
            transforms_dict: Dict[Transform, float],
            ) -> None:
        probabilities = np.array(list(transforms_dict.values()), dtype=float)
        if np.any(probabilities < 0):
            message = (
                'Probabilities must be greater or equal to zero,'
                f' not "{probabilities}"'
            )
            raise ValueError(message)
        if np.all(probabilities == 0):
            message = (
                'At least one probability must be greater than zero,'
                f' but they are "{probabilities}"'
            )
            raise ValueError(message)
        for transform, probability in transforms_dict.items():
            transforms_dict[transform] = probability / probabilities.sum()
