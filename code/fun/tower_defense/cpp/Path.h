#pragma once

#include <vector>
#include <cmath>

struct Vector2D {
    float x, y;
    
    Vector2D(float px = 0, float py = 0) : x(px), y(py) {}
    
    float distance(const Vector2D& other) const {
        float dx = x - other.x;
        float dy = y - other.y;
        return std::sqrt(dx * dx + dy * dy);
    }
};

class Path {
public:
    std::vector<Vector2D> points;
    
    Path() {
        // Initialize path points (15 points forming a winding maze)
        points.push_back(Vector2D(-50, 120));
        points.push_back(Vector2D(820, 120));
        points.push_back(Vector2D(820, 230));
        points.push_back(Vector2D(75, 230));
        points.push_back(Vector2D(75, 310));
        points.push_back(Vector2D(820, 310));
        points.push_back(Vector2D(820, 390));
        points.push_back(Vector2D(150, 390));
        points.push_back(Vector2D(150, 480));
        points.push_back(Vector2D(820, 480));
        points.push_back(Vector2D(820, 560));
        points.push_back(Vector2D(75, 560));
        points.push_back(Vector2D(75, 680));
        points.push_back(Vector2D(950, 680));
        points.push_back(Vector2D(950, 850));
    }
    
    float getDistance(float x, float y, float tolerance = 0) const {
        float minDist = 999999.0f;
        
        for (size_t i = 0; i < points.size() - 1; i++) {
            // Distance from point to line segment
            float px = points[i].x;
            float py = points[i].y;
            float nx = points[i + 1].x;
            float ny = points[i + 1].y;
            
            float dx = nx - px;
            float dy = ny - py;
            float len2 = dx * dx + dy * dy;
            
            if (len2 == 0) {
                float dist = std::sqrt((x - px) * (x - px) + (y - py) * (y - py));
                if (dist < minDist) minDist = dist;
            } else {
                float t = std::max(0.0f, std::min(1.0f, ((x - px) * dx + (y - py) * dy) / len2));
                float closestX = px + t * dx;
                float closestY = py + t * dy;
                float dist = std::sqrt((x - closestX) * (x - closestX) + (y - closestY) * (y - closestY));
                if (dist < minDist) minDist = dist;
            }
        }
        
        return minDist;
    }
    
    bool isOnPath(float x, float y, float tolerance = 60.0f) const {
        return getDistance(x, y) < tolerance;
    }
};
