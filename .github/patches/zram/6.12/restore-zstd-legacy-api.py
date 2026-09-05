#!/usr/bin/env python3
"""Restore the legacy zstd dictionary/advanced API removed by the
zstd-1.5.7.patch upgrade, so drivers/block/zram/backend_zstd.c (which
still calls zstd_custom_mem / zstd_cdict / zstd_ddict / etc.) keeps
compiling.

Usage:
    restore-zstd-legacy-api.py <zstd.h> <zstd_compress_module.c> <zstd_decompress_module.c>
"""
import sys


def insert_after(path, marker, snippet):
    with open(path) as fh:
        content = fh.read()
    if marker not in content:
        raise SystemExit(f"::error::marker not found in {path}: {marker!r}")
    idx = content.index(marker) + len(marker)
    content = content[:idx] + snippet + content[idx:]
    with open(path, "w") as fh:
        fh.write(content)


def insert_before(path, marker, snippet):
    with open(path) as fh:
        content = fh.read()
    if marker not in content:
        raise SystemExit(f"::error::marker not found in {path}: {marker!r}")
    idx = content.index(marker)
    content = content[:idx] + snippet + content[idx:]
    with open(path, "w") as fh:
        fh.write(content)


def main():
    if len(sys.argv) != 4:
        raise SystemExit(f"usage: {sys.argv[0]} <zstd.h> <zstd_compress_module.c> <zstd_decompress_module.c>")

    zstd_h, compress_mod, decompress_mod = sys.argv[1:4]

    with open(zstd_h) as fh:
        if "zstd_create_cdict_byreference" in fh.read():
            print("  legacy dictionary API already present, skipping")
            return

    # ---- include/linux/zstd.h ----

    insert_before(zstd_h, "/* ======   Parameter Selection   ====== */", """/**
 * zstd_default_clevel() - default compression level
 *
 * Return: Default compression level.
 */
int zstd_default_clevel(void);

/**
 * struct zstd_custom_mem - custom memory allocation
 */
typedef ZSTD_customMem zstd_custom_mem;

/**
 * struct zstd_dict_load_method - Dictionary load method.
 * See zstd_lib.h.
 */
typedef ZSTD_dictLoadMethod_e zstd_dict_load_method;

/**
 * struct zstd_dict_content_type - Dictionary context type.
 * See zstd_lib.h.
 */
typedef ZSTD_dictContentType_e zstd_dict_content_type;

""")

    insert_after(zstd_h, "zstd_parameters zstd_get_params(int level,\n\tunsigned long long estimated_src_size);\n", """
/**
 * zstd_get_cparams() - returns zstd_compression_parameters for selected level
 * @level:              The compression level
 * @estimated_src_size: The estimated source size to compress or 0
 *                      if unknown.
 * @dict_size:          Dictionary size.
 *
 * Return:              The selected zstd_compression_parameters.
 */
zstd_compression_parameters zstd_get_cparams(int level,
\tunsigned long long estimated_src_size, size_t dict_size);
""")

    insert_after(zstd_h, "zstd_cctx *zstd_init_cctx(void *workspace, size_t workspace_size);\n", """
/**
 * zstd_create_cctx_advanced() - Create compression context
 * @custom_mem:   Custom allocator.
 *
 * Return:        NULL on error, pointer to compression context otherwise.
 */
zstd_cctx *zstd_create_cctx_advanced(zstd_custom_mem custom_mem);

/**
 * zstd_free_cctx() - Free compression context
 * @cdict:        Pointer to compression context.
 *
 * Return:        Always 0.
 */
size_t zstd_free_cctx(zstd_cctx* cctx);

/**
 * struct zstd_cdict - Compression dictionary.
 * See zstd_lib.h.
 */
typedef ZSTD_CDict zstd_cdict;

/**
 * zstd_create_cdict_byreference() - Create compression dictionary
 * @dict:              Pointer to dictionary buffer.
 * @dict_size:         Size of the dictionary buffer.
 * @cparams:           Compression parameters.
 * @custom_mem:        Memory allocator.
 *
 * Note, this uses @dict by reference (ZSTD_dlm_byRef), so it should be
 * free before zstd_cdict is destroyed.
 *
 * Return:             NULL on error, pointer to compression dictionary
 *                     otherwise.
 */
zstd_cdict *zstd_create_cdict_byreference(const void *dict, size_t dict_size,
\t\t\t\t\t  zstd_compression_parameters cparams,
\t\t\t\t\t  zstd_custom_mem custom_mem);

/**
 * zstd_free_cdict() - Free compression dictionary
 * @cdict:        Pointer to compression dictionary.
 *
 * Return:        Always 0.
 */
size_t zstd_free_cdict(zstd_cdict* cdict);

/**
 * zstd_compress_using_cdict() - compress src into dst using a dictionary
 * @cctx:         The context. Must have been initialized with zstd_init_cctx().
 * @dst:          The buffer to compress src into.
 * @dst_capacity: The size of the destination buffer.
 * @src:          The data to compress.
 * @src_size:     The size of the data to compress.
 * @cdict:        The dictionary to be used.
 *
 * Return:        The compressed size or an error, which can be checked using
 *                zstd_is_error().
 */
size_t zstd_compress_using_cdict(zstd_cctx *cctx, void *dst,
\tsize_t dst_capacity, const void *src, size_t src_size,
\tconst zstd_cdict *cdict);
""")

    insert_after(zstd_h, "zstd_dctx *zstd_init_dctx(void *workspace, size_t workspace_size);\n", """
/**
 * zstd_create_dctx_advanced() - Create decompression context
 * @custom_mem:   Custom allocator.
 *
 * Return:        NULL on error, pointer to decompression context otherwise.
 */
zstd_dctx *zstd_create_dctx_advanced(zstd_custom_mem custom_mem);

/**
 * zstd_free_dctx() -- Free decompression context
 * @dctx:         Pointer to decompression context.
 * Return:        Always 0.
 */
size_t zstd_free_dctx(zstd_dctx *dctx);

/**
 * struct zstd_ddict - Decompression dictionary.
 * See zstd_lib.h.
 */
typedef ZSTD_DDict zstd_ddict;

/**
 * zstd_create_ddict_byreference() - Create decompression dictionary
 * @dict:              Pointer to dictionary buffer.
 * @dict_size:         Size of the dictionary buffer.
 * @custom_mem:        Memory allocator.
 *
 * Note, this uses @dict by reference (ZSTD_dlm_byRef), so it should be
 * free before zstd_ddict is destroyed.
 *
 * Return:             NULL on error, pointer to decompression dictionary
 *                     otherwise.
 */
zstd_ddict *zstd_create_ddict_byreference(const void *dict, size_t dict_size,
\t\t\t\t\t  zstd_custom_mem custom_mem);
/**
 * zstd_free_ddict() - Free decompression dictionary
 * @dict:         Pointer to the dictionary.
 *
 * Return:        Always 0.
 */
size_t zstd_free_ddict(zstd_ddict *ddict);

/**
 * zstd_decompress_using_ddict() - decompress src into dst using a dictionary
 * @dctx:         The decompression context.
 * @dst:          The buffer to decompress src into.
 * @dst_capacity: The size of the destination buffer.
 * @src:          The zstd compressed data to decompress.
 * @src_size:     The exact size of the data to decompress.
 * @ddict:        The dictionary to be used.
 *
 * Return:        The decompressed size or an error, which can be checked using
 *                zstd_is_error().
 */
size_t zstd_decompress_using_ddict(zstd_dctx *dctx,
\tvoid *dst, size_t dst_capacity, const void *src, size_t src_size,
\tconst zstd_ddict *ddict);
""")

    # ---- lib/zstd/zstd_compress_module.c ----

    insert_after(compress_mod, "EXPORT_SYMBOL(zstd_max_clevel);\n", """
int zstd_default_clevel(void)
{
\treturn ZSTD_defaultCLevel();
}
EXPORT_SYMBOL(zstd_default_clevel);
""")

    insert_after(compress_mod, "EXPORT_SYMBOL(zstd_get_params);\n", """
zstd_compression_parameters zstd_get_cparams(int level,
\tunsigned long long estimated_src_size, size_t dict_size)
{
\treturn ZSTD_getCParams(level, estimated_src_size, dict_size);
}
EXPORT_SYMBOL(zstd_get_cparams);
""")

    insert_after(compress_mod, "EXPORT_SYMBOL(zstd_init_cctx);\n", """
zstd_cctx *zstd_create_cctx_advanced(zstd_custom_mem custom_mem)
{
\treturn ZSTD_createCCtx_advanced(custom_mem);
}
EXPORT_SYMBOL(zstd_create_cctx_advanced);

size_t zstd_free_cctx(zstd_cctx *cctx)
{
\treturn ZSTD_freeCCtx(cctx);
}
EXPORT_SYMBOL(zstd_free_cctx);

zstd_cdict *zstd_create_cdict_byreference(const void *dict, size_t dict_size,
\t\t\t\t\t  zstd_compression_parameters cparams,
\t\t\t\t\t  zstd_custom_mem custom_mem)
{
\treturn ZSTD_createCDict_advanced(dict, dict_size, ZSTD_dlm_byRef,
\t\t\t\t\t ZSTD_dct_auto, cparams, custom_mem);
}
EXPORT_SYMBOL(zstd_create_cdict_byreference);

size_t zstd_free_cdict(zstd_cdict *cdict)
{
\treturn ZSTD_freeCDict(cdict);
}
EXPORT_SYMBOL(zstd_free_cdict);
""")

    insert_after(compress_mod, "EXPORT_SYMBOL(zstd_compress_cctx);\n", """
size_t zstd_compress_using_cdict(zstd_cctx *cctx, void *dst,
\tsize_t dst_capacity, const void *src, size_t src_size,
\tconst ZSTD_CDict *cdict)
{
\treturn ZSTD_compress_usingCDict(cctx, dst, dst_capacity,
\t\t\t\t\tsrc, src_size, cdict);
}
EXPORT_SYMBOL(zstd_compress_using_cdict);
""")

    # ---- lib/zstd/zstd_decompress_module.c ----

    insert_after(decompress_mod, "EXPORT_SYMBOL(zstd_dctx_workspace_bound);\n", """
zstd_dctx *zstd_create_dctx_advanced(zstd_custom_mem custom_mem)
{
\treturn ZSTD_createDCtx_advanced(custom_mem);
}
EXPORT_SYMBOL(zstd_create_dctx_advanced);

size_t zstd_free_dctx(zstd_dctx *dctx)
{
\treturn ZSTD_freeDCtx(dctx);
}
EXPORT_SYMBOL(zstd_free_dctx);

zstd_ddict *zstd_create_ddict_byreference(const void *dict, size_t dict_size,
\t\t\t\t\t  zstd_custom_mem custom_mem)
{
\treturn ZSTD_createDDict_advanced(dict, dict_size, ZSTD_dlm_byRef,
\t\t\t\t\t ZSTD_dct_auto, custom_mem);

}
EXPORT_SYMBOL(zstd_create_ddict_byreference);

size_t zstd_free_ddict(zstd_ddict *ddict)
{
\treturn ZSTD_freeDDict(ddict);
}
EXPORT_SYMBOL(zstd_free_ddict);
""")

    insert_after(decompress_mod, "EXPORT_SYMBOL(zstd_decompress_dctx);\n", """
size_t zstd_decompress_using_ddict(zstd_dctx *dctx,
\tvoid *dst, size_t dst_capacity, const void* src, size_t src_size,
\tconst zstd_ddict* ddict)
{
\treturn ZSTD_decompress_usingDDict(dctx, dst, dst_capacity, src,
\t\t\t\t\t  src_size, ddict);
}
EXPORT_SYMBOL(zstd_decompress_using_ddict);
""")

    print("  restored zstd_custom_mem/zstd_cdict/zstd_ddict advanced-dictionary API")


if __name__ == "__main__":
    main()
