#pragma once
#include <vector>
#include <SFML/System.hpp>

class Path {
public:
    std::vector<sf::Vector2f> points;
    
    Path() {
        // Initialize path with all waypoints
        points = {
            {-50, 120},
            {820, 120},
            {820, 230},
            {75, 230},
            {75, 310},
            {820, 310},
            {820, 390},
            {150, 390},
            {150, 480},
            {820, 480},
            {820, 560},
            {75, 560},
            {75, 680},
            {950, 680},
            {950, 850}
        };
    }
    
    float getDistance(float x, float y, float tolerance = 60.0f) const {
        float minDist = tolerance;
        for (const auto& point : points) {
            float dx = x - point.x;
            float dy = y - point.y;
            float dist = std::sqrt(dx * dx + dy * dy);
            if (dist < minDist) minDist = dist;
        }
        return minDist;
    }
    
    bool isOnPath(float x, float y, float tolerance = 60.0f) const {
        return getDistance(x, y) < tolerance;
    }
};
