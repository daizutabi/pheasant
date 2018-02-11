import base64
import io
import os
import tempfile

from .common import get_application

try:
    from PIL import Image
except ImportError:
    pass


def open(path):
    app = get_application('PowerPoint')

    for prs in app.Presentations:
        if prs.FullName == path:
            return prs
    else:
        prs = app.Presentations.Open(path, ReadOnly=True, Untitled=False,
                                     WithWindow=False)
        return prs


def export_shape(shape, path=None, format='png'):
    """
    Export shape as a image

    `shape` is temporarily saved as EMF image, then it's converted to the
    desired format according to `path` extention.

    Parameters
    ----------
    shape : Shape
        Shape to be exported.
    path : str
        File name of the image.
    """
    tmpdir = tempfile.TemporaryDirectory()
    emf_path = os.path.join(tmpdir.name, 'tmp.emf')
    shape.Export(emf_path, 5)  # To EMF. ppShapeFormatEMF is 5.
    with Image.open(emf_path) as image:
        if path is not None:
            image.save(path)
        else:
            in_mem_file = io.BytesIO()
            image.save(in_mem_file, format=format)
            in_mem_file.seek(0)
            img_bytes = in_mem_file.read()
            base64_encoded_result_bytes = base64.b64encode(img_bytes)
            return base64_encoded_result_bytes.decode('ascii')
