import os


# Credit to user aggsol from https://stackoverflow.com/questions/12157685/z-order-curve-coordinates, whose solution
# is based on http://graphics.stanford.edu/~seander/bithacks.html
def cal_z_order(x_pos, y_pos):
    masks = [int("0x55555555", base=16), int("0x33333333", base=16), int("0x0F0F0F0F", base=16),
             int("0x00FF00FF", base=16)]
    shifts = [1, 2, 4, 8]

    x = x_pos
    y = y_pos

    x = (x | (x << shifts[3])) & masks[3]
    x = (x | (x << shifts[2])) & masks[2]
    x = (x | (x << shifts[1])) & masks[1]
    x = (x | (x << shifts[0])) & masks[0]

    y = (y | (y << shifts[3])) & masks[3]
    y = (y | (y << shifts[2])) & masks[2]
    y = (y | (y << shifts[1])) & masks[1]
    y = (y | (y << shifts[0])) & masks[0]

    result = x | (y << 1)

    return result


# unswizzle algorithm
def unswizzle_algorithm(texture, width, height):

    # unSwizzle algorithm
    unswizzled = ""
    indexes = []

    if width > height:
        square = width
    else:
        square = height

    for j in range(0, square):
        for i in range(0, square):

            index = cal_z_order(i, j)

            if len(texture) > (index * 4):
                unswizzled = unswizzled + "0x{:02x}".format(texture[index * 4]).replace('0x', '')
                indexes.append(index * 4)

                if len(texture) > (index * 4 + 1):
                    unswizzled = unswizzled + "0x{:02x}".format(texture[index * 4 + 1]).replace('0x', '')
                    indexes.append(index * 4 + 1)

                    if len(texture) > (index * 4 + 2):
                        unswizzled = unswizzled + "0x{:02x}".format(texture[index * 4 + 2]).replace('0x', '')
                        indexes.append(index * 4 + 2)

                        if len(texture) > (index * 4 + 3):
                            unswizzled = unswizzled + "0x{:02x}".format(texture[index * 4 + 3]).replace('0x', '')
                            indexes.append(index * 4 + 3)

    # End unswizzle algorithm

    # Fix the orientation
    unswizzled = fix_orientation_image(unswizzled, width, height)

    # Fix the colors
    unswizzled = invert_bytes(unswizzled)

    return unswizzled, indexes


def swizzle_algorithm(texture_swizzled, texture_unswizzled, indexes, width, height):

    # Fix the orientation
    texture_unswizzled = invert_bytes(texture_unswizzled.hex())

    # Fix the colors
    texture_unswizzled = bytes.fromhex(fix_orientation_image(texture_unswizzled, width, height))

    with open("tempSwizzle", mode="wb") as temp_file:
        temp_file.write(texture_swizzled)

    j = 0
    with open("tempSwizzle", mode="rb+") as temp_file:
        for i in indexes:
            temp_file.seek(i)
            temp_file.write(texture_unswizzled[j].to_bytes(1, 'big'))
            j = j + 1

        temp_file.seek(0)
        texture_swizzled = temp_file.read()

    os.remove("tempSwizzle")

    return texture_swizzled


def fix_orientation_image(image_data, width, height):
    oriented_image = ""
    width_image_array = width * 4 * 2
    for j in range(height - 1, -1, -1):
        index_start = width * 4 * 2 * j
        index_end = index_start + width_image_array
        oriented_image = oriented_image + image_data[index_start:index_end]

    return oriented_image


def invert_bytes(image_data):
    image_colored_correctly = ""
    for i in range(0, len(image_data), 8):
        bytes4 = image_data[i:i + 8]
        if len(bytes4) == 8:
            new_bytes = bytes4[6] + bytes4[7] + bytes4[4] + bytes4[5] + bytes4[2] + bytes4[3] + bytes4[0] + bytes4[1]
            image_colored_correctly = image_colored_correctly + new_bytes

    return image_colored_correctly
