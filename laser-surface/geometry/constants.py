

class struct(): pass


# PUSHBACK

# -minimum tab edge length, used as a constraint on pushback operation
TAB_EDGE_MIN_LEN = 1.0

# minimum angle between triangle edge and edge between that edge and tab. Constraint on pushback
# NOTE: THIS WILL FUCK WITH POINTY GEOMETRY IF TOO HIGH, check first
EDGE_TABEDGE_MIN_ANGLE = 5

# minimum angle between tab edge and another tab edge
MIN_TAB_TAB_ANGLE = 6

#max angle between tab edge and edge
TAB_EDGE_MAX_ANGLE = 40




MIN_AROUND_VERTEX_POINT_DIST = 2


SLOT_LEN=0.15

#CORNER_GROMMETS = False


TAB_WIDTH=0.5


# -increment tab vertices are pushed back by in ObjVertex pushback rounds
PUSH_BACK_INCREMENT = 0.05

MIN_CORNER_EDGE_LEN = 1

# -scaling applied to vertices when they are read
SCALE = 4


# -distance between parallel edge and tab lines
EDGE_OUT_LEN = 1.0


# - center annotation height, based on edge len
CENTER_ANNOTATION_HEIGHT = EDGE_OUT_LEN * (12.0/15.0)

# edge annotation height, based on edge len
EDGE_ANNOTATION_HEIGHT = EDGE_OUT_LEN * (8.0/15.0)


# if true, the obj output will only contain supporting geometry, not faces. For ease of visual debugging
SKELETAL_OBJ_OUTPUT=True



    
colors = struct()
colors.annotations = 256
colors.perforations = 2
colors.cuts = 1




#etc (unused)
# offset to compensate for folding non-zero thickness materials near corners. currently unused
MATERIAL_THICKNESS = 0.02
# - determines if rectangles are drawn inside faces for use with paper clips
DRAW_PAPERCLIP_RECTANGLES = False

