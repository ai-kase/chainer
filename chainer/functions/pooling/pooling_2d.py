from chainer.backends import cuda
from chainer import function_node
from chainer.utils import collections_abc
from chainer.utils import conv
from chainer.utils import type_check

if cuda.cudnn_enabled:
    cudnn = cuda.cudnn


def _pair(x):
    if isinstance(x, collections_abc.Iterable):
        return x
    return x, x


class Pooling2D(function_node.FunctionNode):

    """Base class of pooling function over a set of 2d planes."""

    def __init__(self, ksize, stride=None, pad=0, cover_all=True,
                 return_indices=False):
        if stride is None:
            stride = ksize

        self.kh, self.kw = _pair(ksize)
        self.sy, self.sx = _pair(stride)
        self.ph, self.pw = _pair(pad)

        self.cover_all = cover_all
        self.return_indices = return_indices

        self._used_cudnn = False
        self._cudnn_inputs = None
        self._cudnn_outputs = None

    def check_type_forward(self, in_types):
        type_check.expect(
            in_types.size() == 1,
            in_types[0].dtype.kind == 'f',
            in_types[0].ndim == 4
        )

    def forward_gpu(self, x):
        self.retain_inputs((0,))
        self._used_cudnn = True

        # Implementation using cudnn
        x = x[0]
        n, c, h, w = x.shape
        y_h = conv.get_conv_outsize(
            h, self.kh, self.sy, self.ph, self.cover_all)
        assert y_h > 0, 'Height in the output should be positive.'
        y_w = conv.get_conv_outsize(
            w, self.kw, self.sx, self.pw, self.cover_all)
        assert y_w > 0, 'Width in the output should be positive.'
        y = cuda.cupy.empty((n, c, y_h, y_w), dtype=x.dtype)

<<<<<<< HEAD
        handle = cudnn.get_handle()
        pool_desc = self.create_pool_desc()
        x_desc = cudnn.create_tensor_descriptor(x)
        y_desc = cudnn.create_tensor_descriptor(y)

        oz_dtype = 'd' if x.dtype == 'd' else 'f'
        one = numpy.array(1, dtype=oz_dtype).ctypes
        zero = numpy.array(0, dtype=oz_dtype).ctypes
        libcudnn.poolingForward(
            handle, pool_desc.value, one.data, x_desc.value,
            x.data.ptr, zero.data, y_desc.value, y.data.ptr)
        self._cudnn_inputs = (x,)
        self._cudnn_outputs = (y,)
=======
        cudnn.pooling_forward(
            x, y,
            (self.kh, self.kw), (self.sy, self.sx), (self.ph, self.pw),
            self._get_pool_mode())

        self.retain_outputs((0,))
>>>>>>> dbdcee87466e4866c7daa70a057ae0896671bca3
        return y,

    def backward_gpu(self, x, gy):
        # Implementation using cudnn
<<<<<<< HEAD
        x = cuda.cupy.ascontiguousarray(x[0])
        y = self._cudnn_outputs[0]
        handle = cudnn.get_handle()
        pool_desc = self.create_pool_desc()

        gy = cuda.cupy.ascontiguousarray(gy[0])

        x_desc = cudnn.create_tensor_descriptor(x)
        y_desc = cudnn.create_tensor_descriptor(gy)

        oz_dtype = 'd' if x.dtype == 'd' else 'f'
        one = numpy.array(1, dtype=oz_dtype).ctypes
        zero = numpy.array(0, dtype=oz_dtype).ctypes
        gx = cuda.cupy.empty_like(x)
        libcudnn.poolingBackward(
            handle, pool_desc.value, one.data, y_desc.value,
            y.data.ptr, y_desc.value, gy.data.ptr, x_desc.value,
            x.data.ptr, zero.data, x_desc.value, gx.data.ptr)
=======
        x = x[0]
        y = self.output_data[0]
        gx = cudnn.pooling_backward(
            x, y, gy[0],
            (self.kh, self.kw), (self.sy, self.sx), (self.ph, self.pw),
            self._get_pool_mode())
>>>>>>> dbdcee87466e4866c7daa70a057ae0896671bca3
        return gx,

    def _get_pool_mode(self):
        raise NotImplementedError()
