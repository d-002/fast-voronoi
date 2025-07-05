# this file is very crappy code, but is a small hack used to be able to import
# fast_voronoi from the testing directory

import sys, importlib.util, os.path
path = os.path.dirname(__file__)
if path.endswith('testing'): path = os.path.dirname(path)
path = os.path.join(path, 'fast_voronoi/__init__.py')
spec = importlib.util.spec_from_file_location("fast_voronoi", path)
module = importlib.util.module_from_spec(spec)
sys.modules["fast_voronoi"] = module
spec.loader.exec_module(module)
