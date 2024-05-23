
# 输出十六进制类型数组
def print_hex(bytes):
    l = [hex(int(i)) for i in bytes]
    print(" ".join(l))

def SetByteBit(byte,offset,value):
    if value == 1:
        mask = 1 << offset
        return (byte | mask)
    elif value == 0:
        mask = ~(1 << offset)
        return (byte & mask)
    else:
        return byte

def GetByteBit(byte,offset):
    return (byte & (1 << offset)) >> offset