#include "automation.h"
#include <iostream>
#include <cassert>

struct FakeAutomation : public UIAutomation {
    int sleep_calls = 0;
    int winkey_calls = 0;
    FakeAutomation(uint32_t a, uint32_t b) : UIAutomation(a,b) {}
    void sleep_ms(uint32_t ms) override { sleep_calls++; }
    void sendWinKey() override { winkey_calls++; }
};

int main() {
    FakeAutomation f(10, 20);
    f.run();
    // expected: sleep called twice (initial and open duration), win key called twice (open and close)
    assert(f.sleep_calls == 2);
    assert(f.winkey_calls == 2);
    std::cout << "All tests passed.\n";
    return 0;
}
