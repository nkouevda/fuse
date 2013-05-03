from fuse import *


inp = Bus(1) * 4 #Bus(4)#[Node(), Node(), Node(), Node()]#Bus(4)
bus1 = inp >> Bus(4)[:2].copy() + Bus(2)

print(inp[0] in bus1.input)
print(NODE_GRAPH)