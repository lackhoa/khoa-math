from khoa_math import *

# Set up the environment
form = MathObj()
form.kattach(None)
type_ = MathObj(role='type', value={MathType.PL_FORMULA}, parent=None, queue=None)
type_.kattach(form)
