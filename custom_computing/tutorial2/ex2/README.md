## What are the types for conjugate, append and triangle?
Conjugate:
- Take P as `P: X ~ X` and Q as `Q: X ~ Y`
- Then `P \ Q : Y ~ Y`

Append:
- `append m n: <<X>_m, <X>_n> ~ <X>_{m+n}`

Triangle:
- `triangle n R: <X>_n ~ <X>_n`
- This is because, despite each parallel level having up to `n` compositions, since compositions don't change the type, each level is simply `X ~ X`
