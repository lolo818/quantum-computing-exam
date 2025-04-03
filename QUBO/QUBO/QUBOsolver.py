from QUBO.compal import compal
from QUBO.local import local
from QUBO.compal_gpu import compal_gpu
from QUBO.compal_new import compal_new


def processQUBO(model, mod, num_reads=3, num_sweeps=2000):
    if mod == "compal_new":
        return compal_new(model)
    if mod == "compal_gpu":
        return compal_gpu(model)
    if mod == "compal":
        return compal(model, num_reads, num_sweeps)
    if mod == "local":
        return local(model, num_reads, num_sweeps)
