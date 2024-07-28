from collections import defaultdict
from typing import Dict
from typing import List
from typing import Sequence
from typing import Tuple
from typing import Union

import numpy as np
import SimpleITK as sitk
import torch

from .. import RandomTransform
from ... import FourierTransform
from ... import IntensityTransform
from ....data.io import nib_to_sitk
from ....data.subject import Subject
from ....typing import TypeTripletFloat


class RandomMotion(RandomTransform, IntensityTransform, FourierTransform):
    r"""Add random MRI motion artifact.

    Magnetic resonance images suffer from motion artifacts when the subject
    moves during image acquisition. This transform follows
    `Shaw et al., 2019 <http://proceedings.mlr.press/v102/shaw19a.html>`_ to
    simulate motion artifacts for data augmentation.

    Args:
        axes: Tuple of integers or strings representing the axes along which
            the simulated movements will occur.
        degrees: Tuple :math:`(a, b)` defining the rotation range in degrees of
            the simulated movements. The rotation angles around each axis are
            :math:`(\theta_1, \theta_2, \theta_3)`,
            where :math:`\theta_i \sim \mathcal{U}(a, b)`.
            If only one value :math:`d` is provided,
            :math:`\theta_i \sim \mathcal{U}(-d, d)`.
            Larger values generate more distorted images.
        translation: Tuple :math:`(a, b)` defining the translation in mm of
            the simulated movements. The translations along each axis are
            :math:`(t_1, t_2, t_3)`,
            where :math:`t_i \sim \mathcal{U}(a, b)`.
            If only one value :math:`t` is provided,
            :math:`t_i \sim \mathcal{U}(-t, t)`.
            Larger values generate more distorted images.
        num_transforms: Number of simulated movements.
            Larger values generate more distorted images.
        image_interpolation: See :ref:`Interpolation`.
        **kwargs: See :class:`~torchio.transforms.Transform` for additional
            keyword arguments.

    .. warning:: Large numbers of movements lead to longer execution times for
        3D images.
    """

    def __init__(
        self,
        axes: Union[int, Tuple[int, ...], str, Tuple[str, ...]] = (0, 1, 2),
        degrees: Union[float, Tuple[float, float]] = 10,
        translation: Union[float, Tuple[float, float]] = 10,  # in mm
        num_transforms: int = 2,
        image_interpolation: str = 'linear',
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.axes = self.parse_axes(axes)
        self.degrees_range = self.parse_degrees(degrees)
        self.translation_range = self.parse_translation(translation)
        if num_transforms < 1 or not isinstance(num_transforms, int):
            message = (
                'Number of transforms must be a strictly positive natural'
                f'number, not {num_transforms}'
            )
            raise ValueError(message)
        self.num_transforms = num_transforms
        self.image_interpolation = self.parse_interpolation(
            image_interpolation,
        )

    def apply_transform(self, subject: Subject) -> Subject:
        axes = self.ensure_axes_indices(subject, self.axes)
        arguments: Dict[str, dict] = defaultdict(dict)
        for name, image in self.get_images_dict(subject).items():
            axis, times, degrees, translation = self.get_params(
                axes,
                self.degrees_range,
                self.translation_range,
                self.num_transforms,
                is_2d=image.is_2d(),
            )
            arguments['axis'][name] = axis
            arguments['times'][name] = times
            arguments['degrees'][name] = degrees
            arguments['translation'][name] = translation
            arguments['image_interpolation'][name] = self.image_interpolation
        transform = Motion(**self.add_include_exclude(arguments))
        transformed = transform(subject)
        assert isinstance(transformed, Subject)
        return transformed

    def get_params(
        self,
        axes: Tuple[int, ...],
        degrees_range: Tuple[float, float],
        translation_range: Tuple[float, float],
        num_transforms: int,
        perturbation: float = 0.3,
        is_2d: bool = False,
    ) -> Tuple[int, np.ndarray, np.ndarray, np.ndarray]:
        axis = axes[torch.randint(0, len(axes), (1,))]
        # If perturbation is 0, time intervals between movements are constant
        degrees_params = self.get_params_array(
            degrees_range,
            num_transforms,
        )
        translation_params = self.get_params_array(
            translation_range,
            num_transforms,
        )
        if is_2d:  # imagine sagittal (1, A, S)
            degrees_params[:, :-1] = 0  # rotate around Z axis only
            translation_params[:, 2] = 0  # translate in XY plane only
        step = 1 / (num_transforms + 1)
        times = torch.arange(0, 1, step)[1:]
        noise = torch.FloatTensor(num_transforms)
        noise.uniform_(-step * perturbation, step * perturbation)
        times += noise
        times_params = times.numpy()
        return axis, times_params, degrees_params, translation_params

    @staticmethod
    def get_params_array(nums_range: Tuple[float, float], num_transforms: int):
        tensor = torch.FloatTensor(num_transforms, 3).uniform_(*nums_range)
        return tensor.numpy()


class Motion(IntensityTransform, FourierTransform):
    r"""Add MRI motion artifact.

    Magnetic resonance images suffer from motion artifacts when the subject
    moves during image acquisition. This transform follows
    `Shaw et al., 2019 <http://proceedings.mlr.press/v102/shaw19a.html>`_ to
    simulate motion artifacts for data augmentation.

    Args:
        axis: Integer representing the axis along which the simulated movements
        degrees: Sequence of rotations :math:`(\theta_1, \theta_2, \theta_3)`.
        translation: Sequence of translations :math:`(t_1, t_2, t_3)` in mm.
        times: Sequence of times from 0 to 1 at which the motions happen.
        image_interpolation: See :ref:`Interpolation`.
        **kwargs: See :class:`~torchio.transforms.Transform` for additional
            keyword arguments.
    """

    def __init__(
        self,
        axis: Union[int, Dict[str, int]],
        degrees: Union[TypeTripletFloat, Dict[str, TypeTripletFloat]],
        translation: Union[TypeTripletFloat, Dict[str, TypeTripletFloat]],
        times: Union[Sequence[float], Dict[str, Sequence[float]]],
        image_interpolation: Union[
            Sequence[str], Dict[str, Sequence[str]]
        ],  # noqa: B950
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.axis = axis
        self.degrees = degrees
        self.translation = translation
        self.times = times
        self.image_interpolation = image_interpolation
        self.args_names = [
            'axis',
            'degrees',
            'translation',
            'times',
            'image_interpolation',
        ]

    def apply_transform(self, subject: Subject) -> Subject:
        axis = self.axis
        degrees = self.degrees
        translation = self.translation
        times = self.times
        image_interpolation = self.image_interpolation
        for image_name, image in self.get_images_dict(subject).items():
            if self.arguments_are_dict():
                assert isinstance(self.axis, dict)
                assert isinstance(self.degrees, dict)
                assert isinstance(self.translation, dict)
                assert isinstance(self.times, dict)
                assert isinstance(self.image_interpolation, dict)
                axis = self.axis[image_name]
                degrees = self.degrees[image_name]
                translation = self.translation[image_name]
                times = self.times[image_name]
                image_interpolation = self.image_interpolation[image_name]
            result_arrays = []
            for channel in image.data:
                sitk_image = nib_to_sitk(
                    channel[np.newaxis],
                    image.affine,
                    force_3d=True,
                )
                transforms = self.get_rigid_transforms(
                    np.asarray(degrees),
                    np.asarray(translation),
                    sitk_image,
                )
                assert isinstance(axis, int)
                assert isinstance(image_interpolation, str)
                transformed_channel = self.add_artifact(
                    sitk_image,
                    transforms,
                    np.asarray(times),
                    axis,
                    image_interpolation,
                )
                result_arrays.append(transformed_channel)
            result = np.stack(result_arrays)
            image.set_data(torch.as_tensor(result))
        return subject

    def get_rigid_transforms(
        self,
        degrees_params: np.ndarray,
        translation_params: np.ndarray,
        image: sitk.Image,
    ) -> List[sitk.Euler3DTransform]:
        center_ijk = np.array(image.GetSize()) / 2
        center_lps = image.TransformContinuousIndexToPhysicalPoint(center_ijk)
        ident_transform = sitk.Euler3DTransform()
        ident_transform.SetCenter(center_lps)
        transforms = [ident_transform]
        for degrees, translation in zip(degrees_params, translation_params):
            radians = np.radians(degrees).tolist()
            motion = sitk.Euler3DTransform()
            motion.SetCenter(center_lps)
            motion.SetRotation(*radians)
            motion.SetTranslation(translation.tolist())
            transforms.append(motion)
        return transforms

    def resample_images(
        self,
        image: sitk.Image,
        transforms: Sequence[sitk.Euler3DTransform],
        interpolation: str,
    ) -> List[sitk.Image]:
        floating = reference = image
        default_value = np.float64(sitk.GetArrayViewFromImage(image).min())
        interpolator = self.get_sitk_interpolator(interpolation)
        transforms = transforms[1:]  # first is identity
        images = [image]  # first is identity
        for transform in transforms:
            resampler = sitk.ResampleImageFilter()
            resampler.SetInterpolator(interpolator)
            resampler.SetReferenceImage(reference)
            resampler.SetOutputPixelType(sitk.sitkFloat32)
            resampler.SetDefaultPixelValue(default_value)
            resampler.SetTransform(transform)
            resampled = resampler.Execute(floating)
            images.append(resampled)
        return images

    @staticmethod
    def sort_spectra(spectra: List[torch.Tensor], times: np.ndarray):
        """Use original spectrum to fill the center of k-space."""
        num_spectra = len(spectra)
        if np.any(times > 0.5):
            index = np.where(times > 0.5)[0].min()
        else:
            index = num_spectra - 1
        spectra[0], spectra[index] = spectra[index], spectra[0]

    def add_artifact(
        self,
        image: sitk.Image,
        transforms: Sequence[sitk.Euler3DTransform],
        times: np.ndarray,
        axis: int,
        interpolation: str,
    ):
        images = self.resample_images(image, transforms, interpolation)
        spectra = []
        for image in images:
            array = sitk.GetArrayFromImage(image).transpose()  # sitk to np
            spectrum = self.fourier_transform(torch.from_numpy(array))
            spectra.append(spectrum)
        self.sort_spectra(spectra, times)
        result_spectrum = torch.empty_like(spectra[0])
        last_index = result_spectrum.shape[axis]
        indices = (last_index * times).astype(int).tolist()
        indices.append(last_index)
        ini = 0
        slices = [slice(None)] * len(result_spectrum.shape)
        for spectrum, fin in zip(spectra, indices):
            slices[axis] = slice(ini, fin)
            result_spectrum[slices] = spectrum[slices]
            ini = fin
        result_image = self.inv_fourier_transform(result_spectrum).real.float()
        return result_image
