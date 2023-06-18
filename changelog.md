# 0.0.4
Introduced geodata check in __init__.py. mapFunctions.py will only be imported if geopandas is present, and if loading of shapefiles is succesful.

# 0.0.5
- Updated use of Pandas DataFrame aggregation methods: only selecting numerical columns first.
- Added in idwMap to draw colorbar on ax explicitly.
