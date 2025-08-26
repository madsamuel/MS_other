#include "automation.h"
#include <iostream>
#include <string>
#include <cstdlib>

int main(int argc, char** argv) {
    uint32_t initial_ms = 2000;
    uint32_t open_ms = 10000;

    if (argc >= 2) initial_ms = static_cast<uint32_t>(std::stoul(argv[1]));
    if (argc >= 3) open_ms = static_cast<uint32_t>(std::stoul(argv[2]));

    std::cout << "UI Start menu automation\n";
    std::cout << "Initial wait (ms) [cmd arg1 or default]: " << initial_ms << "\n";
    std::cout << "Open duration (ms) [cmd arg2 or default]: " << open_ms << "\n";
    std::cout << "Press Enter to start...";
    std::cin.get();

    UIAutomation autom(initial_ms, open_ms);
    autom.run();
    std::cout << "Done.\n";
    return 0;
}
