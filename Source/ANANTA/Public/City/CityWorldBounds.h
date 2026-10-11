#pragma once

namespace CityWorldBounds
{
    // Dong bo voi CityExpansionData.py; luu duoc ca dai via he ngoai cung.
    constexpr float RoadExtent = 336000.f;
    constexpr float SaveExtent = 340000.f;
    constexpr float RoadSpacing = 12000.f;

    inline bool IsCoastalCutout(const float X, const float Y)
    {
        return X >= 120000.f && Y <= -120000.f;
    }

    inline bool IsStreetCutout(const float X, const float Y)
    {
        const bool bAirport = X > 180000.f && X < 276000.f && Y > 180000.f && Y < 228000.f;
        return IsCoastalCutout(X, Y) || bAirport;
    }
}
