#include "automation.h"
#include <windows.h>
#include <iostream>

UIAutomation::UIAutomation(uint32_t initial_ms, uint32_t open_ms)
    : initial_ms_(initial_ms), open_ms_(open_ms) {}

UIAutomation::~UIAutomation() {}

void UIAutomation::sleep_ms(uint32_t ms) {
    Sleep(ms);
}

void UIAutomation::sendWinKey() {
    // Send left Windows key down and up to toggle Start menu
    INPUT input = {0};
    input.type = INPUT_KEYBOARD;
    input.ki.wVk = VK_LWIN;
    SendInput(1, &input, sizeof(INPUT));
    // key up
    input.ki.dwFlags = KEYEVENTF_KEYUP;
    SendInput(1, &input, sizeof(INPUT));
}

void UIAutomation::run() {
    std::cout << "Initial wait: " << initial_ms_ << " ms\n";
    sleep_ms(initial_ms_);
    std::cout << "Opening Start menu...\n";
    sendWinKey();
    std::cout << "Open for: " << open_ms_ << " ms\n";
    sleep_ms(open_ms_);
    std::cout << "Closing Start menu...\n";
    sendWinKey();
}
