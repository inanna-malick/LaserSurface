class struct(): pass


# if true, the obj output will only contain supporting geometry, not faces. For ease of visual debugging
output_skeleton_only=False



'''INITIAL VALUES / DIMENSIONS'''
dimensions = struct()
dimensions.brass_pin_slot_length=0.15
dimensions.pushback_increment = 0.05
dimensions.scale = 3
dimensions.tab_width = 0.5
dimensions.large_text_size = 0.5
dimensions.small_text_size = 0.3



'''CONSTRAINTS'''
constraints = struct()
constraints.min_tab_edge_len = 1
constraints.min_corner_edge_length = 1

constraints.MIN_AROUND_VERTEX_POINT_DIST = 2

# minimum angle between triangle edge and edge between that edge and tab
# NOTE: THIS WILL FUCK WITH POINTY GEOMETRY IF TOO HIGH, check first
constraints.EDGE_TABEDGE_MIN_ANGLE = 5

# minimum angle between tab edge and another tab edge
constraints.MIN_TAB_TAB_ANGLE = 6

#max angle between tab edge and edge
constraints.TAB_EDGE_MAX_ANGLE = 40



'''OUTPUT COLORS'''
colors = struct()
colors.annotations = 256
colors.perforations = 2
colors.cuts = 1

