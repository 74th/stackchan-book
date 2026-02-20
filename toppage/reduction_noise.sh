#!/bin/bash
set -xe
~/tools/realesrgan-ncnn-vulkan-20220424-macos/realesrgan-ncnn-vulkan\
    -i bird_and_ic_illustration-org.png\
    -o bird_and_ic_illustration-nonnoise.png\
    -n realesrgan-x4plus-anime\
    -m ~/tools/realesrgan-ncnn-vulkan-20220424-macos/models
    -s 2\
    -g 0\
    -f png\
    --denoise_strength 0.3