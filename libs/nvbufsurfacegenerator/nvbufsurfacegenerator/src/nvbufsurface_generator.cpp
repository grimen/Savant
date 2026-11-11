#include "nvbufsurface_generator.h"

#include <gst/gst.h>
#include <stdexcept>
#include "gstnvdsbufferpool.h"
#include "nvbufsurface.h"


NvBufSurfaceGenerator::NvBufSurfaceGenerator(
    GstCaps *caps,
    uint32_t gpu_id,
    uint32_t mem_type
) {
    GST_DEBUG("Creating NvBufSurfaceGenerator");
    GstStructure *config;

    buffer_pool = gst_nvds_buffer_pool_new();
    GST_DEBUG("Buffer pool %p created", buffer_pool);

    config = gst_buffer_pool_get_config(buffer_pool);
    gst_buffer_pool_config_set_params(
        config, caps, sizeof(NvBufSurface), 4, 4 + 4);
    gst_structure_set(
        config,
        "memtype", G_TYPE_UINT, mem_type,
        "gpu-id", G_TYPE_UINT, gpu_id,
        "batch-size", G_TYPE_UINT, 1,
        NULL);

    if (!gst_buffer_pool_set_config(buffer_pool, config)) {
        GST_ERROR("Failed to configure buffer pool %p", buffer_pool);
        throw std::runtime_error("Failed to configure buffer pool");
    }
    GST_DEBUG("Buffer pool %p configured", buffer_pool);

    gst_buffer_pool_set_active(buffer_pool, TRUE);

    GST_DEBUG("NvBufSurfaceGenerator created");
}


NvBufSurfaceGenerator::~NvBufSurfaceGenerator() {
    GST_DEBUG("Destroying NvBufSurfaceGenerator");
    gst_object_unref(buffer_pool);
    GST_DEBUG("Buffer pool %p destroyed", buffer_pool);
}


void NvBufSurfaceGenerator::create_surface(GstBuffer *buffer_dest) {
    GST_DEBUG("Creating NvBufSurface at buffer %p", buffer_dest);
    GstBuffer *buffer;
    GstFlowReturn result;

    GST_DEBUG("Acquiring buffer from pool %p", buffer_pool);
    result = gst_buffer_pool_acquire_buffer(
        buffer_pool, &buffer, nullptr);

    if (result != GST_FLOW_OK) {
        GST_ERROR(
            "Failed to acquire buffer from pool %p: %d",
            buffer_pool, result);
        throw std::runtime_error("Failed to acquire buffer from pool");
    }

    // mainstream patch #911: allocate independent storage for resized output.
    GstMapInfo map;
    if (!gst_buffer_map(buffer, &map, GST_MAP_READ)) {
        gst_buffer_unref(buffer);
        gst_buffer_pool_release_buffer(buffer_pool, buffer);
        throw std::runtime_error("Failed to map pooled surface");
    }
    auto *source = reinterpret_cast<NvBufSurface *>(map.data);
    NvBufSurfaceCreateParams create_params = {};
    create_params.gpuId = source->gpuId;
    create_params.memType = source->memType;
    create_params.layout = source->surfaceList[0].layout;
    create_params.colorFormat = source->surfaceList[0].colorFormat;
    create_params.width = source->surfaceList[0].width;
    create_params.height = source->surfaceList[0].height;
    uint32_t batch_size = source->batchSize;
    gst_buffer_unmap(buffer, &map);
    gst_buffer_unref(buffer);
    gst_buffer_pool_release_buffer(buffer_pool, buffer);

    NvBufSurface *surface = nullptr;
    if (NvBufSurfaceCreate(&surface, batch_size, &create_params) != 0) {
        throw std::runtime_error("Failed to allocate independent surface");
    }
    gst_buffer_remove_all_memory(buffer_dest);
    GstMemory *memory = gst_memory_new_wrapped(
        static_cast<GstMemoryFlags>(0), surface, sizeof(NvBufSurface), 0, sizeof(NvBufSurface), surface,
        reinterpret_cast<GDestroyNotify>(NvBufSurfaceDestroy));
    gst_buffer_append_memory(buffer_dest, memory);
    GST_DEBUG("Buffer %p copied into buffer %p", buffer, buffer_dest);
}
