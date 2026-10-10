#include "City/Mobility/CityMobilityData.h"
#include "City/CityWorldBounds.h"

FCityTransportRoute CityMobility::MakeNearbyRoute(const ECityTransportKind Kind, const FVector& PlayerLocation)
{
    const FCityTransportRoute Base = MakeRoute(Kind);
    if (Base.bWater || Base.bRail)
    {
        return Base;
    }
    // Cac vong duong co dinh theo quan; chi xe gan nguoi choi moi duoc spawn.
    const FVector Anchors[] = {
        FVector::ZeroVector,
        FVector(-216000, -216000, 0),
        FVector(-216000, 0, 0),
        FVector(-216000, 216000, 0),
        FVector(0, -216000, 0),
        FVector(0, 216000, 0),
        FVector(216000, 0, 0),
        FVector(216000, 288000, 0)
    };
    FCityTransportRoute Best = Base;
    double BestDistance = TNumericLimits<double>::Max();
    for (const FVector& Anchor : Anchors)
    {
        FCityTransportRoute Candidate = Base;
        bool bSafe = true;
        for (FVector& Point : Candidate.Points)
        {
            Point += Anchor;
            bSafe &= FMath::Abs(Point.X) < CityWorldBounds::RoadExtent
                && FMath::Abs(Point.Y) < CityWorldBounds::RoadExtent
                && !CityWorldBounds::IsStreetCutout(Point.X, Point.Y);
        }
        for (int32 Index = 0; Index < Candidate.Points.Num(); ++Index)
        {
            const FVector Middle = (Candidate.Points[Index]
                + Candidate.Points[(Index + 1) % Candidate.Points.Num()]) * .5;
            bSafe &= !CityWorldBounds::IsStreetCutout(Middle.X, Middle.Y);
        }
        if (!bSafe)
        {
            continue;
        }
        for (const int32 Stop : Candidate.Stops)
        {
            const double Distance = FVector::DistSquared2D(PlayerLocation, Candidate.Points[Stop]);
            if (Distance >= BestDistance)
            {
                continue;
            }
            BestDistance = Distance;
            if (!Anchor.IsZero())
            {
                Candidate.Id = FName(*FString::Printf(TEXT("%s_Road_%.0f_%.0f"),
                    MeshName(Kind), Anchor.X, Anchor.Y));
            }
            Best = Candidate;
        }
    }
    return Best;
}
