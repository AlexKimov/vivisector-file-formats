import struct
import sys
import os
import argparse
from pathlib import Path

# ----------------------------------------------------------------------
# RLE decompression function (from previous answer)
# ----------------------------------------------------------------------
def rle_decompress(src: bytes, dst: bytearray, element_size: int) -> None:
    """
    Decompress RLE data.
    :param src: Compressed bytes.
    :param dst: Mutable bytearray to receive decompressed data.
    :param element_size: Size of each output element (1, 2, or 4).
    """
    src_pos = 0
    dst_pos = 0
    src_len = len(src)

    while src_pos < src_len:
        cl = src[src_pos]
        src_pos += 1

        if cl <= 0x7F:
            # Literal run: copy (cl + 1) elements
            literal_elements = cl + 1
            bytes_to_copy = literal_elements * element_size
            dst[dst_pos:dst_pos + bytes_to_copy] = src[src_pos:src_pos + bytes_to_copy]
            src_pos += bytes_to_copy
            dst_pos += bytes_to_copy

        elif cl >= 0x81:
            # Repeated run: length = 1 - (signed)cl
            signed_cl = cl - 256 if cl >= 128 else cl
            run_elements = 1 - signed_cl
            bytes_to_write = run_elements * element_size

            # Read the value to repeat (little‑endian)
            value_bytes = src[src_pos:src_pos + element_size]
            src_pos += element_size

            # Write the value repeatedly
            for i in range(run_elements):
                dst[dst_pos + i * element_size : dst_pos + (i + 1) * element_size] = value_bytes
            dst_pos += bytes_to_write

        # cl == 0x80 is ignored; just consume the byte


# ----------------------------------------------------------------------
# File reader
# ----------------------------------------------------------------------
def read_uint(f):
    """Read a 32‑bit little‑endian unsigned integer from the file."""
    return struct.unpack('<I', f.read(4))[0]


def process_file(filename):
    with open(filename, 'rb') as f:
        # Header
        unknown1 = read_uint(f)
        num = read_uint(f)
        print(f"num = {num}")

        data = [read_uint(f) for _ in range(num)]
        unknown2 = read_uint(f)
        unknown3 = read_uint(f)
        unknown4 = read_uint(f)
        unknown5 = read_uint(f)

        # Ensure we have at least 6 entries (for data[0]..data[5])
        if num < 6:
            print("Warning: data array has fewer than 6 elements; some blocks may be missing.")

        # ------------------------------------------------------------------
        # Block for data[0]
        # ------------------------------------------------------------------
        if data[0] != 0:
            size1 = read_uint(f)
            rle_data1 = f.read(size1)   
            
            dst1 = bytearray(262144 * 2)
            rle_decompress(rle_data1, dst1, 2)
        else:
            data1 = None

        # ------------------------------------------------------------------
        # Block for data[1] – two RLE sub‑blocks
        # ------------------------------------------------------------------
        if data[1] != 0:
            size2 = read_uint(f)
            rle_data2 = f.read(size2)      # RLE compressed, element size 2
            size3 = read_uint(f)
            rle_data3 = f.read(size3)      # RLE compressed, element size 1

            # Decompress using the element counts from the template comments
            # 262144 elements of size 2 → 524288 bytes
            dst2 = bytearray(262144 * 2)
            rle_decompress(rle_data2, dst2, 2)

            # 262144 elements of size 1 → 262144 bytes
            dst3 = bytearray(262144 * 1)
            rle_decompress(rle_data3, dst3, 1)

            print(f"data[1]: size2={size2}, size3={size3} -> decompressed 2×262144 bytes")
        else:
            rle_data2 = rle_data3 = None
            dst2 = dst3 = None

        # ------------------------------------------------------------------
        # Block for data[2]
        # ------------------------------------------------------------------
        if data[2] != 0:
            size4 = read_uint(f)
            rle_data4 = f.read(size4)      # RLE compressed, element size 2
            # 1048576 elements of size 2 → 2097152 bytes
            dst4 = bytearray(1048576 * 2)
            rle_decompress(rle_data4, dst4, 2)
            print(f"data[2]: size4={size4} -> decompressed 2×1048576 bytes")
        else:
            rle_data4 = None
            dst4 = None

        # ------------------------------------------------------------------
        # Always present block
        # ------------------------------------------------------------------
        size5 = read_uint(f)
        rle_data5 = f.read(size5)          # RLE compressed, element size 2
        dst5 = bytearray(1048576 * 2)
        rle_decompress(rle_data5, dst5, 2)
        print(f"size5: {size5} -> decompressed 2×1048576 bytes")

        # ------------------------------------------------------------------
        # Block for data[3]
        # ------------------------------------------------------------------
        if data[3] != 0:
            size6 = read_uint(f)
            rle_data6 = f.read(size6)      # RLE compressed, element size 1
            dst6 = bytearray(262144 * 1)
            rle_decompress(rle_data6, dst6, 1)
            print(f"data[3]: size6={size6} -> decompressed 262144 bytes")
        else:
            rle_data6 = None
            dst6 = None

        # ------------------------------------------------------------------
        # Block for data[4]
        # ------------------------------------------------------------------
        if data[4] != 0:
            size7 = read_uint(f)
            rle_data7 = f.read(size7)      # RLE compressed, element size 2
            dst7 = bytearray(1048576 * 2)
            rle_decompress(rle_data7, dst7, 2)
            print(f"data[4]: size7={size7} -> decompressed 2×1048576 bytes")
        else:
            rle_data7 = None
            dst7 = None

        # ------------------------------------------------------------------
        # Block for data[5]
        # ------------------------------------------------------------------
        if data[5] != 0:
            size8 = read_uint(f)
            rle_data8 = f.read(size8)      # RLE compressed, element size 1
            dst8 = bytearray(262144 * 1)
            rle_decompress(rle_data8, dst8, 1)
            print(f"data[5]: size8={size8} -> decompressed 262144 bytes")
        else:
            rle_data8 = None
            dst8 = None

        # Return all blocks in a dictionary
        return {
            'unknown1': unknown1,
            'data': data,
            'unknown2': unknown2,
            'unknown3': unknown3,
            'unknown4': unknown4,
            'unknown5': unknown5,
            'data1': dst1,         
            'dst2': dst2,
            'dst3': dst3,
            'dst4': dst4,
            'dst5': dst5,
            'dst6': dst6,
            'dst7': dst7,
            'dst8': dst8,
        }


# ----------------------------------------------------------------------
# Command‑line interface and file saving
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Decompress Vivisector RLE game files."
    )
    parser.add_argument('input', help="Input file to process")
    parser.add_argument('-o', '--outdir', default='.',
                        help="Output directory (default: current directory)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file '{args.input}' not found.")
        sys.exit(1)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    base = input_path.stem

    try:
        blocks = process_file(args.input)
    except Exception as e:
        print(f"Error while processing file: {e}")
        sys.exit(1)

    saved_any = False
    for name in ['dst1', 'dst2', 'dst3', 'dst4', 'dst5', 'dst6', 'dst7', 'dst8']:
        data = blocks.get(name)
        if data is not None:
            out_file = outdir / f"{base}_{name}.raw"
            with open(out_file, 'wb') as f:
                f.write(data)
            print(f"Saved {out_file} ({len(data)} bytes)")
            saved_any = True

    if not saved_any:
        print("No data blocks were found.")
    else:
        print("All done.")


if __name__ == '__main__':
    main()