# Troubleshooting

## Kernel died when initializing the Transformers Extension

### Problem

Running the Transformers Extension Initialization in the transformers/te_init.ipynb notebook results
in a pop-up error message similar to this: "Kernel Restarting. The kernel for transformers/te_init.ipynb
appears to have died. It will restart automatically."

### Cause

The issue is caused by an insufficient memory, either RAM or the free disk space. This, for example,
can be observed when running the AI Lab from certain restricted EC2 instances, e.g.T2.medium.

### Solution

Make sure the available resources satisfy the minimum [system requirements](system-requirements.md).
