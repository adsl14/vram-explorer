import os


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


# Swizzle algorithm
def swizzle_algorithm(texture, width, height):
    # Swizzle algorithm
    swizzled = ""
    indexes = []

    if width > height:
        square = width
    else:
        square = height

    for i in range(0, square):
        for j in range(0, square):

            index = cal_z_order(j, i)

            if len(texture) > (index * 4):
                swizzled = swizzled + "0x{:02x}".format(texture[index * 4]).replace('0x', '')
                indexes.append(index * 4)

                if len(texture) > (index * 4 + 1):
                    swizzled = swizzled + "0x{:02x}".format(texture[index * 4 + 1]).replace('0x', '')
                    indexes.append(index * 4 + 1)

                    if len(texture) > (index * 4 + 2):
                        swizzled = swizzled + "0x{:02x}".format(texture[index * 4 + 2]).replace('0x', '')
                        indexes.append(index * 4 + 2)

                        if len(texture) > (index * 4 + 3):
                            swizzled = swizzled + "0x{:02x}".format(texture[index * 4 + 3]).replace('0x', '')
                            indexes.append(index * 4 + 3)

    # End Swizzle algorithm

    # Fix the colors and orientation
    swizzled = fix_orientation_image(swizzled, width, height)
    swizzled = invert_bytes(swizzled)

    return swizzled, indexes


def unswizzle_algorithm(texture_unswizzled, texture_swizzled, indexes, width, height):
    # Invert the colors and orientation
    texture_swizzled = invert_bytes(texture_swizzled.hex())
    texture_swizzled = bytes.fromhex(fix_orientation_image(texture_swizzled, width, height))

    with open("tempSwizzle", mode="wb") as temp_file:
        temp_file.write(texture_unswizzled)

    j = 0
    with open("tempSwizzle", mode="rb+") as temp_file:
        for i in indexes:
            temp_file.seek(i)
            temp_file.write(texture_swizzled[j].to_bytes(1, 'big'))
            j = j + 1

        temp_file.seek(0)
        texture_unswizzled = temp_file.read()

    os.remove("tempSwizzle")

    return texture_unswizzled


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
