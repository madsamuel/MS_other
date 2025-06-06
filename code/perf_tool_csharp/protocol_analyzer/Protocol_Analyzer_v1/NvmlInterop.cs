using System;
using System.Runtime.InteropServices;

public static class NvmlInterop
{
    public const int NVML_SUCCESS = 0;

    [DllImport("nvml.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern int nvmlInit_v2();

    [DllImport("nvml.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern int nvmlShutdown();

    [DllImport("nvml.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern int nvmlDeviceGetHandleByIndex(uint index, out IntPtr device);

    [DllImport("nvml.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern int nvmlDeviceGetUtilizationRates(IntPtr device, out NvmlUtilization utilization);

    [DllImport("nvml.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern int nvmlDeviceGetMemoryInfo(IntPtr device, out NvmlMemory memory);

    [DllImport("nvml.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern int nvmlDeviceGetEncoderUtilization(IntPtr device, out uint utilization, out uint samplingPeriod);

    [DllImport("nvml.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern int nvmlDeviceGetDecoderUtilization(IntPtr device, out uint utilization, out uint samplingPeriod);

    [StructLayout(LayoutKind.Sequential)]
    public struct NvmlUtilization
    {
        public uint gpu;
        public uint memory;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct NvmlMemory
    {
        public ulong total;
        public ulong free;
        public ulong used;
    }
}
