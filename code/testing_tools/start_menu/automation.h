#pragma once
#include <cstdint>

class UIAutomation {
public:
    UIAutomation(uint32_t initial_ms = 2000, uint32_t open_ms = 10000);
    virtual ~UIAutomation();

    // Run the full sequence: wait initial, open, wait open duration, close
    void run();

    // Hooks that can be overridden for unit tests
    virtual void sleep_ms(uint32_t ms);
    virtual void sendWinKey();

    uint32_t initial_ms() const { return initial_ms_; }
    uint32_t open_ms() const { return open_ms_; }

private:
    uint32_t initial_ms_;
    uint32_t open_ms_;
};
