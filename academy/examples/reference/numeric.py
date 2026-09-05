"""範圍截斷的參考契約。"""
def clamp(value, low, high):
    if low > high:
        raise ValueError('low exceeds high')
    return max(low, min(value, high))
