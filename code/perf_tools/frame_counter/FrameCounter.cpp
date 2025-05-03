// FrameCounter.cpp
#include <windows.h>
#include <dxgi1_4.h>
#include <d3d12.h>
#include <iostream>

int main() {
    // Initialize DX12 + create device + swap chain (omitted for brevity)
    // After swapChain->Present(), get frame count
    DXGI_FRAME_STATISTICS stats;
    if (SUCCEEDED(swapChain->GetFrameStatistics(&stats))) {
        std::cout << "Present Count: " << stats.PresentCount << std::endl;
    } else {
        std::cerr << "Failed to get frame statistics." << std::endl;
    }

    return 0;
}
