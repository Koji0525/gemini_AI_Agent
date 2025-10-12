#!/usr/bin/env python3
# バグのあるテストファイル

def broken_function():
    data = None
    return data.get('key')  # AttributeError!

if __name__ == "__main__":
    broken_function()
