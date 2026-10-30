# Example status

Runnable examples:

- `maquinas.ronin`: PUSFRE compatibility acceptance case.
- `maquinas_ces.ronin`: CES extension.
- `pesca.ronin`: five-agent baseline.
- `degeneracy_active.ronin`: narrow Omega range, K-alpha degeneracy active.
- `degeneracy_inactive.ronin`: Omega range above three full orders.

The supplied RONIN 1.1 document also sketches NeuralScaling (46 models) and
FamaFrench (720 monthly observations), but both examples contain ellipses
instead of complete records. The NeuralScaling excerpt also supplies phi and
psi values above 1 although the same document's validator constrains both to
[0,1]. No synthetic observations are substituted here: those examples remain
templates until the source dataset and a resolution of the range conflict are
provided.
