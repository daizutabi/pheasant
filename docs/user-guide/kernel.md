# Kernel

## IJavascript

~~~bash terminal
$ conda install jupyter
$ conda install nodejs==8.9.3
$ npm install -g ijavascript
$ ijsinstall
~~~

~~~
```javascript
console.log("Hello, IJavascript!")
```
~~~

## IJulia

~~~julia
julia> using Pkg
julia> Pkg.add("IJulia")
~~~

~~~
```julia
println("Hello, IJulia!")
```
~~~


## Kernel list

Mapping a language to kernel names can be obtained as a dictionary by `kernels.kernel_names` property:

```python
from pheasant.renderers.jupyter.kernel import kernels
kernels.kernel_names
```
