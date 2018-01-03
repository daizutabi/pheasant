import base64
import io
import os
import tempfile

try:
    import win32com.client
    from PIL import Image
except ImportError:
    pass

apps = {}


def get_application(name):
    if name not in apps:
        obj = win32com.client.gencache.EnsureDispatch(f'{name}.Application')
        apps[name] = obj
    return apps[name]


def quit(name):
    if name in apps:
        apps[name].Quit()
        del apps[name]


def extract_shape_with_title(obj, collection_name):
    """
    Extract shapes with title from all collection of a object.

    Parameters
    ----------
    obj : Office object (Presentation or Workbook)

    Yield
    ------
    shape : Shape
    """
    def extract(shape):
        if shape.Title:
            yield shape
        try:
            for shape in shape.GroupItems:
                yield from extract(shape)
        except Exception:
            pass

    for element in getattr(obj, collection_name):
        for shape in element.Shapes:
            yield from extract(shape)


def export_shape(shape, path=None):
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
    with tempfile.TemporaryDirectory() as tmpdir:
        emf_path = os.path.join(tmpdir, 'tmp.emf')
        shape.Export(emf_path, 5)  # To EMF. ppShapeFormatEMF is 5.
        with Image.open(emf_path) as image:
            if path is not None:
                image.save(path)
            else:
                in_mem_file = io.BytesIO()
                image.save(in_mem_file, format='PNG')
                in_mem_file.seek(0)
                img_bytes = in_mem_file.read()
                base64_encoded_result_bytes = base64.b64encode(img_bytes)
                return base64_encoded_result_bytes.decode('ascii')
